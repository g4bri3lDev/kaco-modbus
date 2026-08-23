"""The device object: one KACO inverter reached through a ``ModbusUnit``."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from modbus_connection import (
    IllegalDataAddressError,
    IllegalDataValueError,
    IllegalFunctionError,
    ModbusError,
)
from modbus_connection.model.sunspec import SunSpecError, scan

from .const import (
    INVERTER_MODEL_ID,
    READINGS,
    RUNNING_STATES,
    SETTINGS,
    SUNSPEC_BASE_ADDRESSES,
)
from .exceptions import ModelMissingError, SunSpecNotFoundError
from .models import (
    Common,
    Conn,
    Controls,
    Hfrt,
    Hvrt,
    InverterThreePhase,
    Lfrt,
    Lvrt,
    Mppt,
    Nameplate,
    OutPFSetEna,
    Settings,
    Status,
    VArPctEna,
    VArPctMod,
    VoltVar,
    VoltWatt,
    WMaxLimEna,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    from modbus_connection import ModbusUnit
    from modbus_connection.model import Component
    from modbus_connection.model.sunspec import SunSpecComponent, SunSpecModels

    from .models import MpptModule

_LOGGER = logging.getLogger(__name__)

# A model the device never advertised, or one it advertises but refuses to
# read. Strict SunSpec omits absent models from the chain, but not every
# device is strict — some list a model and then reject reads of it. Both mean
# "this inverter does not have it".
_ABSENT = (IllegalDataAddressError, IllegalFunctionError)


@dataclass
class UpdateReport:
    """What one poll managed to refresh."""

    updated: list[str] = field(default_factory=list)
    failed: dict[str, ModbusError] = field(default_factory=dict)


@dataclass(frozen=True)
class DeviceInfo:
    """What SunSpec model 1 says about this inverter. Read once, at setup."""

    manufacturer: str
    model: str
    serial_number: str
    firmware: str
    options: str


class KacoInverter:
    """A KACO inverter reached through a ``ModbusUnit``.

    The caller owns the connection: this object only reads and writes
    registers, and never opens or closes anything. That keeps it usable
    against any backend, and against the in-memory mock in tests.

    Which components exist is settled once, by :meth:`_async_setup`, from what
    the device's SunSpec chain actually advertises. Everything after that
    polls a fixed list.
    """

    def __init__(self, unit: ModbusUnit, *, base_address: int | None = None) -> None:
        """Prepare to talk to the inverter on *unit*.

        Pass *base_address* to skip discovery of where the SunSpec map starts;
        by default the standard locations are probed in turn.
        """
        self._unit = unit
        self._base_addresses = (
            (base_address,) if base_address is not None else SUNSPEC_BASE_ADDRESSES
        )

        self.info: DeviceInfo | None = None
        self.base_address: int | None = None
        self.models: SunSpecModels | None = None

        # Readings.
        self.inverter: InverterThreePhase | None = None
        self.mppt: Mppt | None = None
        self.status: Status | None = None

        # Settings.
        self.nameplate: Nameplate | None = None
        self.settings: Settings | None = None
        self.controls: Controls | None = None
        self.volt_var: VoltVar | None = None

        # Grid-code curves. Bound if present but never polled by default:
        # they are static configuration, and reading them costs a lot of
        # registers. Use :meth:`async_update_curves` to read them on demand.
        self.curves: dict[str, SunSpecComponent] = {}

        self._readings: tuple[str, ...] | None = None
        self._settings: tuple[str, ...] = ()

        # Whether this device let us clear a setpoint's revert timer. None
        # until a setpoint is written. See :meth:`async_set_power_limit`.
        self.setpoints_held: bool | None = None

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    async def _async_discover(self) -> SunSpecModels:
        """Find the SunSpec map, trying each standard base address in turn."""
        for base in self._base_addresses:
            try:
                models = await scan(self._unit, base)
            except (SunSpecError, *_ABSENT) as err:
                # No marker here. A transport failure is a different thing and
                # deliberately propagates instead.
                _LOGGER.debug("No SunSpec map at %s: %s", base, err)
                continue
            _LOGGER.debug("SunSpec map at %s: models %s", base, sorted(models))
            self.base_address = base
            return models
        raise SunSpecNotFoundError(
            f"no SunSpec marker at any of {', '.join(str(b) for b in self._base_addresses)}"
        )

    def _bind(self, component: type[Any], *model_ids: int) -> Any | None:
        """Return *component* bound to the first of *model_ids* present."""
        assert self.models is not None
        if (found := self.models.first(*model_ids)) is None:
            return None
        return component(self._unit, found)

    async def _async_setup(self) -> None:
        """Read what never changes, and settle which components this unit has."""
        self.models = await self._async_discover()

        if (common := self._bind(Common, 1)) is None:
            raise SunSpecNotFoundError("device has no SunSpec model 1 (common)")
        await common.async_update()
        self.info = DeviceInfo(
            manufacturer=common.mn or "KACO new energy",
            model=common.md or "unknown",
            serial_number=common.sn or "",
            firmware=common.vr or "",
            options=common.opt or "",
        )

        self.inverter = self._bind(InverterThreePhase, INVERTER_MODEL_ID)
        if self.inverter is None:
            raise ModelMissingError(f"device exposes no SunSpec inverter model {INVERTER_MODEL_ID}")

        self.status = self._bind(Status, 122)
        self.nameplate = self._bind(Nameplate, 120)
        self.settings = self._bind(Settings, 121)
        self.controls = self._bind(Controls, 123)
        self.volt_var = self._bind(VoltVar, 126)

        # How many MPPT strings this inverter has is fixed by its hardware, so
        # resolve the repeating group once rather than on every poll.
        if (mppt := self._bind(Mppt, 160)) is not None:
            try:
                await mppt.async_update_repeating_groups()
            except _ABSENT:
                _LOGGER.debug("Model 160 is advertised but unreadable; ignoring it")
            else:
                self.mppt = mppt

        for name, component, model_id in (
            ("volt_watt", VoltWatt, 132),
            ("lvrt", Lvrt, 129),
            ("hvrt", Hvrt, 130),
            ("lfrt", Lfrt, 135),
            ("hfrt", Hfrt, 136),
        ):
            if (bound := self._bind(component, model_id)) is not None:
                self.curves[name] = bound

        self._readings = tuple(n for n in READINGS if getattr(self, n) is not None)
        self._settings = tuple(n for n in SETTINGS if getattr(self, n) is not None)
        _LOGGER.debug(
            "%s: readings=%s settings=%s curves=%s",
            self.info.model,
            self._readings,
            self._settings,
            sorted(self.curves),
        )

    async def _async_ensure_setup(self) -> tuple[str, ...]:
        """Run setup if it has not run, and return the readings to poll."""
        if self._readings is None:
            await self._async_setup()
            assert self._readings is not None
        return self._readings

    # ------------------------------------------------------------------
    # Polling
    # ------------------------------------------------------------------

    @property
    def strings(self) -> Sequence[MpptModule]:
        """The per-string MPPT sub-blocks, empty if this unit has no model 160."""
        if self.mppt is None:
            return ()
        return self.mppt.module

    # ------------------------------------------------------------------
    # Readings that are only meaningful while the inverter is running
    # ------------------------------------------------------------------

    @property
    def is_running(self) -> bool:
        """Whether the inverter is converting power right now.

        While it is not, it keeps answering Modbus but stops measuring the
        grid and its own temperature. See :data:`RUNNING_STATES`.
        """
        if self.inverter is None:
            return False
        state = self.inverter.st
        return state is not None and int(state) in RUNNING_STATES

    def _measured(self, value: float | None) -> float | None:
        """Pass *value* through only while the inverter is actually measuring.

        The registers below are parked at zero when it is not, so returning
        the raw reading would claim a dead grid and a freezing cabinet.
        """
        return value if self.is_running else None

    @property
    def frequency(self) -> float | None:
        """Grid frequency in Hz, or None when not being measured.

        Reported as 0.0 while asleep, which would look like the grid is gone.
        """
        return self._measured(self.inverter.hz if self.inverter else None)

    @property
    def phase_voltages(self) -> tuple[float | None, float | None, float | None]:
        """Phase-to-neutral voltages, or None each when not being measured.

        Reported as 0.0 while asleep, though the mains is plainly still live.
        """
        if self.inverter is None:
            return (None, None, None)
        return (
            self._measured(self.inverter.ph_vph_a),
            self._measured(self.inverter.ph_vph_b),
            self._measured(self.inverter.ph_vph_c),
        )

    @property
    def power_factor(self) -> float | None:
        """Power factor, or None when not being measured.

        Parked at 1.00 while asleep rather than zeroed, which is just as
        misleading: with no current flowing the ratio is undefined.
        """
        return self._measured(self.inverter.pf if self.inverter else None)

    @property
    def temperature(self) -> float | None:
        """Cabinet temperature in degC, or None when not being measured.

        Reported as 0.0 while asleep. Gating on the operating state rather
        than on the value keeps a genuine 0 degC in winter honest.
        """
        return self._measured(self.inverter.tmp_cab if self.inverter else None)

    def string_temperature(self, index: int) -> float | None:
        """Temperature of one MPPT string, or None when not being measured."""
        strings = self.strings
        if index >= len(strings):
            return None
        return self._measured(strings[index].tmp)

    async def _async_poll(self, names: Iterable[str], report: UpdateReport) -> UpdateReport:
        """Read each named component on its own, recording what happened.

        Components are polled one at a time rather than as a group: a group
        aborts every read when one block fails, so a single slow or broken
        register range would take out every entity instead of its own.
        """
        for name in names:
            component: Component = getattr(self, name)
            try:
                await component.async_update(notify=False)
            except ModbusError as err:
                report.failed[name] = err
            else:
                report.updated.append(name)
        return report

    def _notify(self, report: UpdateReport) -> None:
        """Fire the listeners of everything this update refreshed."""
        for name in report.updated:
            getattr(self, name).notify()

    async def async_update_readings(self) -> UpdateReport:
        """Refresh what the inverter measures — power, voltages, strings."""
        readings = await self._async_ensure_setup()
        report = await self._async_poll(readings, UpdateReport())
        self._notify(report)
        return report

    async def async_update_settings(self) -> UpdateReport:
        """Refresh what the inverter is configured to do."""
        await self._async_ensure_setup()
        report = await self._async_poll(self._settings, UpdateReport())
        self._notify(report)
        return report

    async def async_update(self) -> UpdateReport:
        """Refresh readings and settings together."""
        readings = await self._async_ensure_setup()
        report = await self._async_poll(readings, UpdateReport())
        await self._async_poll(self._settings, report)
        self._notify(report)
        return report

    async def async_update_curves(self) -> UpdateReport:
        """Read the grid-code curve models. Not part of a normal poll."""
        await self._async_ensure_setup()
        report = UpdateReport()
        for name, component in self.curves.items():
            try:
                await component.async_update(notify=False)
            except ModbusError as err:
                report.failed[name] = err
            else:
                report.updated.append(name)
                component.notify()
        return report

    async def async_read_raw(self) -> dict[str, dict[int, int | bool]]:
        """Every register this device reads, undecoded — for diagnostics."""
        readings = await self._async_ensure_setup()
        raw: dict[str, dict[int, int | bool]] = {}
        for name in (*readings, *self._settings):
            read = await getattr(self, name).async_read_raw(notify=False)
            for space, values in read.items():
                raw.setdefault(space, {}).update(values)
        return raw

    # ------------------------------------------------------------------
    # Control (SunSpec model 123 only)
    # ------------------------------------------------------------------

    def _require_controls(self) -> Controls:
        """Return the immediate-controls component, or explain its absence."""
        if self.controls is None:
            raise ModelMissingError(
                "this inverter does not expose SunSpec model 123, so it cannot be controlled"
            )
        return self.controls

    @property
    def revert_seconds(self) -> int | None:
        """How long a power-limit setpoint survives before reverting.

        ``None`` once :meth:`async_set_power_limit` has succeeded in clearing
        the timer, or if the device does not implement one.
        """
        if self.controls is None:
            return None
        # A zero timer means "hold indefinitely", which is the same answer as
        # a device with no timer at all: there is no window to refresh within.
        value = self.controls.w_max_lim_pct_rvrt_tms
        return int(value) if value else None

    async def _async_hold(self, revert_field: str) -> bool:
        """Try to clear a setpoint's revert timer so the value sticks.

        Returns whether the device allowed it. When it does not, the caller
        must rewrite the setpoint within :attr:`revert_seconds` to keep it.
        """
        controls = self._require_controls()
        try:
            await controls.write(revert_field, 0)
        except (IllegalDataValueError, *_ABSENT) as err:
            _LOGGER.debug("Device refuses to clear %s: %s", revert_field, err)
            return False
        return True

    async def async_set_power_limit(self, percent: float, *, enable: bool = True) -> None:
        """Curtail output to *percent* of nameplate power.

        Writes the setpoint before enabling it, so the inverter never briefly
        applies a stale limit.
        """
        if not 0.0 <= percent <= 100.0:
            raise ValueError(f"power limit must be between 0 and 100 %, got {percent}")
        controls = self._require_controls()
        await controls.write("w_max_lim_pct", percent)
        self.setpoints_held = await self._async_hold("w_max_lim_pct_rvrt_tms")
        await controls.write("w_max_lim_ena", WMaxLimEna.ENABLED if enable else WMaxLimEna.DISABLED)
        await controls.async_update()

    async def async_clear_power_limit(self) -> None:
        """Stop curtailing and return the inverter to full output.

        The setpoint itself is left alone, so it is still visible — and still
        there to be re-enabled.
        """
        controls = self._require_controls()
        await controls.write("w_max_lim_ena", WMaxLimEna.DISABLED)
        await controls.async_update()

    async def async_set_power_factor(self, power_factor: float, *, enable: bool = True) -> None:
        """Hold output at a fixed *power_factor*, the cosine of the phase angle."""
        if not -1.0 <= power_factor <= 1.0:
            raise ValueError(f"power factor must be between -1 and 1, got {power_factor}")
        controls = self._require_controls()
        await controls.write("out_pf_set", power_factor)
        await self._async_hold("out_pf_set_rvrt_tms")
        await controls.write(
            "out_pf_set_ena", OutPFSetEna.ENABLED if enable else OutPFSetEna.DISABLED
        )
        await controls.async_update()

    async def async_clear_power_factor(self) -> None:
        """Stop holding a fixed power factor."""
        controls = self._require_controls()
        await controls.write("out_pf_set_ena", OutPFSetEna.DISABLED)
        await controls.async_update()

    async def async_set_reactive_power(
        self, percent: float, *, mode: VArPctMod = VArPctMod.WMax, enable: bool = True
    ) -> None:
        """Set reactive power to *percent*, interpreted according to *mode*.

        A negative value reverses the direction of the reactive flow.
        """
        if not -100.0 <= percent <= 100.0:
            raise ValueError(f"reactive power must be between -100 and 100 %, got {percent}")
        controls = self._require_controls()
        field = "v_ar_w_max_pct" if mode is VArPctMod.WMax else "v_ar_max_pct"
        await controls.write("v_ar_pct_mod", mode)
        await controls.write(field, percent)
        await self._async_hold("v_ar_pct_rvrt_tms")
        await controls.write("v_ar_pct_ena", VArPctEna.ENABLED if enable else VArPctEna.DISABLED)
        await controls.async_update()

    async def async_clear_reactive_power(self) -> None:
        """Stop applying a reactive power setpoint."""
        controls = self._require_controls()
        await controls.write("v_ar_pct_ena", VArPctEna.DISABLED)
        await controls.async_update()

    async def async_set_connected(self, connected: bool) -> None:
        """Connect the inverter to the grid, or disconnect it.

        Disconnecting stops export entirely. On most installations this is
        subject to the interconnection agreement.
        """
        controls = self._require_controls()
        await controls.write("conn", Conn.CONNECT if connected else Conn.DISCONNECT)
        await controls.async_update()
