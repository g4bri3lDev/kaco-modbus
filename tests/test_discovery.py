"""Finding the SunSpec map, and deciding what this inverter has."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from modbus_connection import IllegalDataAddressError, ModbusTimeoutError

from kaco_modbus import KacoInverter, ModelMissingError, SunSpecNotFoundError
from kaco_modbus.const import SUNSPEC_BASE_ADDRESSES
from kaco_modbus.testing import BASE_ADDRESS, BLUEPLANET_86TL3, MODEL_CHAIN

if TYPE_CHECKING:
    from modbus_connection.mock import MockModbusUnit


async def test_discovers_the_real_device(inverter: KacoInverter) -> None:
    """The captured image identifies itself exactly as the hardware does."""
    assert inverter.base_address == BASE_ADDRESS
    assert inverter.info is not None
    assert inverter.info.manufacturer == "KACO new energy"
    assert inverter.info.model == "blueplanet 8.6 TL3 INT"
    assert inverter.info.serial_number == "8.6TL01736586"
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
    shifted = {
        address - BASE_ADDRESS: value for address, value in BLUEPLANET_86TL3.items()
    }
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
