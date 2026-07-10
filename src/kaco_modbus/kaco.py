"""Top-level entrypoint: one object for one KACO inverter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from modbus_connection.model import ComponentGroup

from . import common as common_model
from . import inverter as inverter_model
from .common import Common
from .discovery import ModelBlock, find_sunspec_base, walk_model_chain
from .exceptions import SunSpecModelMissingError
from .inverter import Inverter

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit


@dataclass(frozen=True)
class KacoProbe:
    """Identity and layout read once during setup."""

    manufacturer: str | None
    model: str | None
    options: str | None
    firmware: str | None
    serial: str | None
    base_address: int
    blocks: tuple[ModelBlock, ...]

    def block_for(self, *model_ids: int) -> ModelBlock | None:
        for block in self.blocks:
            if block.model_id in model_ids:
                return block
        return None


class KacoInverter:
    """A KACO blueplanet inverter speaking SunSpec Modbus."""

    def __init__(self, unit: ModbusUnit, probe: KacoProbe) -> None:
        self._unit = unit
        self.probe = probe

        common_block = probe.block_for(common_model.MODEL_ID)
        inverter_block = probe.block_for(*inverter_model.MODEL_IDS)
        if common_block is None:
            raise SunSpecModelMissingError("device chain has no common model (1)")
        if inverter_block is None:
            raise SunSpecModelMissingError(
                "device chain has no inverter model (101/102/103)"
            )

        self.common = Common(unit, base_offset=common_block.address)
        self.inverter = Inverter(unit, base_offset=inverter_block.address)
        self._group = ComponentGroup(unit, [self.common, self.inverter])

    @classmethod
    async def async_probe(cls, unit: ModbusUnit) -> KacoProbe:
        """Discover the SunSpec layout and read the identity block."""
        base = await find_sunspec_base(unit)
        blocks = await walk_model_chain(unit, base)

        common_block = next(
            (b for b in blocks if b.model_id == common_model.MODEL_ID), None
        )
        if common_block is None:
            raise SunSpecModelMissingError("device chain has no common model (1)")
        identity = Common(unit, base_offset=common_block.address)
        await identity.async_update()

        return KacoProbe(
            manufacturer=identity.manufacturer,
            model=identity.model,
            options=identity.options,
            firmware=identity.version,
            serial=identity.serial,
            base_address=base,
            blocks=blocks,
        )

    async def async_update(self) -> None:
        """Refresh identity and live data in pooled reads."""
        await self._group.async_update()
