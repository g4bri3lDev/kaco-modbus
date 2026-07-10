# Architecture

How the KACO blueplanet integration is layered, what each piece does, and
where the interfaces are.

## The stack

    ┌──────────────────────────────────────────────────────────┐
    │  Home Assistant UI (sensors, Energy dashboard)           │
    ├──────────────────────────────────────────────────────────┤
    │  kaco integration (custom_components/kaco)               │
    │  config_flow · coordinator · entity · sensor             │
    ├────────────────────────────┬─────────────────────────────┤
    │  kaco-modbus (this repo)   │  modbus_connection          │
    │  KacoInverter · discovery  │  integration (shared owner  │
    │  Common · Inverter · enums │  of the TCP connection)     │
    ├────────────────────────────┴─────────────────────────────┤
    │  modbus-connection library                               │
    │  ModbusConnection/ModbusUnit protocols · Component model │
    │  · sunspec fields · pymodbus/tmodbus backends · mock     │
    ├──────────────────────────────────────────────────────────┤
    │  Modbus TCP, port 502  →  KACO blueplanet inverter (LAN) │
    └──────────────────────────────────────────────────────────┘

Two hard boundaries follow from Home Assistant core rules:

1. **This library never opens a connection.** Every entry point takes a
   `ModbusUnit` — a stateless handle for one unit id on a connection someone
   else owns. In HA that owner is the shared `modbus_connection` integration;
   in the dump CLI it is the CLI's own `connect_tcp` call; in tests it is the
   in-memory mock. Because only the unit protocol is used, all three run the
   same code.
2. **This library never imports Home Assistant.** All HA-specific wiring
   lives in the separate `kaco` integration, which imports this package.

## Why SunSpec discovery instead of a fixed register map

KACO (like most PV vendors) implements the SunSpec information model: a
`"SunS"` marker at a well-known base address, then a chain of self-describing
model blocks, each starting with `[model id, data length]` and ending with a
sentinel id 0xFFFF. Firmware versions differ in *which* models they expose
(V2.02: 1/102/103; V4.00 adds 112/113/160 and control models) and models can
sit at different offsets per device. Walking the chain at runtime means one
codebase handles every blueplanet TL1/TL3/Powador TL3 variant — and unknown
models are simply skipped instead of breaking.

## Module responsibilities (kaco_modbus)

| Module         | Responsibility | Interface |
|----------------|----------------|-----------|
| `discovery.py` | Find the map, walk the chain | `find_sunspec_base(unit) -> int`; `walk_model_chain(unit, base) -> tuple[ModelBlock, ...]` |
| `common.py`    | SunSpec Model 1 register map | `Common(unit, base_offset=...)`: `.manufacturer/.model/.options/.version/.serial` |
| `inverter.py`  | SunSpec Model 101/102/103 map | `Inverter(unit, base_offset=...)`: typed live values, `.energy_total` property |
| `enums.py`     | SunSpec St / Evt1 vocabularies | `OperatingState(IntEnum)`, `InverterEvent(IntFlag)` |
| `kaco.py`      | The one public entrypoint | `KacoInverter.async_probe(unit)`, `KacoInverter(unit, probe)`, `.async_update()` |
| `exceptions.py`| Failure vocabulary | `KacoError` ← `SunSpecNotFoundError`, `SunSpecModelMissingError` |
| `testing.py`   | Synthetic register image | `BLUEPLANET_86TL3_REGISTERS: dict[int, int]` (shared by both repos' tests) |
| `dump.py`      | Ground-truth CLI | `python -m kaco_modbus.dump <host> --json out.json` |

Field declarations use `modbus_connection.model.sunspec` factories, so SunSpec
semantics (scale-factor registers, "unimplemented" sentinels → `None`,
big-endian word order) are handled below this library. Components declare
addresses *relative to their model's ID register* and are placed with
`base_offset=<discovered address>` — the same class works wherever a model
lands on a given firmware.

One quirk: SunSpec accumulators (`WH`) carry a scale factor, but the
`acc32` factory takes no `scale_register`; `Inverter` therefore declares the
raw accumulator + `sunssf` privately and exposes `energy_total` as a property.

## The two-phase lifecycle

**Probe (setup time, runs once):**
`async_probe(unit)` → find base → walk chain → read Model 1 → frozen
`KacoProbe(manufacturer, model, options, firmware, serial, base_address,
blocks)`. The config flow uses it to validate the connection and derive the
unique id (serial); `async_setup_entry` re-probes and feeds the result to the
constructor. Nothing about layout is persisted — the device is re-discovered
on every HA start, so firmware updates that move blocks cannot strand stale
offsets.

**Poll (every SCAN_INTERVAL):**
`KacoInverter.async_update()` → `ComponentGroup.async_update()` → a *pooled*
read plan (computed once, cached) fetches Model 1 + Model 103 in a handful of
FC03 block reads instead of ~30 point reads. Entities then read plain Python
attributes; no I/O happens on attribute access.

## The HA integration (custom_components/kaco)

- `provider.py` — resolves `async_get_unit` from the `modbus_connection`
  provider (custom component today, HA core once released). This is the only
  place the provider is imported.
- `config_flow.py` — one step: pick an existing Modbus Connection entry +
  unit id (default 1). Validates by probing; aborts on duplicate serial. The
  entry stores **only** `{connection_entry_id, unit_id}` — host/port live in
  the shared connection entry, so several integrations can share one socket
  (the inverter's Modbus server accepts few clients; sharing is the point of
  the new framework).
- `coordinator.py` — `DataUpdateCoordinator[KacoInverter]`, 10 s interval.
  `ModbusError` → `UpdateFailed` (entities go unavailable); a failure after a
  previously good refresh schedules an entry reload to re-acquire the unit.
- `__init__.py` — glue: get unit → probe → build device → first refresh →
  register `on_connection_lost` → forward to the sensor platform.
- `entity.py` / `sensor.py` — declarative `SensorEntityDescription` table;
  each sensor is `value_fn(coordinator.device)` over a library attribute.
  `lifetime_energy` uses `state_class=TOTAL_INCREASING` (Energy dashboard),
  the state sensor is a translated enum, per-phase/DC detail sensors are
  registry-disabled by default, temperatures are diagnostic-category.

## Error model

| Failure | Where handled | Result |
|---------|--------------|--------|
| No SunSpec map / Modbus disabled | `SunSpecNotFoundError` from probe | config flow `cannot_connect`; setup `ConfigEntryNotReady` (HA retries) |
| Required model missing | `SunSpecModelMissingError` from constructor | same as above |
| Poll timeout / device rejects read | `ModbusError` in coordinator | `UpdateFailed` → entities unavailable until next success |
| TCP link drops | `unit.on_connection_lost` callback | entry reload; `modbus_connection`'s own retry re-opens the socket |

## Testing strategy

The mock backend (`modbus_connection.mock`, a pytest plugin) implements the
same `ModbusUnit` protocol, so the full stack — discovery, pooled reads,
scaling, sentinels — is exercised with no hardware. `kaco_modbus.testing`
ships a synthetic register image of a blueplanet 8.6 TL3 built from the
SunSpec spec + KACO's application note; both the library tests and the HA
integration tests (which stub the provider and run a real config flow +
sensor platform via pytest-homeassistant-custom-component) seed the mock from
it. `tests/reference/blueplanet_86tl3.json` will be captured from the real
inverter with the dump CLI (`python -m kaco_modbus.dump --json`) and loaded
back into the same `dict[int, int]` shape via
`kaco_modbus.testing.registers_from_dump`, then replayed the same way once
it exists. Until it's captured on-site, the synthetic image above is the
canonical fixture.

## References

- KACO "MODBUS Protocol Application Note, Tx1 and Tx3 Series" (v180730):
  register map start 40001 (wire 40000), enabling via GUI/WebGUI, FC03/06/16,
  firmware/model matrix. Mirror:
  https://forum.iobroker.net/assets/uploads/files/1620202325160-apl_modbus-protocol_de_180730.pdf
- KACO SunSpec-Information-Model-Reference(.xlsx / -Kaco.xlsx) — per-firmware
  model/register lists, kaco-newenergy.com → Downloads.
- SunSpec specs: sunspec.org (Common Models v1.5, Inverter Models v1.1).
- modbus-connection docs: https://home-assistant-libs.github.io/modbus-connection/
- Reference implementations: github.com/Tom-Bom-badil/trovis-modbus (+ -hass).
