"""SunSpec Model 1 common component tests."""

from kaco_modbus.common import Common

from .conftest import seed_device


async def test_common_identity(mock_modbus_unit):
    seed_device(mock_modbus_unit)
    common = Common(mock_modbus_unit, base_offset=40002)
    await common.async_update()
    assert common.manufacturer == "KACO new energy"
    assert common.model == "blueplanet 8.6 TL3"
    assert common.version == "V1.23"
    assert common.serial == "8.6TL01723456"
