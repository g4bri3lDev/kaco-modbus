"""Constants describing where a KACO inverter keeps things."""

from __future__ import annotations

MANUFACTURER = "KACO new energy"

# Where a SunSpec map may start, in the order worth trying. 40000 is what
# every KACO tested uses; the other two are the remaining locations the
# specification allows. Probing a wrong one is cheap — the device answers
# "illegal data address" rather than hanging.
SUNSPEC_BASE_ADDRESSES = (40000, 0, 50000)

# The inverter block. Model 103 is the three-phase, integer-plus-scale-factor
# inverter, and it is the only one KACO needs:
#
#   * Every current KACO inverter is three-phase — the whole range is NX3, TL3
#     or NH3, down to the 3 kW residential blueplanet 3.0 NX3 M2. There is no
#     TL1 or NX1, so the single- and split-phase models (101, 102) would never
#     bind.
#   * The float model 113 is published *alongside* 103 carrying identical
#     values, verified field by field against hardware. It is a duplicate
#     rather than an alternative, and it spans 62 registers against 103's 52.
#
# If KACO ever ships a single-phase or float-only inverter, regenerate
# models.py with the extra model IDs and turn this back into a preference
# ordering.
INVERTER_MODEL_ID = 103

# Components polled every cycle, and those polled rarely. Order is poll order.
READINGS = ("inverter", "mppt", "status")
SETTINGS = ("nameplate", "settings", "controls", "volt_var")

# The vendor block this firmware advertises. There is no public definition for
# it, so it is reported as raw registers and never decoded.
VENDOR_MODEL_ID = 64204
