import pytest

from kaco_modbus import KacoInverter, OperatingState, SunSpecModelMissingError

from .conftest import seed_device


async def test_probe(mock_modbus_unit):
    seed_device(mock_modbus_unit)
    probe = await KacoInverter.async_probe(mock_modbus_unit)
    assert probe.manufacturer == "KACO new energy"
    assert probe.serial == "8.6TL01723456"
    assert probe.base_address == 40000
    assert probe.block_for(101, 102, 103).model_id == 103


async def test_full_device(mock_modbus_unit):
    seed_device(mock_modbus_unit)
    probe = await KacoInverter.async_probe(mock_modbus_unit)
    device = KacoInverter(mock_modbus_unit, probe)
    await device.async_update()
    assert device.inverter.ac_power == 3280.0
    assert device.inverter.state is OperatingState.MPPT
    assert device.common.serial == "8.6TL01723456"


async def test_missing_inverter_model(mock_modbus_unit):
    mock_modbus_unit.holding[40000] = [0x5375, 0x6E53]
    mock_modbus_unit.holding[40002] = [1, 66]
    mock_modbus_unit.holding[40070] = [0xFFFF, 0]
    probe = await KacoInverter.async_probe(mock_modbus_unit)
    with pytest.raises(SunSpecModelMissingError):
        KacoInverter(mock_modbus_unit, probe)
