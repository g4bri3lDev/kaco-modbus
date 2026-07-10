"""SunSpec Model 101/102/103 inverter component tests."""

from kaco_modbus.enums import OperatingState
from kaco_modbus.inverter import Inverter

from .conftest import seed_device


async def test_inverter_values(mock_modbus_unit):
    seed_device(mock_modbus_unit)
    inv = Inverter(mock_modbus_unit, base_offset=40070)
    await inv.async_update()
    assert inv.ac_power == 3280.0
    assert inv.ac_current == 12.5
    assert inv.voltage_phase_a == 231.1
    assert inv.frequency == 49.99
    assert inv.energy_total == 8_883_000
    assert inv.dc_voltage == 650.2
    assert inv.temperature_cabinet == 41.2
    assert inv.state is OperatingState.MPPT


async def test_unimplemented_points_are_none(mock_modbus_unit):
    seed_device(mock_modbus_unit)
    inv = Inverter(mock_modbus_unit, base_offset=40070)
    await inv.async_update()
    assert inv.temperature_transformer is None  # 0x8000 sentinel
    assert inv.vendor_state is None  # 0xFFFF sentinel
