# kaco-modbus

Read and control KACO solar inverters over SunSpec Modbus.

Built on [`modbus-connection`](https://github.com/home-assistant-libs/modbus-connection).
The library never opens a connection of its own: you hand it a `ModbusUnit` and keep
ownership of the socket. It contains no Home Assistant imports.

Developed against a **KACO blueplanet 8.6 TL3 INT** (firmware V5.53). It is driven by
SunSpec discovery rather than a fixed register map, so it should work with any KACO
inverter that exposes SunSpec over Modbus TCP — KACO's whole current range is
three-phase, which is what this targets. Older *Powador* units that speak KACO's
proprietary RS485 ASCII protocol are **not** supported; that is a different protocol.

## Install

```bash
pip install kaco-modbus
```

You also need a Modbus backend, chosen by you rather than by this library:

```bash
pip install "modbus-connection[tmodbus]"   # or [pymodbus]
```

## Use

```python
import asyncio

from modbus_connection import ModbusTcpParams
from modbus_connection.tmodbus import ModbusConnection

from kaco_modbus import KacoInverter


async def main() -> None:
    connection = ModbusConnection(ModbusTcpParams(host="192.168.0.155"))
    try:
        inverter = KacoInverter(connection.for_unit(1))
        await inverter.async_update()

        print(inverter.info.model, inverter.info.serial_number)
        print(inverter.inverter.w, "W")  # AC power, scale factor applied
        for string in inverter.strings:
            print(string.id_str, string.dcw, "W")  # per MPPT string
    finally:
        await connection.close()


asyncio.run(main())
```

`async_update()` establishes first that the device really is a KACO, raising
`NotAKacoInverterError` if not. SunSpec is a shared specification, so another
vendor's inverter answers the same models at the same addresses — but
everything this library knows beyond the bare register map is KACO-specific
(see [`docs/quirks.md`](docs/quirks.md)), and applied elsewhere it would report
plausible nonsense rather than fail outright. The check is SunSpec model 1's
manufacturer, matched as a prefix.

## Command line

```bash
pip install "kaco-modbus[cli]"
```

Two tools, for two different readers.

### `kaco-status` — what the inverter is doing

```bash
kaco-status 192.168.0.155
kaco-status 192.168.0.155 --watch      # live, refreshing every 5 s
```

Plain language, real units, and a judgement on each grid reading. No SunSpec
vocabulary: the operating state reads *"Producing power"*, not `MPPT`.

```
╭────────────────────── blueplanet 8.6 TL3 INT ───────────────────────╮
│  ● Producing power                   KACO new energy · 8.60 kW rated│
│                                                                     │
│  1.18 kW  ████░░░░░░░░░░░░░░░░░░░░░░  14% of capacity                │
│                                                                     │
│  ╭─────── Solar panels ────────╮  ╭────────── Grid ──────────╮      │
│  │  String    Voltage   Power  │  │  Phase 1   230.1 V normal│      │
│  │  String 1    344 V   270 W  │  │  Frequency 50.07 Hz normal      │
│  │  String 2    537 V   460 W  │  │  Power factor 1.00       │      │
│  ╰─────────────────────────────╯  ╰──────────────────────────╯      │
│                                                                     │
│    Generated all-time    Conversion efficiency     Temperature      │
│        12.19 MWh                 98.0%                46 °C         │
╰──────────────── 8.6TL00000000 · firmware V5.53 ─────────────────────╯
```

It withholds numbers it cannot stand behind. Conversion efficiency is blank below
1 kW, because the inverter reports power in 10 W steps and the rounding would show a
false 100 %.

### `kaco-query` — every register, for developers

```bash
kaco-query 192.168.0.155
kaco-query 192.168.0.155 --raw     # plus an undecoded register dump
```

Prints the discovered SunSpec model chain and every decoded field under its real
SunSpec name, with `—` for the ones this firmware does not implement.

### `kaco-limit` — supervised power limit tests

```bash
kaco-limit 192.168.0.155 show
kaco-limit 192.168.0.155 set 50 --revert 300 --watch 420 --yes-write-to-inverter
kaco-limit 192.168.0.155 resend --revert 300 --yes-write-to-inverter
kaco-limit 192.168.0.155 clear --yes-write-to-inverter
```

Writes to the inverter's grid control (see [Control](#control)), for checking on hardware
what the setters do. Nothing is sent without `--yes-write-to-inverter`, and an inverter
that ignores the writes is reported.

## At night

A KACO stays on Modbus after dark rather than going silent, but parks the readings it
is no longer taking at zero — reporting 0 Hz and 0 V for a grid that is plainly still
live. The device object withholds those rather than passing them on:

```python
inverter.is_running  # False while asleep
inverter.frequency  # None unless running
inverter.phase_voltages  # (None, None, None) unless running
inverter.temperature  # None unless running
inverter.power_factor  # None unless running
```

Power, current and energy are *not* withheld — zero is genuinely correct for those.
See [`docs/quirks.md`](docs/quirks.md).

> [!NOTE]
> The inverter accepts only **one Modbus client at a time**, so the CLIs cannot be used
> while Home Assistant is polling it.

## Control

Writes are limited to SunSpec model 123 (immediate controls):

```python
await inverter.async_set_power_limit(50.0, revert_seconds=3600)  # curtail to 50 % for an hour
await inverter.async_resend_power_limit(3600)  # still in force? send it again
await inverter.async_clear_power_limit()
```

> [!WARNING]
> These write to a live grid-tied inverter. Curtailment and disconnection can take your
> plant off the grid and may be subject to your interconnection agreement. The volt-var,
> volt-watt and ride-through curve models are deliberately decoded read-only.

The inverter drops a power limit `revert_seconds` after it was last written, and only a
write restarts that period, so a caller keeping a limit has to keep resending it. A limit
cannot be held without resending: the firmware refuses a period of `0`.

Writing needs **Modbus TCP Schreibzugriff** (write access) enabled in the inverter's web
interface. With it off, the inverter acknowledges every write and ignores it, which the
setters report as `SetpointRejectedError`. See [`docs/quirks.md`](docs/quirks.md).

## License

Apache-2.0
