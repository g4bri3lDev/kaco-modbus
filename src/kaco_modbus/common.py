"""SunSpec Model 1 — manufacturer identity."""

from modbus_connection.model import Component
from modbus_connection.model.sunspec import string, uint16

MODEL_ID = 1


class Common(Component):
    """SunSpec common model; addresses relative to the model's ID register."""

    manufacturer = string(2, 16)  # Mn
    model = string(18, 16)  # Md
    options = string(34, 8)  # Opt
    version = string(42, 8)  # Vr
    serial = string(50, 16)  # SN
    device_address = uint16(66)  # DA
