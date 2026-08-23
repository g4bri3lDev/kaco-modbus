"""Print what a KACO inverter reports, for diagnostics.

Run it against a real device::

    python -m kaco_modbus.query 192.168.0.155

Needs a backend, so install the ``cli`` extra: ``pip install kaco-modbus[cli]``.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from typing import TYPE_CHECKING, Any

from modbus_connection import ModbusError, ModbusTcpParams

from .const import VENDOR_MODEL_ID
from .device import KacoInverter
from .exceptions import KacoError

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit
    from modbus_connection.model import Component


def _show(component: Component, indent: str = "  ") -> None:
    """Print every declared field of *component*, marking absent ones."""
    for name in sorted(component.declared_fields):
        if name in ("model_id", "model_length"):
            continue
        value = getattr(component, name, None)
        rendered = "—" if value is None else repr(value)
        print(f"{indent}{name:<28} {rendered}")


async def _run(host: str, port: int, unit_id: int, raw: bool) -> int:
    from modbus_connection.tmodbus import ModbusConnection

    connection = ModbusConnection(ModbusTcpParams(host=host, port=port))
    try:
        unit: ModbusUnit = connection.for_unit(unit_id)
        device = KacoInverter(unit)
        report = await device.async_update()
    except KacoError as err:
        print(f"Not a supported inverter: {err}", file=sys.stderr)
        return 2
    except ModbusError as err:
        print(f"Could not read {host}:{port} unit {unit_id}: {err}", file=sys.stderr)
        return 1
    else:
        info = device.info
        assert info is not None
        print(f"{info.manufacturer} {info.model}")
        print(f"  firmware {info.firmware}   serial {info.serial_number}   options {info.options}")
        assert device.models is not None
        print(f"  SunSpec base {device.base_address}, models {sorted(device.models)}")
        if VENDOR_MODEL_ID in device.models:
            print(
                f"  note: model {VENDOR_MODEL_ID} is a KACO vendor block with no public "
                "definition; it is not decoded"
            )
        if report.failed:
            print("\nfailed to read:")
            for name, failure in report.failed.items():
                print(f"  {name}: {failure}")

        for name in report.updated:
            component = getattr(device, name)
            print(f"\n[{component.model_id}] {name}")
            _show(component)

        if device.strings:
            print("\nstrings")
            for string in device.strings:
                print(f"  {string.id_str}")
                _show(string, indent="    ")

        if device.controls is not None:
            held = (
                "held indefinitely"
                if device.revert_seconds is None
                else (f"reverts after {device.revert_seconds} s unless rewritten")
            )
            print(f"\nsetpoints: {held}")

        if raw:
            registers = await device.async_read_raw()
            print("\nraw registers")
            for space, values in sorted(registers.items()):
                print(f"  {space}: {len(values)} registers")
                for address in sorted(values):
                    print(f"    {address}  0x{values[address]:04X}")
        return 0
    finally:
        await connection.close()


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``kaco-query`` script."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("host", help="the inverter's address")
    parser.add_argument("--port", type=int, default=502, help="Modbus TCP port (default 502)")
    parser.add_argument(
        "--unit-id",
        type=int,
        default=1,
        help="Modbus unit ID (default 1; most KACO inverters ignore it)",
    )
    parser.add_argument("--raw", action="store_true", help="also dump every register")
    args: Any = parser.parse_args(argv)
    return asyncio.run(_run(args.host, args.port, args.unit_id, args.raw))


if __name__ == "__main__":
    raise SystemExit(main())
