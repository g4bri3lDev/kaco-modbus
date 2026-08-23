"""Shared fixtures.

``mock_modbus_unit`` and ``mock_modbus_connection`` come from the pytest
plugin ``modbus-connection`` registers, so they need no wiring here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from kaco_modbus import KacoInverter
from kaco_modbus.models import InverterThreePhase
from kaco_modbus.testing import BLUEPLANET_86TL3

if TYPE_CHECKING:
    from modbus_connection.mock import MockModbusUnit


@pytest.fixture
def inverter_unit(mock_modbus_unit: MockModbusUnit) -> MockModbusUnit:
    """A mock unit loaded with the real 8.6 TL3 register image."""
    mock_modbus_unit.load_raw({"holding": BLUEPLANET_86TL3})
    return mock_modbus_unit


@pytest.fixture
async def inverter(inverter_unit: MockModbusUnit) -> KacoInverter:
    """A set-up inverter, already polled once."""
    device = KacoInverter(inverter_unit)
    await device.async_update()
    return device


@pytest.fixture
def ac(inverter: KacoInverter) -> InverterThreePhase:
    """The inverter block — always SunSpec model 103, the only one KACO ships."""
    assert inverter.inverter is not None
    return inverter.inverter
