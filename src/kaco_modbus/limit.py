"""Set, resend or clear a KACO inverter's power limit, for supervised tests.

This writes to the inverter's grid control. It exists to verify on hardware
what the library's setters do, while someone watches::

    kaco-limit 192.168.0.155 show
    kaco-limit 192.168.0.155 set 50 --revert 300 --watch 420 --yes-write-to-inverter

Nothing is written without ``--yes-write-to-inverter``. ``--revert`` is
required wherever a limit is written, because ``0`` holds it indefinitely.

Needs a backend, so install the ``cli`` extra: ``pip install kaco-modbus[cli]``.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import datetime
from typing import TYPE_CHECKING, Any

from modbus_connection import ModbusError, ModbusTcpParams

from .device import KacoInverter
from .exceptions import KacoError
from .query import _show

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit

WATCH_TICK = 10.0
# The revert timers are uint16 seconds.
MAX_REVERT_SECONDS = 0xFFFF


def _percent(value: str) -> float:
    percent = float(value)
    if not 0.0 <= percent <= 100.0:
        raise argparse.ArgumentTypeError(f"must be between 0 and 100, got {value}")
    return percent


def _seconds(value: str) -> int:
    seconds = int(value)
    if not 0 <= seconds <= MAX_REVERT_SECONDS:
        raise argparse.ArgumentTypeError(f"must be between 0 and {MAX_REVERT_SECONDS}, got {value}")
    return seconds


def _status_line(device: KacoInverter) -> str:
    """One timestamped line: what the inverter does and what limit it holds."""
    ac = device.inverter
    controls = device.controls
    state = ac.st.name if ac is not None and ac.st is not None else "—"
    power = ac.w if ac is not None else None
    parts = [
        datetime.now().strftime("%H:%M:%S"),
        f"state={state}",
        f"ac={'—' if power is None else f'{power:g}'} W",
    ]
    if controls is not None:
        enabled = controls.w_max_lim_ena
        parts += [
            f"limit={controls.w_max_lim_pct} %",
            f"enabled={'—' if enabled is None else enabled.name}",
            f"revert={controls.w_max_lim_pct_rvrt_tms} s",
        ]
    return "  ".join(parts)


def _intended(args: Any) -> str:
    if args.action == "set":
        return f"set the limit to {args.percent:g} % with a {args.revert} s revert period"
    if args.action == "resend":
        return f"resend the active limit with a {args.revert} s revert period"
    return "disable the limit"


async def _run(unit: ModbusUnit, args: Any) -> int:
    """Do what *args* asks of the inverter on *unit*."""
    if args.action != "show" and not args.yes_write_to_inverter:
        print(
            f"Would {_intended(args)}. Nothing was sent; pass --yes-write-to-inverter to do it.",
            file=sys.stderr,
        )
        return 2

    device = KacoInverter(unit)
    await device.async_update_readings()
    if device.controls is None:
        print("This inverter exposes no SunSpec model 123.", file=sys.stderr)
        return 1

    if args.action == "show":
        print("[123] controls")
        _show(device.controls)
    elif args.action == "set":
        await device.async_set_power_limit(args.percent, revert_seconds=args.revert)
        print(f"setpoints_held={device.setpoints_held}")
    elif args.action == "resend":
        if not await device.async_resend_power_limit(args.revert):
            print("There is no limit in force to resend.", file=sys.stderr)
            return 1
        print(f"setpoints_held={device.setpoints_held}")
    else:
        await device.async_clear_power_limit()

    print(_status_line(device))
    for _ in range(int(args.watch // WATCH_TICK)):
        await asyncio.sleep(WATCH_TICK)
        await device.async_update_readings()
        print(_status_line(device), flush=True)
    return 0


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--watch",
        type=float,
        default=0.0,
        metavar="SECONDS",
        help=f"keep printing the state every {WATCH_TICK:g} s for this long",
    )
    common.add_argument(
        "--yes-write-to-inverter",
        action="store_true",
        help="actually write; without it, only print what would be sent",
    )

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("host", help="the inverter's address, e.g. 192.168.0.155")
    parser.add_argument("--port", type=int, default=502, help="Modbus TCP port (default 502)")
    parser.add_argument("--unit-id", type=int, default=1, help="Modbus unit ID (default 1)")
    actions = parser.add_subparsers(dest="action", required=True)

    actions.add_parser("show", parents=[common], help="print model 123 and the state; read-only")
    set_ = actions.add_parser("set", parents=[common], help="set and enable a limit")
    set_.add_argument("percent", type=_percent, help="0 to 100 %% of rated power")
    resend = actions.add_parser("resend", parents=[common], help="resend the active limit")
    for sub in (set_, resend):
        sub.add_argument(
            "--revert",
            type=_seconds,
            required=True,
            metavar="SECONDS",
            help="revert period the inverter keeps the limit for; 0 holds it indefinitely",
        )
    actions.add_parser("clear", parents=[common], help="disable the limit")
    return parser


async def _connect_and_run(args: Any) -> int:
    from modbus_connection.tmodbus import ModbusConnection

    connection = ModbusConnection(ModbusTcpParams(host=args.host, port=args.port))
    try:
        return await _run(connection.for_unit(args.unit_id), args)
    except KacoError as err:
        print(f"Not a supported inverter: {err}", file=sys.stderr)
        return 2
    except ModbusError as err:
        print(f"Modbus error talking to {args.host}:{args.port}: {err}", file=sys.stderr)
        return 1
    finally:
        await connection.close()


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``kaco-limit`` script."""
    args = build_parser().parse_args(argv)
    try:
        return asyncio.run(_connect_and_run(args))
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())
