"""SunSpec inverter enumerations (model 101/102/103 St and Evt1 points)."""

from enum import IntEnum, IntFlag


class OperatingState(IntEnum):
    """SunSpec inverter operating state (St)."""

    OFF = 1
    SLEEPING = 2
    STARTING = 3
    MPPT = 4
    THROTTLED = 5
    SHUTTING_DOWN = 6
    FAULT = 7
    STANDBY = 8


class InverterEvent(IntFlag):
    """SunSpec inverter event flags (Evt1)."""

    GROUND_FAULT = 1 << 0
    DC_OVER_VOLTAGE = 1 << 1
    AC_DISCONNECT = 1 << 2
    DC_DISCONNECT = 1 << 3
    GRID_DISCONNECT = 1 << 4
    CABINET_OPEN = 1 << 5
    MANUAL_SHUTDOWN = 1 << 6
    OVER_TEMPERATURE = 1 << 7
    OVER_FREQUENCY = 1 << 8
    UNDER_FREQUENCY = 1 << 9
    AC_OVER_VOLTAGE = 1 << 10
    AC_UNDER_VOLTAGE = 1 << 11
    BLOWN_STRING_FUSE = 1 << 12
    UNDER_TEMPERATURE = 1 << 13
    MEMORY_LOSS = 1 << 14
    HW_TEST_FAILURE = 1 << 15
