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


class NotAKacoInverterError(KacoError):
    """The device is a SunSpec inverter, but not a KACO one.

    SunSpec is a shared specification, but each manufacturer layers its own
    quirks on top — which is why per-vendor libraries exist at all rather than
    one generic SunSpec one. Everything this library knows beyond the bare
    register map is KACO-specific: that this firmware parks unmeasured
    registers at zero after dark rather than at the not-implemented sentinel,
    that model 113 duplicates 103 and can be skipped, that 64204 is a vendor
    block. Applied to another vendor's inverter, those assumptions do not hold
    and the readings would be quietly wrong rather than obviously absent.

    Model 1's ``Mn`` is what tells the two apart.
    """


class ModelMissingError(KacoError):
    """The device does not expose a SunSpec model this operation needs.

    Raised when asking for a capability the device never advertised, such as
    curtailment on an inverter without model 123.
    """
