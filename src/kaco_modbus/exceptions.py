"""Errors raised by this library."""

from __future__ import annotations


class KacoError(Exception):
    """Base class for every error this library raises of its own accord.

    Modbus and SunSpec failures are *not* wrapped: ``ModbusError`` and
    ``SunSpecMapShiftError`` propagate as themselves, so a consumer keeps the
    neutral error hierarchy it already handles.
    """


class SunSpecNotFoundError(KacoError):
    """No SunSpec marker was found at any of the standard base addresses.

    The device answered, but it is not a SunSpec device — or its map lives
    somewhere non-standard.
    """


class ModelMissingError(KacoError):
    """The device does not expose a SunSpec model this operation needs.

    Raised when asking for a capability the device never advertised, such as
    curtailment on an inverter without model 123.
    """
