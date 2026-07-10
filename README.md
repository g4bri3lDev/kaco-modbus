# kaco-modbus

Read a KACO blueplanet inverter over SunSpec Modbus TCP. This library discovers the device's register layout at runtime using SunSpec, then provides typed access to identity and live data. Built on the [modbus-connection](https://home-assistant-libs.github.io/modbus-connection/) library, it is the core device integration behind the [kaco Home Assistant integration](https://github.com/glackermeier/kaco-hass).

## Installation

```bash
pip install kaco-modbus
```

For the `dump` CLI tool (below), install with the `cli` extra:

```bash
pip install "kaco-modbus[cli]"
```

Note: The package is not yet published to PyPI; for now, install from the GitHub repository or build locally with `uv`.

## Usage

```python
import asyncio
from modbus_connection.tmodbus import connect_tcp
from kaco_modbus import KacoInverter

async def main():
    connection = await connect_tcp("192.168.1.50", port=502)
    try:
        unit = connection.for_unit(1)
        probe = await KacoInverter.async_probe(unit)
        device = KacoInverter(unit, probe)
        await device.async_update()
        
        print(f"AC Power: {device.inverter.ac_power} W")
        print(f"Energy Total: {device.inverter.energy_total} kWh")
        print(f"State: {device.inverter.state}")
    finally:
        await connection.close()

asyncio.run(main())
```

## Dump CLI

The `dump` tool reads your inverter's complete SunSpec register image. This is useful for:
- Capturing on-device ground-truth data for test fixtures
- Verifying Modbus connectivity
- Debugging SunSpec layout issues

Run it directly on the inverter's LAN:

```bash
uv run --extra cli python -m kaco_modbus.dump 192.168.1.50 --json dump.json
```

The command prints live data (AC power, energy, state, temperatures) and optionally saves the raw register image as JSON for analysis.

**Important:** Modbus TCP must be enabled on the inverter. In the inverter's menu (local GUI or WebGUI), navigate to **MODBUS / SunSpec protocol** and enable it (default port 502). The inverter's Modbus server is single-threaded, so sharing a connection across multiple clients (via modbus-connection) is more reliable than opening separate TCP connections.

## Supported Devices

| Device Series | Models | SunSpec IDs | Firmware |
|---|---|---|---|
| KACO blueplanet TL1 | TL1.5 – TL8.6 | 1, 101/102/103 | ≥ V2.02 |
| KACO blueplanet TL3 | TL3.0 – TL10.0 | 1, 101/102/103 | ≥ V2.02 |
| KACO Powador TL3 | TL3.0 – TL15.0 | 1, 101/102/103 | ≥ V2.02 |

Data based on KACO's "MODBUS Protocol Application Note, Tx1 and Tx3 Series" (v180730) and SunSpec specs. Other firmware versions and models may expose additional SunSpec models (e.g., 112, 113, 160); the library skips unknown models and will discover them in future versions.

## Development

Clone and set up:

```bash
git clone https://github.com/glackermeier/kaco-modbus
cd kaco-modbus
uv sync
```

Run tests, type checks, and lint:

```bash
uv run pytest -v
uv run mypy
uv run ruff check
uv run ruff format --check
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for a detailed explanation of the library's design, module responsibilities, and layering.

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.
