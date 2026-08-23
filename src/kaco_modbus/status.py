"""Show what a KACO inverter is doing, in plain language.

For people rather than developers::

    kaco-status 192.168.0.155
    kaco-status 192.168.0.155 --watch

Where :mod:`kaco_modbus.query` dumps raw SunSpec field names, this explains what
the numbers mean. Needs ``pip install kaco-modbus[cli]``.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from typing import TYPE_CHECKING, Any

from modbus_connection import ModbusError, ModbusTcpParams

from .device import KacoInverter
from .exceptions import KacoError
from .models import OperatingState, VArPctEna, WMaxLimEna

if TYPE_CHECKING:
    from rich.console import RenderableType

# What each operating state means to someone who did not write the firmware,
# with the colour to show it in.
_STATES: dict[int, tuple[str, str]] = {
    OperatingState.OFF: ("Off", "dim"),
    OperatingState.SLEEPING: ("Asleep — not enough sunlight", "blue"),
    OperatingState.STARTING: ("Starting up", "yellow"),
    OperatingState.MPPT: ("Producing power", "green"),
    OperatingState.THROTTLED: ("Producing, but limited", "yellow"),
    OperatingState.SHUTTING_DOWN: ("Shutting down", "yellow"),
    OperatingState.FAULT: ("Stopped — something is wrong", "red"),
    OperatingState.STANDBY: ("On standby, not producing", "blue"),
}

# Grid limits. EN 50160 allows the supply voltage to sit within ±10 % of
# nominal, and the frequency within ±1 %; outside that the inverter is
# entitled to disconnect, so it is worth flagging.
_VOLTAGE_TOLERANCE = 0.10
_FREQUENCY_TOLERANCE = 0.01

# Below this DC input, the 10 W reporting granularity makes a conversion
# efficiency meaningless. See :func:`efficiency`.
_EFFICIENCY_FLOOR = 1000.0


def format_power(watts: float | None) -> str:
    """Render watts the way a person reads them."""
    if watts is None:
        return "—"
    if abs(watts) >= 1000:
        return f"{watts / 1000:.2f} kW"
    return f"{watts:.0f} W"


def format_energy(watt_hours: float | None) -> str:
    """Render a lifetime energy total, scaled to a sensible unit."""
    if watt_hours is None:
        return "—"
    if watt_hours >= 1_000_000:
        return f"{watt_hours / 1_000_000:.2f} MWh"
    if watt_hours >= 1000:
        return f"{watt_hours / 1000:.1f} kWh"
    return f"{watt_hours:.0f} Wh"


def describe_state(state: OperatingState | None) -> tuple[str, str]:
    """Return plain-language text and a colour for an operating state.

    Falls back to naming the raw value, so firmware that invents a state
    still renders rather than crashing.
    """
    if state is None:
        return "Unknown", "dim"
    return _STATES.get(int(state), (f"State {int(state)}", "dim"))


def judge(value: float | None, nominal: float, tolerance: float) -> tuple[str, str]:
    """Say whether a reading sits within *tolerance* of *nominal*."""
    if value is None:
        return "—", "dim"
    if value > nominal * (1 + tolerance):
        return "high", "yellow"
    if value < nominal * (1 - tolerance):
        return "low", "yellow"
    return "normal", "green"


def efficiency(ac_watts: float | None, dc_watts: float | None) -> float | None:
    """How much of the panels' power reaches the grid, as a percentage.

    ``None`` when the answer would not be trustworthy. This inverter reports
    power with a scale factor of 1, meaning 10 W steps, so at a few hundred
    watts the rounding is larger than the conversion loss and the ratio comes
    out as a flat 100 % — which is never true of a real inverter. Below
    :data:`_EFFICIENCY_FLOOR` the reading is withheld rather than invented.
    """
    if not ac_watts or not dc_watts or dc_watts < _EFFICIENCY_FLOOR:
        return None
    return min(ac_watts / dc_watts * 100, 100.0)


def bar(fraction: float | None, width: int = 28) -> str:
    """A block bar for a 0..1 fraction."""
    if fraction is None:
        return "░" * width
    filled = round(max(0.0, min(fraction, 1.0)) * width)
    return "█" * filled + "░" * (width - filled)


def _render(device: KacoInverter, failed: dict[str, ModbusError]) -> RenderableType:
    """Build the whole display for one poll."""
    from rich.columns import Columns
    from rich.console import Group
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    info = device.info
    ac = device.inverter
    assert info is not None
    assert ac is not None

    state_text, state_colour = describe_state(ac.st)
    rated = device.nameplate.w_rtg if device.nameplate else None

    header = Table.grid(expand=True)
    header.add_column()
    header.add_column(justify="right")
    header.add_row(
        Text.assemble(("● ", state_colour), (state_text, f"bold {state_colour}")),
        Text(f"{info.manufacturer} · {format_power(rated)} rated", style="dim"),
    )

    # The headline: what it is making right now, against what it could make.
    share = (ac.w / rated) if (ac.w is not None and rated) else None
    headline = Table.grid(padding=(0, 2))
    headline.add_column(justify="right")
    headline.add_column()
    headline.add_row(
        Text(format_power(ac.w), style=f"bold {state_colour}"),
        Text.assemble(
            (bar(share), state_colour),
            ("  " + (f"{share * 100:.0f}% of capacity" if share is not None else ""), "dim"),
        ),
    )

    panels = Table(box=None, show_header=True, header_style="bold", padding=(0, 2))
    panels.add_column("String")
    panels.add_column("Voltage", justify="right")
    panels.add_column("Current", justify="right")
    panels.add_column("Power", justify="right")
    panels.add_column("Share", justify="right")
    total_dc = sum(s.dcw for s in device.strings if s.dcw is not None)
    for index, string in enumerate(device.strings, start=1):
        portion = (string.dcw / total_dc) if (string.dcw and total_dc) else None
        panels.add_row(
            f"String {index}",
            f"{string.dcv:.0f} V" if string.dcv is not None else "—",
            f"{string.dca:.2f} A" if string.dca is not None else "—",
            format_power(string.dcw),
            f"{portion * 100:.0f}%" if portion is not None else "—",
        )
    if not device.strings:
        panels.add_row("[dim]this inverter does not report per-string values[/dim]")

    nominal_v = device.settings.v_ref if device.settings else None
    nominal_v = nominal_v if nominal_v else 230.0
    nominal_hz = 50.0 if (device.frequency is None or 45 < device.frequency < 55) else 60.0

    grid = Table(box=None, show_header=False, padding=(0, 2))
    grid.add_column()
    grid.add_column(justify="right")
    grid.add_column()
    phases = tuple((f"Phase {i}", v) for i, v in enumerate(device.phase_voltages, start=1))
    for name, volts in phases:
        verdict, colour = judge(volts, nominal_v, _VOLTAGE_TOLERANCE)
        reading = f"{volts:.1f} V" if volts is not None else "—"
        grid.add_row(name, reading, f"[{colour}]{verdict}[/]")
    frequency = device.frequency
    verdict, colour = judge(frequency, nominal_hz, _FREQUENCY_TOLERANCE)
    reading = f"{frequency:.2f} Hz" if frequency is not None else "—"
    grid.add_row("Frequency", reading, f"[{colour}]{verdict}[/]")
    if (power_factor := device.power_factor) is not None:
        grid.add_row("Power factor", f"{power_factor:.2f}", "[dim]ideal is 1.00[/dim]")

    columns = Columns(
        [
            Panel(panels, title="Solar panels", border_style="dim", padding=(1, 1)),
            Panel(grid, title="Grid", border_style="dim", padding=(1, 1)),
        ],
        equal=True,
        expand=True,
    )

    summary = Table.grid(expand=True, padding=(0, 3))
    for _ in range(3):
        summary.add_column(justify="center")
    loss = efficiency(ac.w, ac.dcw)
    summary.add_row(
        Text.assemble(("Generated all-time\n", "dim"), (format_energy(ac.wh), "bold")),
        Text.assemble(("Conversion efficiency\n", "dim"), (f"{loss:.1f}%", "bold"))
        if loss is not None
        else Text.assemble(
            ("Conversion efficiency\n", "dim"), ("too little sun to tell", "dim italic")
        ),
        Text.assemble(
            ("Temperature\n", "dim"),
            (
                f"{device.temperature:.0f} °C"
                if device.temperature is not None
                else "not while asleep"
            ),
        ),
    )

    parts: list[RenderableType] = [header, "", headline, "", columns, "", summary]

    for note in _notes(device, failed):
        parts.extend(["", note])

    return Panel(
        Group(*parts),
        title=f"[bold]{info.model}[/bold]",
        subtitle=f"[dim]{info.serial_number} · firmware {info.firmware}[/dim]",
        border_style=state_colour,
        padding=(1, 2),
    )


def _notes(device: KacoInverter, failed: dict[str, ModbusError]) -> list[str]:
    """Anything the reader should be told about, in plain language."""
    notes: list[str] = []
    controls = device.controls
    if controls is not None:
        if controls.w_max_lim_ena is WMaxLimEna.ENABLED:
            limit = controls.w_max_lim_pct
            notes.append(
                f"[yellow]Output is being limited to {limit:.0f}% on purpose.[/yellow]"
                if limit is not None
                else "[yellow]Output is being limited on purpose.[/yellow]"
            )
        if controls.v_ar_pct_ena is VArPctEna.ENABLED:
            notes.append("[yellow]A reactive power setpoint is active.[/yellow]")

    ac = device.inverter
    if ac is not None and ac.evt1:
        notes.append(f"[red]The inverter is reporting a fault: {ac.evt1!r}[/red]")

    if failed:
        names = ", ".join(sorted(failed))
        notes.append(f"[dim]Some readings were unavailable this cycle: {names}[/dim]")

    return notes


async def _run(host: str, port: int, unit_id: int, watch: float | None) -> int:
    from modbus_connection.tmodbus import ModbusConnection
    from rich.console import Console
    from rich.live import Live

    console = Console()
    connection = ModbusConnection(ModbusTcpParams(host=host, port=port))
    device = KacoInverter(connection.for_unit(unit_id))

    async def poll() -> RenderableType:
        report = await device.async_update()
        return _render(device, report.failed)

    try:
        try:
            first = await poll()
        except KacoError as err:
            console.print(f"[red]{host} does not look like a SunSpec inverter:[/red] {err}")
            return 2
        except ModbusError as err:
            console.print(f"[red]Could not reach {host}:{port}:[/red] {err}")
            console.print("[dim]If the sun is down, the inverter may simply be asleep.[/dim]")
            return 1

        if watch is None:
            console.print(first)
            return 0

        with Live(first, console=console, refresh_per_second=4, screen=True) as live:
            while True:
                await asyncio.sleep(watch)
                try:
                    live.update(await poll())
                except ModbusError as err:
                    live.update(f"[red]Lost contact with {host}:[/red] {err}")
    except KeyboardInterrupt:  # pragma: no cover - interactive
        return 0
    finally:
        await connection.close()


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``kaco-status`` script."""
    parser = argparse.ArgumentParser(
        description="Show what a KACO solar inverter is doing, in plain language."
    )
    parser.add_argument("host", help="the inverter's address, e.g. 192.168.0.155")
    parser.add_argument("--port", type=int, default=502, help="Modbus TCP port (default 502)")
    parser.add_argument(
        "--unit-id",
        type=int,
        default=1,
        help="Modbus unit ID (default 1; most KACO inverters ignore it)",
    )
    parser.add_argument(
        "--watch",
        nargs="?",
        type=float,
        const=5.0,
        default=None,
        metavar="SECONDS",
        help="keep the display updating (default every 5 s); Ctrl-C to stop",
    )
    parser.add_argument("--debug", action="store_true", help="show library logging and tracebacks")
    args: Any = parser.parse_args(argv)

    # The backends log a traceback when a connection times out. That is useful
    # when debugging and pure noise for someone who just wants to know whether
    # the sun is out, so keep it quiet unless asked.
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.CRITICAL)

    try:
        return asyncio.run(_run(args.host, args.port, args.unit_id, args.watch))
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())
