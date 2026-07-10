"""Shared fixtures: seed the mock unit with a synthetic blueplanet."""

from kaco_modbus.testing import BLUEPLANET_86TL3_REGISTERS


def seed_device(unit, registers=BLUEPLANET_86TL3_REGISTERS) -> None:
    for address, value in registers.items():
        unit.holding[address] = value
