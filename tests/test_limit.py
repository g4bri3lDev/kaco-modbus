"""The kaco-limit CLI: supervised power limit tests against a real inverter."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

import pytest

from kaco_modbus import KacoInverter, WMaxLimEna
from kaco_modbus.limit import _run, build_parser
from kaco_modbus.testing import BLUEPLANET_86TL3, holding, without_model

if TYPE_CHECKING:
    from collections.abc import Iterator

    from modbus_connection.mock import MockModbusUnit

# Offsets within SunSpec model 123, counted from its header.
LIMIT = 5
REVERT_TIMER = 7
LIMIT_ENABLE = 9


@pytest.fixture
def controls(inverter: KacoInverter) -> int:
    """Where model 123 starts, found by discovery rather than by hand."""
    assert inverter.models is not None
    model = inverter.models.first(123)
    assert model is not None
    return model.address


@pytest.fixture
def writes(inverter_unit: MockModbusUnit) -> Iterator[list[int]]:
    """The address of every register write, in order."""
    recorded: list[int] = []
    inverter_unit.on_write(lambda event: recorded.append(event.address))
    yield recorded


async def run(unit: MockModbusUnit, *argv: str) -> int:
    return await _run(unit, build_parser().parse_args(["inverter.local", *argv]))


@pytest.mark.parametrize(
    "argv",
    [
        pytest.param(["set", "50", "--revert", "300"], id="set"),
        pytest.param(["resend", "--revert", "300"], id="resend"),
        pytest.param(["clear"], id="clear"),
    ],
)
async def test_writing_needs_confirmation(
    inverter_unit: MockModbusUnit, writes: list[int], argv: list[str]
) -> None:
    """Without the flag it says what it would do, and sends nothing."""
    assert await run(inverter_unit, *argv) == 2
    assert writes == []


async def test_show_writes_nothing(
    inverter_unit: MockModbusUnit, writes: list[int], capsys: pytest.CaptureFixture[str]
) -> None:
    assert await run(inverter_unit, "show") == 0
    assert writes == []
    assert "w_max_lim_pct_rvrt_tms" in capsys.readouterr().out


async def test_set_writes_period_limit_then_enable(
    inverter_unit: MockModbusUnit, writes: list[int], controls: int
) -> None:
    assert await run(inverter_unit, "set", "50", "--revert", "300", "--yes-write-to-inverter") == 0
    assert writes == [controls + REVERT_TIMER, controls + LIMIT, controls + LIMIT_ENABLE]


async def test_set_zero(inverter_unit: MockModbusUnit, writes: list[int], controls: int) -> None:
    """0 % is a real use: no feed-in while it would cost money."""
    assert await run(inverter_unit, "set", "0", "--revert", "300", "--yes-write-to-inverter") == 0
    assert controls + LIMIT in writes


async def test_resend_restarts_the_period(
    inverter_unit: MockModbusUnit,
    writes: list[int],
    controls: int,
    capsys: pytest.CaptureFixture[str],
) -> None:
    await run(inverter_unit, "set", "50", "--revert", "300", "--yes-write-to-inverter")
    writes.clear()

    assert await run(inverter_unit, "resend", "--revert", "120", "--yes-write-to-inverter") == 0
    assert writes == [controls + REVERT_TIMER, controls + LIMIT, controls + LIMIT_ENABLE]
    assert "revert=120 s" in capsys.readouterr().out


async def test_resend_without_a_limit(
    inverter_unit: MockModbusUnit, writes: list[int], capsys: pytest.CaptureFixture[str]
) -> None:
    """Nothing in force, nothing sent, and it says so."""
    assert await run(inverter_unit, "resend", "--revert", "120", "--yes-write-to-inverter") == 1
    assert writes == []
    assert "no limit in force" in capsys.readouterr().err


async def test_clear(inverter_unit: MockModbusUnit, writes: list[int], controls: int) -> None:
    await run(inverter_unit, "set", "50", "--revert", "300", "--yes-write-to-inverter")
    writes.clear()

    assert await run(inverter_unit, "clear", "--yes-write-to-inverter") == 0
    assert writes == [controls + LIMIT_ENABLE]


@pytest.mark.parametrize(
    "argv",
    [
        pytest.param(["set", "101", "--revert", "300"], id="over-100"),
        pytest.param(["set", "-1", "--revert", "300"], id="negative"),
        pytest.param(["set", "50"], id="no-revert"),
        pytest.param(["resend"], id="resend-no-revert"),
        pytest.param(["set", "50", "--revert", "70000"], id="revert-too-long"),
        pytest.param(["set", "50", "--revert", "0"], id="revert-zero"),
    ],
)
def test_refused_arguments(argv: list[str]) -> None:
    """A revert of 0 holds forever, so it is never implied by leaving it out."""
    with pytest.raises(SystemExit) as exc:
        build_parser().parse_args(["inverter.local", *argv])
    assert exc.value.code == 2


async def test_watch_prints_a_line_per_tick(
    inverter_unit: MockModbusUnit, capsys: pytest.CaptureFixture[str]
) -> None:
    sleep = AsyncMock()
    with patch("kaco_modbus.limit.asyncio.sleep", sleep):
        assert await run(inverter_unit, "show", "--watch", "30") == 0

    assert sleep.await_count == 3
    lines = [line for line in capsys.readouterr().out.splitlines() if "ac=" in line]
    # One before the first tick, then one per tick.
    assert len(lines) == 4


async def test_status_line(
    inverter_unit: MockModbusUnit, capsys: pytest.CaptureFixture[str]
) -> None:
    await run(inverter_unit, "set", "50", "--revert", "300", "--yes-write-to-inverter")
    line = capsys.readouterr().out.splitlines()[-1]
    assert "limit=50.0 %" in line
    assert f"enabled={WMaxLimEna.ENABLED.name}" in line
    assert "revert=300 s" in line


async def test_inverter_without_controls(
    mock_modbus_unit: MockModbusUnit, capsys: pytest.CaptureFixture[str]
) -> None:
    mock_modbus_unit.load_raw(holding(without_model(BLUEPLANET_86TL3, 123)))
    assert await run(mock_modbus_unit, "show") == 1
    assert "no SunSpec model 123" in capsys.readouterr().err


@pytest.mark.usefixtures("writes_ignored")
async def test_ignored_write_names_the_setting(
    inverter_unit: MockModbusUnit, capsys: pytest.CaptureFixture[str]
) -> None:
    """Write access off looks like success on the wire, so say what to check."""
    assert await run(inverter_unit, "set", "50", "--revert", "3600", "--yes-write-to-inverter") == 1
    assert "Schreibzugriff" in capsys.readouterr().err
