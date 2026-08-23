# Device quirks

Everything here was read from a real **KACO blueplanet 8.6 TL3 INT** on firmware
**V5.53**, and is pinned by tests in `tests/test_readings.py` against the captured
register image in `kaco_modbus.testing`. Other models and firmware may differ.

## Fields the firmware does not implement

SunSpec has a sentinel per type for "not implemented", and this library decodes all
of them to `None`. Do not surface these as values:

| Field | Model | Note |
|---|---|---|
| `pp_vph_ab`, `pp_vph_bc`, `pp_vph_ca` | 103 | Line-to-line voltages, despite being a 3-phase unit. Only phase-to-neutral (`ph_vph_a/b/c`) is real. |
| `tmp_snk`, `tmp_trns`, `tmp_ot` | 103 | Only `tmp_cab` (cabinet) is a real sensor. |
| `evt_vnd1`–`evt_vnd4` | 103 | Vendor event bitfields are all `0xFFFFFFFF`. |
| `a_rtg` | 120 | No current rating. |
| `dcwh` | 160 | **No per-string lifetime energy.** Use the inverter-level `wh`. |
| `dc_st`, `dc_evt` | 160 | No per-string operating state or events. |
| `tms_per` | 160 | No timestamp period. |
| most of model 122 | 122 | `act_wh`, `ris`, `rt_st`, `st_act_ctl` and the `act_v_arh_*` accumulators are all absent. |
| `v_ref_ofs`, `v_max`, `v_min`, `w_gra`, `pf_min_*` | 121 | Absent; `w_max`, `v_ref` and `va_max` are real. |

## Fields that return wrong values

These read as *something*, which is worse than absent — they must be ignored explicitly.

- **`pf_rtg_q1` / `pf_rtg_q4` (model 120)** decode to `-14.656`. A power factor is the
  cosine of an angle and cannot leave `[-1, 1]`, so the register is junk.
- **`ecp_conn` (model 122)** reports `DISCONNECTED` while the inverter is exporting
  power. Do not use it as a grid-connected indicator — use `controls.conn` (model 123)
  or the operating state `st` instead. Note that SunSpec really does define bit 0 of
  `ECPConn` as `DISCONNECTED`, so this is the device lying, not a decode error.
- **`tm_src` (model 122)** returns a truncated, null-embedded fragment of the
  manufacturer string (`'KACO n\x00e'`) rather than a time source.
- **`tmp` on MPPT 1 (model 160)** reads `0` while MPPT 0 reports a plausible
  temperature. The second string appears to have no sensor, and `0` is not a sentinel,
  so it cannot be distinguished from a real reading. Treat per-string temperature as
  available on the first string only.

## Only model 103 is supported

SunSpec defines six inverter blocks — 101/102/103 for single-, split- and three-phase
with scale factors, and 111/112/113 as their float equivalents. This library generates
and binds **only 103**, on two pieces of evidence:

- **KACO's entire range is three-phase.** Every current model is `NX3`, `TL3` or `NH3`,
  down to the smallest residential unit, the 3 kW *blueplanet 3.0 NX3 M2*, which KACO
  describes as a "3-phase string inverter". There is no `TL1` or `NX1` in the catalogue,
  so 101 and 102 could never bind.
- **The float models are duplicates, not alternatives.** This device publishes 113
  alongside 103 with identical values, so a float fallback is unreachable.

If KACO ever ships a single-phase or float-only inverter, regenerate `models.py` with the
extra model IDs and turn `INVERTER_MODEL_ID` back into a preference ordering.

## Behaviour

### At night it lies rather than going quiet

Most inverters stop answering Modbus after dark — SolarEdge and Sofar both do, so
integrations for them simply go unavailable. **A KACO does not.** It stays connected and
answers normally in the `SLEEPING` state, but parks the registers it is no longer
measuring at **zero**, not at the "not implemented" sentinel. Captured from the hardware
on a warm August night:

| Reading | Asleep | Truth |
|---|---|---|
| `hz` | `0.0 Hz` | the grid is still live at ~50 Hz |
| `ph_vph_a/b/c` | `0.0 V` | the mains is still at ~230 V |
| `tmp_cab` | `0.0 °C` | it was 46.9 °C that afternoon |
| `tmp` (per string) | `0` | — |
| `pf` | `1.00` | undefined with no current flowing |

Left alone these look plausible, so they would show a grid outage every night and drag
statistics down with zeros. `KacoInverter` therefore withholds them —
:attr:`frequency`, :attr:`phase_voltages`, :attr:`temperature`, :attr:`power_factor`
and :meth:`string_temperature` return `None` unless :attr:`is_running`.

The gate is the **operating state**, not the value, so a genuine 0 °C in winter is still
reported honestly.

What is *not* withheld: power, current and energy. Zero really is the right answer for
those, and `wh` keeps counting.

### Model 160 raises CABINET_OPEN every night

`mppt.evt` reads `32` (`GlobalEvents.CABINET_OPEN`) whenever the inverter is asleep, and
`0` while producing. The cabinet is not open. Do not surface model 160's event bitfield
as an alarm.

### Only one Modbus client at a time

The inverter accepts a **single concurrent TCP connection**. A second one is met with
`Connection reset by peer`, so `kaco-query` and `kaco-status` cannot be used while Home
Assistant is polling — stop the integration first, or read through its diagnostics
download instead.

### The unit ID is ignored

The inverter answers identically on unit IDs 1, 3, 126 and 247 — it is TCP-native and
does not decode the field. The default of 1 works. A KACO reached through an
RS485-to-TCP gateway *will* care, which is why the ID remains configurable.

### Setpoints revert after 300 seconds

`w_max_lim_pct_rvrt_tms`, `out_pf_set_rvrt_tms` and `v_ar_pct_rvrt_tms` all read `300`.
A setpoint written without clearing its timer is silently dropped after five minutes.

Every control setter in this library therefore tries to write the matching revert timer
to `0` first, which this firmware accepts — so a limit holds indefinitely. If a device
refuses, the setter does not fail: it records `setpoints_held = False`, and
`revert_seconds` then tells the caller how long it has to rewrite the value.

### Frequency must be read unsigned

At 50 Hz, `hz` holds `49987`, which is above `0x8000`. Decoded as a signed word it
becomes `-15.548`. The generated model gets this right; hand-rolled register maps
routinely do not.

### The model chain

Discovered at base address **40000**; probing `0` and `50000` returns *illegal data
address* rather than hanging, so probing all three costs almost nothing.

```
1, 103, 113, 120, 121, 122, 123, 126, 129, 130, 132, 135, 136, 160, 64204
```

- Both **103** (integer + scale factor) and **113** (float) are present and carry the
  **same measurements** — verified field by field against the live device, agreeing to
  within the integer model's rounding. This library binds 103 and ignores 113: the float
  model is a redundant duplicate rather than an alternative, and it spans 62 registers
  against 103's 52.
- **64204** is a KACO vendor block, 8 registers, with no definition in the
  [SunSpec model repository](https://github.com/sunspec/models). It is never decoded —
  `kaco-query --raw` will show its registers.
- **126** (volt-var) does implement `n_crv` (4) and `n_pt` (10), so its curves are
  introspectable. This library decodes the fixed header only and does not write curves.
- **129, 130, 135, 136** are the low/high voltage and frequency ride-through curves, and
  **132** is volt-watt. These are grid-code configuration. They are bound and readable
  through `async_update_curves()`, but never polled and never written: changing them can
  breach an interconnection agreement.
