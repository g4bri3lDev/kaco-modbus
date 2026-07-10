"""SunSpec discovery tests against the mock backend."""

import pytest

from kaco_modbus.discovery import ModelBlock, find_sunspec_base, walk_model_chain
from kaco_modbus.exceptions import SunSpecNotFoundError

from .conftest import seed_device


async def test_finds_base_at_40000(mock_modbus_unit):
    seed_device(mock_modbus_unit)
    assert await find_sunspec_base(mock_modbus_unit) == 40000


async def test_no_marker_raises(mock_modbus_unit):
    mock_modbus_unit.holding[40000] = [0, 0]
    mock_modbus_unit.holding[0] = [0, 0]
    mock_modbus_unit.holding[50000] = [0, 0]
    with pytest.raises(SunSpecNotFoundError):
        await find_sunspec_base(mock_modbus_unit)


async def test_walk_model_chain(mock_modbus_unit):
    seed_device(mock_modbus_unit)
    blocks = await walk_model_chain(mock_modbus_unit, 40000)
    assert blocks == (
        ModelBlock(model_id=1, address=40002, length=66),
        ModelBlock(model_id=103, address=40070, length=50),
    )


async def test_unterminated_chain_raises(mock_modbus_unit):
    mock_modbus_unit.holding[40000] = [0x5375, 0x6E53]
    for address in range(40002, 41000):  # headers never reach 0xFFFF
        mock_modbus_unit.holding[address] = 1
    with pytest.raises(SunSpecNotFoundError):
        await walk_model_chain(mock_modbus_unit, 40000)
