from kaco_modbus.dump import dump_registers
from kaco_modbus.testing import BLUEPLANET_86TL3_REGISTERS

from .conftest import seed_device


async def test_dump_matches_seed(mock_modbus_unit):
    seed_device(mock_modbus_unit)
    image = await dump_registers(mock_modbus_unit)
    assert image == BLUEPLANET_86TL3_REGISTERS
