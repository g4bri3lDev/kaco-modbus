"""Finding the SunSpec map, and deciding what this inverter has."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from modbus_connection import IllegalDataAddressError, ModbusTimeoutError

from kaco_modbus import (
    KacoInverter,
    ModelMissingError,
    NotAKacoInverterError,
    SunSpecNotFoundError,
)
from kaco_modbus.const import SUNSPEC_BASE_ADDRESSES
from kaco_modbus.models import Common
from kaco_modbus.testing import (
    BASE_ADDRESS,
    BLUEPLANET_86TL3,
    MODEL_CHAIN,
    with_manufacturer,
)

if TYPE_CHECKING:
    from modbus_connection.mock import MockModbusUnit


async def test_discovers_the_real_device(inverter: KacoInverter) -> None:
    """The captured image identifies itself exactly as the hardware does."""
    assert inverter.base_address == BASE_ADDRESS
    assert inverter.info is not None
    assert inverter.info.manufacturer == "KACO new energy"
    assert inverter.info.model == "blueplanet 8.6 TL3 INT"
    # Anonymised in the fixture: a real serial identifies someone's hardware,
    # and this library is published. See testing.py.
    assert inverter.info.serial_number == "8.6TL00000000"
    assert inverter.info.firmware == "V5.53"


async def test_discovers_the_whole_model_chain(inverter: KacoInverter) -> None:
    assert inverter.models is not None
    assert sorted(inverter.models) == sorted(MODEL_CHAIN)


async def test_ignores_the_float_inverter_model(inverter: KacoInverter) -> None:
    """This device advertises 113 (float) as well as 103 (integer + scale
    factor), carrying identical values. 103 is bound and 113 is ignored:
    polling both would cost 62 extra registers a cycle for nothing.
    """
    assert inverter.models is not None
    assert 113 in inverter.models, "the fixture should still advertise the float model"

    assert inverter.inverter is not None
    assert inverter.inverter.model_id == 103
    assert type(inverter.inverter).__name__ == "InverterThreePhase"


async def test_binds_the_optional_components(inverter: KacoInverter) -> None:
    assert inverter.mppt is not None
    assert inverter.status is not None
    assert inverter.nameplate is not None
    assert inverter.settings is not None
    assert inverter.controls is not None
    assert inverter.volt_var is not None


async def test_binds_curves_without_polling_them(inverter: KacoInverter) -> None:
    """Grid-code curves are available on demand, but cost nothing per poll."""
    assert sorted(inverter.curves) == ["hfrt", "hvrt", "lfrt", "lvrt", "volt_watt"]


async def test_probes_base_addresses_in_order(inverter_unit: MockModbusUnit) -> None:
    """A device whose map is not at 40000 is still found."""
    shifted = {address - BASE_ADDRESS: value for address, value in BLUEPLANET_86TL3.items()}
    inverter_unit.load_raw({"holding": shifted})
    # Reading 40000 must now fail the way a real device fails an unmapped read.
    for address in range(BASE_ADDRESS, BASE_ADDRESS + 2):
        inverter_unit.fail_read(address, IllegalDataAddressError())

    device = KacoInverter(inverter_unit)
    await device.async_update()

    assert device.base_address == 0
    assert SUNSPEC_BASE_ADDRESSES.index(0) > SUNSPEC_BASE_ADDRESSES.index(BASE_ADDRESS)


async def test_explicit_base_address_skips_probing(inverter_unit: MockModbusUnit) -> None:
    device = KacoInverter(inverter_unit, base_address=BASE_ADDRESS)
    await device.async_update()
    assert device.base_address == BASE_ADDRESS


async def test_no_marker_anywhere(mock_modbus_unit: MockModbusUnit) -> None:
    """A device that answers but is not SunSpec is reported as such."""
    mock_modbus_unit.load_raw({"holding": dict.fromkeys(range(40000, 40010), 0)})
    with pytest.raises(SunSpecNotFoundError, match="no SunSpec marker"):
        await KacoInverter(mock_modbus_unit).async_update()


async def test_transport_failure_is_not_mistaken_for_absence(
    mock_modbus_unit: MockModbusUnit,
) -> None:
    """A dead link must not look like 'this is not a SunSpec device'."""
    mock_modbus_unit.fail_requests(ModbusTimeoutError("no answer"))
    with pytest.raises(ModbusTimeoutError):
        await KacoInverter(mock_modbus_unit).async_update()


def test_with_manufacturer_rewrites_only_the_manufacturer() -> None:
    """The helper the guard's tests are built from must be surgical.

    Asserted on the registers rather than through a device, so it keeps
    working for names the guard rejects.
    """
    # Model 1 starts two registers past the marker; Mn is its first field and
    # spans 16 registers. Stated absolutely, the way this file already pins
    # model 1's length in test_device_without_an_inverter_model.
    mn = range(BASE_ADDRESS + 2 + 2, BASE_ADDRESS + 2 + 2 + 16)

    image = with_manufacturer(BLUEPLANET_86TL3, "Fronius")

    assert Common.mn.decode([image[a] for a in mn]) == "Fronius"
    assert image.keys() == BLUEPLANET_86TL3.keys(), "no registers added or removed"
    changed = {a for a in image if image[a] != BLUEPLANET_86TL3[a]}
    assert changed <= set(mn), f"registers outside Mn changed: {sorted(changed - set(mn))}"
    assert BLUEPLANET_86TL3[mn[0]] == 0x4B41, "the original image is not mutated"


def test_with_manufacturer_needs_a_model_1_to_rewrite() -> None:
    """Misuse fails loudly rather than silently writing over another model."""
    marker_only = {BASE_ADDRESS: 0x5375, BASE_ADDRESS + 1: 0x6E53, BASE_ADDRESS + 2: 0xFFFF}

    with pytest.raises(KeyError, match="model 1 is not in this image"):
        with_manufacturer(marker_only, "KACO new energy")


@pytest.mark.parametrize(
    ("manufacturer", "description"),
    [
        ("Fronius", "another vendor's SunSpec inverter"),
        ("", "a device that reports no manufacturer at all"),
        ("   ", "a manufacturer of nothing but whitespace"),
        ("kaco new energy", "a case SunSpec's registered value never uses"),
        (" KACO new energy", "a leading space no captured firmware produces"),
        ("NOTKACO", "a brand that merely contains the letters"),
    ],
)
async def test_a_device_that_is_not_a_kaco_is_rejected(
    mock_modbus_unit: MockModbusUnit, manufacturer: str, description: str
) -> None:
    """SunSpec is a shared dialect, so answering it proves nothing.

    A Fronius, SolarEdge or SMA exposes the same models at the same addresses
    and would otherwise set up as a KACO. Model 1's ``Mn`` is the only thing
    that says whose inverter this is, and a blank one is not evidence of
    anything.
    """
    image = with_manufacturer(BLUEPLANET_86TL3, manufacturer)
    mock_modbus_unit.load_raw({"holding": image})

    with pytest.raises(NotAKacoInverterError) as caught:
        await KacoInverter(mock_modbus_unit).async_update()

    # The message has to name what the device actually said, or a
    # misidentified unit cannot be diagnosed from a log.
    assert repr(manufacturer) in str(caught.value), description


@pytest.mark.parametrize(
    ("manufacturer", "description"),
    [
        ("KACO new energy", "exactly what the captured 8.6 TL3 reports"),
        ("KACO new energy GmbH", "a firmware that spells out the legal entity"),
        ("KACO", "a firmware that reports the bare brand"),
    ],
)
async def test_a_kaco_under_any_spelling_is_accepted(
    mock_modbus_unit: MockModbusUnit, manufacturer: str, description: str
) -> None:
    """Matched as a prefix, because only one firmware has ever been captured.

    The tolerance runs one way on purpose. Locking a real KACO out of its own
    inverter is a failure its owner cannot do anything about; letting a
    suspicious string through is the failure this guard exists to prevent. So
    an unseen model that appends to the brand is accepted, and anything that
    alters it — case, leading whitespace — is not.
    """
    image = with_manufacturer(BLUEPLANET_86TL3, manufacturer)
    mock_modbus_unit.load_raw({"holding": image})

    device = KacoInverter(mock_modbus_unit)
    await device.async_update()

    assert device.info is not None, description
    # Reported as the device worded it, not normalised to a canonical name.
    assert device.info.manufacturer == manufacturer


async def test_device_without_an_inverter_model(mock_modbus_unit: MockModbusUnit) -> None:
    """A SunSpec device that is not an inverter is rejected clearly."""
    common_only = {
        address: value
        for address, value in BLUEPLANET_86TL3.items()
        if address < BASE_ADDRESS + 2 + 2 + 66
    }
    # Terminate the chain right after model 1.
    end = BASE_ADDRESS + 2 + 2 + 66
    common_only[end] = 0xFFFF
    common_only[end + 1] = 0
    mock_modbus_unit.load_raw({"holding": common_only})

    with pytest.raises(ModelMissingError, match="no SunSpec inverter model"):
        await KacoInverter(mock_modbus_unit).async_update()
