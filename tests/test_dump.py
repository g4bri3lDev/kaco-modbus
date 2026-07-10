import json

from kaco_modbus.dump import dump_registers
from kaco_modbus.testing import BLUEPLANET_86TL3_REGISTERS, registers_from_dump

from .conftest import seed_device


async def test_dump_matches_seed(mock_modbus_unit):
    seed_device(mock_modbus_unit)
    image = await dump_registers(mock_modbus_unit)
    assert image == BLUEPLANET_86TL3_REGISTERS


async def test_dump_round_trips_through_registers_from_dump(mock_modbus_unit, tmp_path):
    """The dump CLI's JSON shape must be loadable back via registers_from_dump."""
    seed_device(mock_modbus_unit)
    image = await dump_registers(mock_modbus_unit)

    dump_path = tmp_path / "dump.json"
    dump_path.write_text(
        json.dumps({"registers": {str(k): v for k, v in sorted(image.items())}})
    )

    assert registers_from_dump(dump_path) == BLUEPLANET_86TL3_REGISTERS
