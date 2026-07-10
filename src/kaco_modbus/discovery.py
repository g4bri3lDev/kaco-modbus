"""Locate the SunSpec register map and walk its model chain."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from modbus_connection import ModbusError

from .exceptions import SunSpecNotFoundError

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit

SUNSPEC_MARKER = (0x5375, 0x6E53)  # "SunS"
BASE_ADDRESSES = (40000, 0, 50000)
END_MODEL_ID = 0xFFFF
_MAX_MODELS = 64


@dataclass(frozen=True)
class ModelBlock:
    """One SunSpec model block: its id, absolute address, and data length."""

    model_id: int
    address: int  # absolute address of the model's ID register
    length: int  # data registers following the two-register header


async def find_sunspec_base(unit: ModbusUnit) -> int:
    """Return the base address holding the "SunS" marker."""
    for base in BASE_ADDRESSES:
        try:
            marker = await unit.read_holding_registers(base, 2)
        except ModbusError:
            continue  # unmapped address on this device; try the next base
        if tuple(marker) == SUNSPEC_MARKER:
            return base
    raise SunSpecNotFoundError(
        f"no SunSpec marker at any of {BASE_ADDRESSES}; "
        "is Modbus TCP / SunSpec enabled on the device?"
    )


async def walk_model_chain(unit: ModbusUnit, base: int) -> tuple[ModelBlock, ...]:
    """Read the chain of model headers starting after the marker."""
    blocks: list[ModelBlock] = []
    address = base + 2
    for _ in range(_MAX_MODELS):
        model_id, length = await unit.read_holding_registers(address, 2)
        if model_id == END_MODEL_ID:
            return tuple(blocks)
        blocks.append(ModelBlock(model_id=model_id, address=address, length=length))
        address += 2 + length
    raise SunSpecNotFoundError("SunSpec model chain did not terminate")
