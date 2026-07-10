"""SunSpec inverter model (101 single / 102 split / 103 three-phase).

Scaled points are decoded manually via ``_apply_sf`` rather than the
``scale_register=`` kwarg on the field factories: ``modbus_connection``'s
``Component.register_items`` resolves ``scale_register`` as an **absolute**
address that is never shifted by ``base_offset`` (see
``modbus_connection.model.component.Component`` docstring — "scale_register
addresses are not shifted by base_offset"). That is correct for a component
whose scale factors live in one fixed shared location while ``base_offset``
walks repeated instances of the *value* fields, but SunSpec model blocks are
discovered at a runtime-variable address, and the scale-factor register lives
*inside* that same relocatable block. Using ``scale_register=`` here would
therefore read the wrong (unshifted, near-zero) address once a real
``base_offset`` is applied. Reading the raw value and the ``sunssf`` exponent
as ordinary fields (both correctly shifted by ``base_offset``) and combining
them in a property sidesteps that.
"""

from modbus_connection.model import Component
from modbus_connection.model.sunspec import (
    acc32,
    bitfield32,
    enum16,
    int16,
    sunssf,
    uint16,
)

from .enums import InverterEvent, OperatingState

MODEL_IDS = (101, 102, 103)


def _apply_sf(raw: int | float | None, sf: int | None) -> float | None:
    """Apply a SunSpec scale-factor exponent: ``raw * 10**sf``, sensibly rounded."""
    if raw is None or sf is None:
        return None
    if sf == 0:
        return float(raw)
    decimals = max(0, -sf)
    return float(round(raw * (10**sf), decimals))


class Inverter(Component):
    """Live inverter data; addresses relative to the model's ID register.

    On single-phase units (model 101) the phase B/C points decode to None.
    """

    _ac_current_raw = uint16(2, unit="A")
    _current_phase_a_raw = uint16(3, unit="A")
    _current_phase_b_raw = uint16(4, unit="A")
    _current_phase_c_raw = uint16(5, unit="A")
    _current_sf = sunssf(6)
    _voltage_ab_raw = uint16(7, unit="V")
    _voltage_bc_raw = uint16(8, unit="V")
    _voltage_ca_raw = uint16(9, unit="V")
    _voltage_phase_a_raw = uint16(10, unit="V")
    _voltage_phase_b_raw = uint16(11, unit="V")
    _voltage_phase_c_raw = uint16(12, unit="V")
    _voltage_sf = sunssf(13)
    _ac_power_raw = int16(14, unit="W")
    _ac_power_sf = sunssf(15)
    _frequency_raw = uint16(16, unit="Hz")
    _frequency_sf = sunssf(17)
    _apparent_power_raw = int16(18, unit="VA")
    _apparent_power_sf = sunssf(19)
    _reactive_power_raw = int16(20, unit="var")
    _reactive_power_sf = sunssf(21)
    _power_factor_raw = int16(22, unit="%")
    _power_factor_sf = sunssf(23)
    _energy_raw = acc32(24, unit="Wh")  # WH; SunSpec accumulators scale via WH_SF
    _energy_sf = sunssf(26)
    _dc_current_raw = uint16(27, unit="A")
    _dc_current_sf = sunssf(28)
    _dc_voltage_raw = uint16(29, unit="V")
    _dc_voltage_sf = sunssf(30)
    _dc_power_raw = int16(31, unit="W")
    _dc_power_sf = sunssf(32)
    _temperature_cabinet_raw = int16(33, unit="°C")
    _temperature_heatsink_raw = int16(34, unit="°C")
    _temperature_transformer_raw = int16(35, unit="°C")
    _temperature_other_raw = int16(36, unit="°C")
    _temperature_sf = sunssf(37)
    state = enum16(38, OperatingState)
    vendor_state = enum16(39)
    events = bitfield32(40, InverterEvent)

    @property
    def ac_current(self) -> float | None:
        return _apply_sf(self._ac_current_raw, self._current_sf)

    @property
    def current_phase_a(self) -> float | None:
        return _apply_sf(self._current_phase_a_raw, self._current_sf)

    @property
    def current_phase_b(self) -> float | None:
        return _apply_sf(self._current_phase_b_raw, self._current_sf)

    @property
    def current_phase_c(self) -> float | None:
        return _apply_sf(self._current_phase_c_raw, self._current_sf)

    @property
    def voltage_ab(self) -> float | None:
        return _apply_sf(self._voltage_ab_raw, self._voltage_sf)

    @property
    def voltage_bc(self) -> float | None:
        return _apply_sf(self._voltage_bc_raw, self._voltage_sf)

    @property
    def voltage_ca(self) -> float | None:
        return _apply_sf(self._voltage_ca_raw, self._voltage_sf)

    @property
    def voltage_phase_a(self) -> float | None:
        return _apply_sf(self._voltage_phase_a_raw, self._voltage_sf)

    @property
    def voltage_phase_b(self) -> float | None:
        return _apply_sf(self._voltage_phase_b_raw, self._voltage_sf)

    @property
    def voltage_phase_c(self) -> float | None:
        return _apply_sf(self._voltage_phase_c_raw, self._voltage_sf)

    @property
    def ac_power(self) -> float | None:
        return _apply_sf(self._ac_power_raw, self._ac_power_sf)

    @property
    def frequency(self) -> float | None:
        return _apply_sf(self._frequency_raw, self._frequency_sf)

    @property
    def apparent_power(self) -> float | None:
        return _apply_sf(self._apparent_power_raw, self._apparent_power_sf)

    @property
    def reactive_power(self) -> float | None:
        return _apply_sf(self._reactive_power_raw, self._reactive_power_sf)

    @property
    def power_factor(self) -> float | None:
        return _apply_sf(self._power_factor_raw, self._power_factor_sf)

    @property
    def dc_current(self) -> float | None:
        return _apply_sf(self._dc_current_raw, self._dc_current_sf)

    @property
    def dc_voltage(self) -> float | None:
        return _apply_sf(self._dc_voltage_raw, self._dc_voltage_sf)

    @property
    def dc_power(self) -> float | None:
        return _apply_sf(self._dc_power_raw, self._dc_power_sf)

    @property
    def temperature_cabinet(self) -> float | None:
        return _apply_sf(self._temperature_cabinet_raw, self._temperature_sf)

    @property
    def temperature_heatsink(self) -> float | None:
        return _apply_sf(self._temperature_heatsink_raw, self._temperature_sf)

    @property
    def temperature_transformer(self) -> float | None:
        return _apply_sf(self._temperature_transformer_raw, self._temperature_sf)

    @property
    def temperature_other(self) -> float | None:
        return _apply_sf(self._temperature_other_raw, self._temperature_sf)

    @property
    def energy_total(self) -> float | None:
        """Lifetime AC energy in Wh (WH scaled by WH_SF)."""
        raw = self._energy_raw
        if raw is None:
            return None
        return float(raw * 10 ** (self._energy_sf or 0))
