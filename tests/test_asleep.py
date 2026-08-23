"""What this firmware reports after dark, and what we refuse to pass on.

Unlike SolarEdge or Sofar, a KACO stays on Modbus overnight and answers
normally. The catch is that it parks the registers it is no longer measuring
at zero rather than at the "not implemented" sentinel, so a naive read claims
a dead grid and a freezing cabinet. These are real readings, captured from the
hardware in the SLEEPING state.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from kaco_modbus import KacoInverter, OperatingState
from kaco_modbus.testing import BLUEPLANET_86TL3_ASLEEP

if TYPE_CHECKING:
    from modbus_connection.mock import MockModbusUnit


@pytest.fixture
async def asleep(mock_modbus_unit: MockModbusUnit) -> KacoInverter:
    """The inverter as captured after dark."""
    mock_modbus_unit.load_raw({"holding": BLUEPLANET_86TL3_ASLEEP})
    device = KacoInverter(mock_modbus_unit)
    await device.async_update()
    return device


async def test_it_still_answers(asleep: KacoInverter) -> None:
    """The whole point: it does not go silent, so nothing is unavailable."""
    report = await asleep.async_update()
    assert report.failed == {}
    assert "inverter" in report.updated


async def test_it_reports_sleeping(asleep: KacoInverter) -> None:
    assert asleep.inverter is not None
    assert asleep.inverter.st is OperatingState.SLEEPING
    assert asleep.is_running is False


async def test_a_producing_inverter_is_running(inverter: KacoInverter) -> None:
    assert inverter.is_running is True


class TestGenuineZeros:
    """Not everything zero at night is wrong — most of it is simply true."""

    async def test_power_really_is_zero(self, asleep: KacoInverter) -> None:
        assert asleep.inverter is not None
        assert asleep.inverter.w == 0
        assert asleep.inverter.dcw == 0

    async def test_current_really_is_zero(self, asleep: KacoInverter) -> None:
        assert asleep.inverter is not None
        assert asleep.inverter.a == 0.0

    async def test_strings_really_produce_nothing(self, asleep: KacoInverter) -> None:
        assert [s.dcw for s in asleep.strings] == [0, 0]

    async def test_lifetime_energy_still_counts(self, asleep: KacoInverter) -> None:
        """It is a meter, not a measurement — it must survive the night."""
        assert asleep.inverter is not None
        assert asleep.inverter.wh is not None
        assert asleep.inverter.wh > 12_000_000


class TestWithheldReadings:
    """Readings the inverter parks at zero rather than measuring."""

    async def test_the_grid_is_not_actually_dead(self, asleep: KacoInverter) -> None:
        """The raw register says 0 Hz. The mains is plainly still live."""
        assert asleep.inverter is not None
        assert asleep.inverter.hz == 0.0  # what the device claims
        assert asleep.frequency is None  # what we are willing to report

    async def test_the_mains_is_not_actually_at_zero_volts(self, asleep: KacoInverter) -> None:
        assert asleep.inverter is not None
        assert asleep.inverter.ph_vph_a == 0.0
        assert asleep.phase_voltages == (None, None, None)

    async def test_the_cabinet_is_not_actually_freezing(self, asleep: KacoInverter) -> None:
        """0.0 degC on a warm night is the register being parked, not weather."""
        assert asleep.inverter is not None
        assert asleep.inverter.tmp_cab == 0.0
        assert asleep.temperature is None

    async def test_string_temperatures_are_withheld(self, asleep: KacoInverter) -> None:
        assert asleep.string_temperature(0) is None
        assert asleep.string_temperature(1) is None


class TestWhileRunning:
    """The same accessors pass readings straight through while producing."""

    async def test_frequency(self, inverter: KacoInverter) -> None:
        assert inverter.frequency == 49.944

    async def test_phase_voltages(self, inverter: KacoInverter) -> None:
        assert inverter.phase_voltages == (226.5, 228.2, 227.8)

    async def test_temperature(self, inverter: KacoInverter) -> None:
        assert inverter.temperature == 46.9

    async def test_string_temperature(self, inverter: KacoInverter) -> None:
        assert inverter.string_temperature(0) == 45

    async def test_a_string_that_does_not_exist(self, inverter: KacoInverter) -> None:
        assert inverter.string_temperature(9) is None


async def test_gating_is_on_state_not_on_the_value(inverter: KacoInverter) -> None:
    """A genuine 0 degC in winter must still be reported.

    Suppressing whenever the value happens to be zero would hide a real
    reading; suppressing on the operating state does not.
    """
    assert inverter.is_running is True
    assert inverter._measured(0.0) == 0.0


async def test_power_factor_is_withheld(asleep: KacoInverter) -> None:
    """Parked at 1.00 rather than zeroed — undefined with no current flowing."""
    assert asleep.inverter is not None
    assert asleep.inverter.pf == 1.0
    assert asleep.power_factor is None


async def test_power_factor_while_running(inverter: KacoInverter) -> None:
    assert inverter.power_factor == 1.0
