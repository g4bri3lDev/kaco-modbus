"""Replay the register image captured from a real inverter.

Captured 2026-07-11 with ``python -m kaco_modbus.dump`` from a
blueplanet 8.6 TL3 INT running firmware V5.53. Identity assertions are
exact; live electrical values are asserted as plausible ranges since
they reflect one arbitrary moment of production.
"""

from pathlib import Path

from kaco_modbus import KacoInverter, OperatingState
from kaco_modbus.testing import registers_from_dump

REFERENCE = Path(__file__).parent / "reference" / "blueplanet_86tl3.json"


async def test_real_device_image(mock_modbus_unit):
    for address, value in registers_from_dump(REFERENCE).items():
        mock_modbus_unit.holding[address] = value

    probe = await KacoInverter.async_probe(mock_modbus_unit)
    assert probe.manufacturer == "KACO new energy"
    assert probe.model == "blueplanet 8.6 TL3 INT"
    assert probe.serial == "8.6TL01700000"
    assert probe.firmware == "V5.53"
    assert probe.base_address == 40000
    assert [block.model_id for block in probe.blocks] == [
        1, 103, 113, 120, 121, 122, 123, 126,
        129, 130, 132, 135, 136, 160, 64204,
    ]  # fmt: skip

    inverter_block = probe.block_for(101, 102, 103)
    assert inverter_block is not None
    assert inverter_block.address == 40070  # int model preferred over float 113

    device = KacoInverter(mock_modbus_unit, probe)
    await device.async_update()

    inv = device.inverter
    assert inv.state is OperatingState.MPPT
    assert inv.ac_power is not None and 0 < inv.ac_power < 8_500
    assert inv.energy_total is not None and inv.energy_total > 10_000_000
    assert inv.frequency is not None and 49.0 < inv.frequency < 51.0
    assert inv.dc_voltage is not None and 100 < inv.dc_voltage < 1_000
    for phase in (inv.voltage_phase_a, inv.voltage_phase_b, inv.voltage_phase_c):
        assert phase is not None and 200 < phase < 260
    # Points this unit does not implement decode to None, not garbage.
    assert inv.voltage_ab is None
    assert inv.temperature_heatsink is None
