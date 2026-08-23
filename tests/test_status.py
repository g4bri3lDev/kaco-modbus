"""The plain-language layer: how readings are turned into something readable."""

from __future__ import annotations

import pytest

from kaco_modbus import OperatingState
from kaco_modbus.status import (
    bar,
    describe_state,
    efficiency,
    format_energy,
    format_power,
    judge,
)


@pytest.mark.parametrize(
    ("watts", "expected"),
    [
        (None, "—"),
        (0, "0 W"),
        (720, "720 W"),
        (999, "999 W"),
        (1000, "1.00 kW"),
        (8600, "8.60 kW"),
        (-450, "-450 W"),
    ],
)
def test_format_power(watts: float | None, expected: str) -> None:
    assert format_power(watts) == expected


@pytest.mark.parametrize(
    ("watt_hours", "expected"),
    [
        (None, "—"),
        (850, "850 Wh"),
        (12_500, "12.5 kWh"),
        (12_187_169, "12.19 MWh"),
    ],
)
def test_format_energy(watt_hours: float | None, expected: str) -> None:
    assert format_energy(watt_hours) == expected


class TestDescribeState:
    def test_every_state_is_explained(self) -> None:
        """No user should have to look up what 'MPPT' means — and every state
        must be covered, including the ones that rarely happen.
        """
        for state in OperatingState:
            text, style = describe_state(state)
            assert not text.startswith("State "), f"{state.name} has no explanation"
            assert style

    def test_a_fault_is_loud(self) -> None:
        text, style = describe_state(OperatingState.FAULT)
        assert "wrong" in text
        assert style == "red"

    def test_producing(self) -> None:
        assert describe_state(OperatingState.MPPT) == ("Producing power", "green")

    def test_night(self) -> None:
        text, style = describe_state(OperatingState.SLEEPING)
        assert "sunlight" in text
        assert style == "blue"

    def test_unknown_state(self) -> None:
        assert describe_state(None) == ("Unknown", "dim")


class TestJudge:
    """Grid readings are flagged against nominal, not shown bare."""

    def test_nominal_is_normal(self) -> None:
        assert judge(230.0, 230.0, 0.10) == ("normal", "green")

    def test_within_tolerance(self) -> None:
        assert judge(240.0, 230.0, 0.10)[0] == "normal"

    def test_above_tolerance(self) -> None:
        assert judge(260.0, 230.0, 0.10) == ("high", "yellow")

    def test_below_tolerance(self) -> None:
        assert judge(200.0, 230.0, 0.10) == ("low", "yellow")

    def test_frequency_is_judged_tightly(self) -> None:
        """1 % on 50 Hz is half a hertz; 49.94 is fine, 49.4 is not."""
        assert judge(49.94, 50.0, 0.01)[0] == "normal"
        assert judge(49.4, 50.0, 0.01)[0] == "low"

    def test_missing_reading(self) -> None:
        assert judge(None, 230.0, 0.10) == ("—", "dim")


class TestEfficiency:
    def test_a_normal_afternoon(self) -> None:
        assert efficiency(1000, 1020) == pytest.approx(98.03, abs=0.01)

    def test_withheld_when_the_reading_is_too_coarse(self) -> None:
        """Power comes in 10 W steps, so 460/460 would read as a false 100 %.

        Better to say nothing than to claim an inverter is perfect.
        """
        assert efficiency(460, 460) is None

    def test_withheld_when_idle(self) -> None:
        assert efficiency(0, 0) is None
        assert efficiency(None, None) is None

    def test_never_exceeds_one_hundred(self) -> None:
        """Rounding can put AC above DC; that is noise, not free energy."""
        result = efficiency(1020, 1010)
        assert result is not None
        assert result == 100.0


class TestBar:
    def test_empty_and_full(self) -> None:
        assert bar(0.0, width=10) == "░" * 10
        assert bar(1.0, width=10) == "█" * 10

    def test_half(self) -> None:
        assert bar(0.5, width=10) == "█████░░░░░"

    def test_clamps_out_of_range(self) -> None:
        assert bar(2.0, width=10) == "█" * 10
        assert bar(-1.0, width=10) == "░" * 10

    def test_unknown_fraction(self) -> None:
        assert bar(None, width=10) == "░" * 10

    def test_width_is_always_respected(self) -> None:
        for fraction in (0.0, 0.13, 0.5, 0.77, 1.0):
            assert len(bar(fraction, width=28)) == 28
