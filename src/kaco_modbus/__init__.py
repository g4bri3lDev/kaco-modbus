"""Read and control KACO solar inverters over SunSpec Modbus.

The library takes a ``ModbusUnit`` and never opens a connection of its own,
so the caller keeps ownership of the socket and picks the backend.
"""

from __future__ import annotations

# Re-exported because a consumer must handle them: SunSpecMapShiftError is not
# a ModbusError, so it needs its own except clause, and a caller that misses it
# will keep reading a map that has moved underneath it.
from modbus_connection.model.sunspec import SunSpecError, SunSpecMapShiftError

from .const import MANUFACTURER
from .device import DeviceInfo, KacoInverter, UpdateReport
from .exceptions import (
    KacoError,
    ModelMissingError,
    NotAKacoInverterError,
    SunSpecNotFoundError,
)
from .models import (
    Conn,
    DERTyp,
    Event1,
    MpptModuleOperatingState,
    OperatingState,
    OutPFSetEna,
    VArPctEna,
    VArPctMod,
    WMaxLimEna,
)

__version__ = "1.0.1"  # x-release-please-version

__all__ = [
    "MANUFACTURER",
    "Conn",
    "DERTyp",
    "DeviceInfo",
    "Event1",
    "KacoError",
    "KacoInverter",
    "ModelMissingError",
    "MpptModuleOperatingState",
    "NotAKacoInverterError",
    "OperatingState",
    "OutPFSetEna",
    "SunSpecError",
    "SunSpecMapShiftError",
    "SunSpecNotFoundError",
    "UpdateReport",
    "VArPctEna",
    "VArPctMod",
    "WMaxLimEna",
    "__version__",
]
