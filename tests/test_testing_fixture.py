"""Guard against silent drift in the synthetic register fixture's layout."""

from kaco_modbus.testing import BLUEPLANET_86TL3_REGISTERS


def test_model_103_block_is_exactly_50_registers() -> None:
    data_addresses = set(range(40072, 40122))
    assert data_addresses <= BLUEPLANET_86TL3_REGISTERS.keys()
    assert len(data_addresses) == 50


def test_end_of_chain_marker_at_40122() -> None:
    assert BLUEPLANET_86TL3_REGISTERS[40122] == 0xFFFF
    assert BLUEPLANET_86TL3_REGISTERS[40123] == 0
