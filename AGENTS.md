# kaco-modbus

A library for KACO solar inverters over SunSpec Modbus. Published to PyPI and
consumed by the `kaco` Home Assistant integration, which lives in its own
repository ([kaco-modbus-hass](https://github.com/g4bri3lDev/kaco-modbus-hass)).
Nothing here may import Home Assistant.

```bash
uv sync
uv run pytest              # 104 tests, coverage must stay >= 90%
uv run ruff check .
uv run ruff format .       # CI checks formatting; run it before pushing
uv run mypy src/ tests/    # strict
```

## The two rules that matter most

**`src/kaco_modbus/models.py` is generated. Never hand-edit it.** Regenerate:

```bash
uv run python -m modbus_connection.model.sunspec.generate \
  1 103 120 121 122 123 126 129 130 132 135 136 160 \
  -o src/kaco_modbus/models.py
```

Hand-deriving SunSpec register offsets is the single most reliable way to get
this wrong — it has already happened twice in this project, both times
producing plausible-looking nonsense. Field offsets in the generated code are
relative to the model header and already count its two registers, so an
absolute address is `model.address + offset` with no further arithmetic.

**The library never opens a connection.** Every entry point takes a
`ModbusUnit`; the caller owns the socket and picks the backend. There is
deliberately no backend extra in the runtime dependencies — pinning one would
force that choice on every consumer.

## Only SunSpec model 103

The generator list above covers one inverter model on purpose. KACO's entire
current range is three-phase (`NX3`, `TL3`, `NH3`, down to the 3 kW blueplanet
3.0 NX3 M2), so the single- and split-phase blocks 101/102 could never bind.
The float models 111/112/113 are duplicates rather than alternatives — this
firmware publishes 113 alongside 103 with identical values, verified field by
field, and 103 costs 52 registers a poll against 113's 62.

If a single-phase or float-only KACO ever appears, regenerate with the extra
IDs and turn `INVERTER_MODEL_ID` back into a preference ordering.

## Device behaviour you will otherwise misread

`docs/quirks.md` is the authoritative list and is pinned by tests. The two
that bite hardest:

**It lies at night rather than going quiet.** Unlike SolarEdge or Sofar, a
KACO keeps answering Modbus after dark but parks the registers it is no longer
measuring at zero — not at the "not implemented" sentinel. So it reports 0 Hz
and 0 V for a live grid, 0 °C for a warm cabinet, and a power factor of 1.00
with no current flowing. `KacoInverter` withholds those: `frequency`,
`phase_voltages`, `temperature`, `power_factor` and `string_temperature`
return `None` unless `is_running`. The gate is the **operating state, not the
value**, so a genuine 0 °C in winter still reports. Power, current and energy
are not withheld — zero is the truth for those.

**One Modbus client at a time.** A second connection is met with `Connection
reset by peer`, so `kaco-query` and `kaco-status` cannot run while Home
Assistant is polling the same inverter.

## Testing

Both fixtures in `src/kaco_modbus/testing.py` are real register images
captured from a blueplanet 8.6 TL3 INT — `BLUEPLANET_86TL3` while producing,
`BLUEPLANET_86TL3_ASLEEP` after dark. They ship with the package so the Home
Assistant integration can reuse them. The serial number is anonymised to
`8.6TL00000000`; keep it that way, a real one identifies someone's hardware.

`modbus-connection` registers a pytest plugin, so `mock_modbus_unit` and
`mock_modbus_connection` need no conftest wiring.

## Releasing

release-please, driven by conventional commits. Do not edit `__version__` or
`.release-please-manifest.json` by hand — the release PR does that, and
merging it tags, publishes to PyPI via trusted publishing, and writes the
changelog. `feat:` and `fix:` reach the changelog; `chore:`, `ci:`, `style:`
and `test:` are hidden.

## Writing to the inverter

Writes are confined to SunSpec model 123 (immediate controls). The volt-var,
volt-watt and ride-through curve models are decoded read-only on purpose:
changing them can breach an interconnection agreement.

Setpoints on this hardware carry a revert timer — the inverter drops back to
default after 300 s unless the value is rewritten. Each setter tries to clear
that timer and reports through `setpoints_held` whether the device allowed it.
**This has never been verified against real hardware**; it needs a deliberate
curtailment in daylight.

Never retry a write. `modbus-connection` performs no automatic retries by
design; retrying a read is fine, but a retried write must first read back to
see whether the first one landed.
