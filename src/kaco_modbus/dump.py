"""Dump a KACO inverter's SunSpec registers — the on-site ground-truth tool.

Usage:  python -m kaco_modbus.dump 192.168.1.50 --json dump.json
Needs:  pip install "kaco-modbus[cli]"
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from typing import TYPE_CHECKING

from .discovery import END_MODEL_ID, find_sunspec_base, walk_model_chain
from .kaco import KacoInverter

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit

_CHUNK = 100  # registers per read while dumping

_REPORT_FIELDS = (
    "ac_current",
    "current_phase_a",
    "current_phase_b",
    "current_phase_c",
    "voltage_ab",
    "voltage_bc",
    "voltage_ca",
    "voltage_phase_a",
    "voltage_phase_b",
    "voltage_phase_c",
    "ac_power",
    "frequency",
    "apparent_power",
    "reactive_power",
    "power_factor",
    "energy_total",
    "dc_current",
    "dc_voltage",
    "dc_power",
    "temperature_cabinet",
    "temperature_heatsink",
    "temperature_transformer",
    "temperature_other",
    "state",
    "vendor_state",
    "events",
)


async def dump_registers(unit: ModbusUnit) -> dict[int, int]:
    """Read marker, every model block, and the end marker, raw."""
    base = await find_sunspec_base(unit)
    blocks = await walk_model_chain(unit, base)

    image: dict[int, int] = {}
    marker = await unit.read_holding_registers(base, 2)
    image[base], image[base + 1] = marker[0], marker[1]

    end = base + 2
    for block in blocks:
        span = 2 + block.length
        for start in range(block.address, block.address + span, _CHUNK):
            count = min(_CHUNK, block.address + span - start)
            values = await unit.read_holding_registers(start, count)
            for offset, value in enumerate(values):
                image[start + offset] = value
        end = block.address + span
    image[end], image[end + 1] = END_MODEL_ID, 0
    return image


def format_report(device: KacoInverter) -> str:
    probe = device.probe
    lines = [
        f"Device:   {probe.manufacturer} {probe.model}",
        f"Serial:   {probe.serial}   Firmware: {probe.firmware}",
        f"SunSpec:  base {probe.base_address}, models "
        + ", ".join(f"{b.model_id}@{b.address}(len {b.length})" for b in probe.blocks),
        "",
    ]
    for name in _REPORT_FIELDS:
        value = getattr(device.inverter, name, None)
        lines.append(f"  {name:28s} {value}")
    return "\n".join(lines)


async def _run(host: str, port: int, unit_id: int, json_path: str | None) -> int:
    from modbus_connection.tmodbus import connect_tcp

    connection = await connect_tcp(host, port=port)
    try:
        unit = connection.for_unit(unit_id)
        probe = await KacoInverter.async_probe(unit)
        device = KacoInverter(unit, probe)
        await device.async_update()
        print(format_report(device))
        if json_path:
            image = await dump_registers(unit)
            with open(json_path, "w", encoding="utf-8") as fp:
                json.dump(
                    {"registers": {str(k): v for k, v in sorted(image.items())}},
                    fp,
                    indent=1,
                )
            print(f"\nRaw register image written to {json_path}")
    finally:
        await connection.close()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("host")
    parser.add_argument("--port", type=int, default=502)
    parser.add_argument("--unit", type=int, default=1)
    parser.add_argument("--json", dest="json_path", default=None)
    args = parser.parse_args(argv)
    return asyncio.run(_run(args.host, args.port, args.unit, args.json_path))


if __name__ == "__main__":
    sys.exit(main())
