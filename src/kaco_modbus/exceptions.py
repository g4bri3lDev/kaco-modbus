"""Exceptions raised by kaco_modbus."""


class KacoError(Exception):
    """Base error for kaco_modbus."""


class SunSpecNotFoundError(KacoError):
    """The device does not expose a SunSpec register map."""


class SunSpecModelMissingError(KacoError):
    """A required SunSpec model is absent from the device's chain."""
