"""SunSpec Model 160 (per-MPPT-string monitoring)."""

from pathlib import Path

from kaco_modbus import KacoInverter
from kaco_modbus.mppt import module_count
from kaco_modbus.testing import registers_from_dump

from .conftest import seed_device

REFERENCE = Path(__file__).parent / "reference" / "blueplanet_86tl3.json"


def test_module_count():
    assert module_count(48) == 2
    assert module_count(8) == 0
    assert module_count(0) == 0


async def test_mppt_modules_constructed_from_real_dump(mock_modbus_unit):
    for address, value in registers_from_dump(REFERENCE).items():
        mock_modbus_unit.holding[address] = value

    probe = await KacoInverter.async_probe(mock_modbus_unit)
    device = KacoInverter(mock_modbus_unit, probe)
    await device.async_update()

    assert len(device.mppt_modules) == 2
    assert device.mppt is not None
    assert device.mppt.advertised_count == 2


async def test_mppt_module_values_are_plausible_and_agree_with_inverter(
    mock_modbus_unit,
):
    for address, value in registers_from_dump(REFERENCE).items():
        mock_modbus_unit.holding[address] = value

    probe = await KacoInverter.async_probe(mock_modbus_unit)
    device = KacoInverter(mock_modbus_unit, probe)
    await device.async_update()

    modules = device.mppt_modules
    assert len(modules) == 2

    for module in modules:
        assert module.dc_power is not None and 0 <= module.dc_power <= 8_500
        assert module.dc_voltage is not None and 0 <= module.dc_voltage <= 1_000
        assert module.dc_current is not None and 0 <= module.dc_current <= 20

    total = sum(m.dc_power for m in modules)
    inverter_dc_power = device.inverter.dc_power
    assert inverter_dc_power is not None
    assert abs(total - inverter_dc_power) <= 0.05 * inverter_dc_power


async def test_synthetic_fixture_has_no_mppt(mock_modbus_unit):
    seed_device(mock_modbus_unit)
    probe = await KacoInverter.async_probe(mock_modbus_unit)
    device = KacoInverter(mock_modbus_unit, probe)
    await device.async_update()

    assert device.mppt is None
    assert device.mppt_modules == ()
