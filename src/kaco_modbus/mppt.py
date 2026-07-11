"""SunSpec Model 160 — per-MPPT-string (module) monitoring.

Model 160 has a fixed block (holding the scale factors and the advertised
module count) followed by a repeating block of per-module data. The scale
factors and the scaled values live in different sub-blocks, so — per the
constraint documented in ``inverter.py`` — ``scale_register=`` cannot be used
(it is never shifted by ``base_offset``, and here the scaled fields are
additionally in a *different* component than their scale factors). Instead
each module keeps a reference to the shared ``MpptFixed`` fixed block and
combines raw value + scale factor via the existing ``_apply_sf`` helper, the
same pattern ``Inverter`` uses for its own scaled points.

Addresses below are relative to the model's ID register (offset 0 = ID).
``MpptModule``'s field addresses are those of module 0 (i.e. already include
the fixed block's 10-register width); instance *m* is built with
``base_offset = block.address + m * MODULE_LENGTH``, which lands field
addresses at ``block.address + 10 + m * MODULE_LENGTH`` — exactly module m's
data, since ``Component._address`` adds ``base_offset`` on top of the
field's own (module-0) address.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from modbus_connection.model import Component
from modbus_connection.model.sunspec import (
    acc32,
    bitfield32,
    enum16,
    int16,
    string,
    sunssf,
    uint16,
)

from .enums import InverterEvent, OperatingState
from .inverter import _apply_sf

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit

MODEL_ID = 160
FIXED_BLOCK_LENGTH = 8  # data registers before the repeating modules
MODULE_LENGTH = 20


def module_count(block_length: int) -> int:
    """Number of MPPT modules advertised by a model-160 block header."""
    return max(0, (block_length - FIXED_BLOCK_LENGTH) // MODULE_LENGTH)


class MpptFixed(Component):
    """Model 160 fixed block: scale factors and the advertised module count."""

    _dca_sf = sunssf(2)
    _dcv_sf = sunssf(3)
    _dcw_sf = sunssf(4)
    _dcwh_sf = sunssf(5)
    events = bitfield32(6, InverterEvent)
    advertised_count = uint16(8)


class MpptModule(Component):
    """One MPPT string/module's live data; addresses at module-0 offsets.

    Scaled points are decoded manually via ``_apply_sf`` against the shared
    ``MpptFixed`` sibling component's scale factors — see the module
    docstring above and ``inverter.py`` for why ``scale_register=`` cannot
    be used here.
    """

    input_id = uint16(10)
    name = string(11, 8)
    _dc_current_raw = uint16(19, unit="A")
    _dc_voltage_raw = uint16(20, unit="V")
    _dc_power_raw = uint16(21, unit="W")
    _dc_energy_raw = acc32(22, unit="Wh")
    temperature = int16(26, unit="°C")
    state = enum16(27, OperatingState)
    events = bitfield32(28, InverterEvent)

    def __init__(self, unit: ModbusUnit, fixed: MpptFixed, *, base_offset: int) -> None:
        self._fixed = fixed
        super().__init__(unit, base_offset=base_offset)

    @property
    def dc_current(self) -> float | None:
        return _apply_sf(self._dc_current_raw, self._fixed._dca_sf)

    @property
    def dc_voltage(self) -> float | None:
        return _apply_sf(self._dc_voltage_raw, self._fixed._dcv_sf)

    @property
    def dc_power(self) -> float | None:
        return _apply_sf(self._dc_power_raw, self._fixed._dcw_sf)

    @property
    def dc_energy(self) -> float | None:
        return _apply_sf(self._dc_energy_raw, self._fixed._dcwh_sf)
