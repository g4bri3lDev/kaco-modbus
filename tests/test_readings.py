"""Decoding a poll, including every quirk this firmware actually shows."""

from __future__ import annotations

from typing import TYPE_CHECKING

from kaco_modbus import OperatingState

if TYPE_CHECKING:
    from kaco_modbus import KacoInverter
    from kaco_modbus.models import InverterThreePhase


async def test_ac_measurements(ac: InverterThreePhase) -> None:
    """Scale factors are applied, so callers get real units."""
    assert ac.w == 1000  # W_SF = 1, so the raw 100 means 1000 W
    assert ac.va == 990
    assert ac.pf == 1.0
    assert ac.a == 4.84
    assert (ac.aph_a, ac.aph_b, ac.aph_c) == (1.64, 1.62, 1.57)
    assert (ac.ph_vph_a, ac.ph_vph_b, ac.ph_vph_c) == (226.5, 228.2, 227.8)


async def test_frequency_is_unsigned(ac: InverterThreePhase) -> None:
    """Hz sits above 0x8000 at 50 Hz. Read as a signed word it decodes to
    nonsense (-15.5), which is how this goes wrong when hand-rolled.
    """
    assert ac.hz == 49.944
    assert 49.0 < ac.hz < 51.0


async def test_dc_side(ac: InverterThreePhase) -> None:
    assert ac.dcw == 1020
    assert ac.dcv == 443.7
    assert ac.dca == 2.3
    # DC must exceed AC: the difference is conversion loss, not a decode error.
    assert ac.w is not None
    assert ac.dcw >= ac.w


async def test_lifetime_energy(ac: InverterThreePhase) -> None:
    assert ac.wh == 12_187_169


async def test_operating_state_is_an_enum(ac: InverterThreePhase) -> None:
    assert ac.st is OperatingState.MPPT


async def test_strings(inverter: KacoInverter) -> None:
    """Model 160's repeating group is sized from the device, not hardcoded."""
    strings = inverter.strings
    assert len(strings) == 2
    assert [s.id_str for s in strings] == ["MPPT 0", "MPPT 1"]
    assert (strings[0].dcv, strings[0].dca, strings[0].dcw) == (355.1, 1.02, 360)
    assert (strings[1].dcv, strings[1].dca, strings[1].dcw) == (533.0, 1.22, 650)


async def test_strings_sum_to_dc_power(inverter: KacoInverter, ac: InverterThreePhase) -> None:
    """A sanity check that the per-string scale factors are right."""
    total = sum(s.dcw for s in inverter.strings if s.dcw is not None)
    assert ac.dcw is not None
    assert abs(total - ac.dcw) <= 20


async def test_nameplate(inverter: KacoInverter) -> None:
    assert inverter.nameplate is not None
    assert inverter.nameplate.w_rtg == 8600  # an 8.6 kW inverter
    assert inverter.nameplate.va_rtg == 8600


async def test_settings(inverter: KacoInverter) -> None:
    assert inverter.settings is not None
    assert inverter.settings.w_max == 8600
    assert inverter.settings.v_ref == 230.0


class TestQuirks:
    """Fields this firmware does not implement, or implements wrongly.

    Each is a real reading from the hardware. They are pinned so that a
    library change that starts surfacing junk as a value gets caught.
    """

    async def test_line_to_line_voltages_absent(self, ac: InverterThreePhase) -> None:
        """Only phase-to-neutral is implemented, despite this being 3-phase."""
        assert ac.pp_vph_ab is None
        assert ac.pp_vph_bc is None
        assert ac.pp_vph_ca is None

    async def test_only_cabinet_temperature_is_real(self, ac: InverterThreePhase) -> None:
        assert ac.tmp_cab == 46.9
        assert ac.tmp_snk is None
        assert ac.tmp_trns is None
        assert ac.tmp_ot is None

    async def test_no_per_string_lifetime_energy(self, inverter: KacoInverter) -> None:
        """Model 160 carries DCWH fields, but this firmware leaves them empty."""
        assert all(s.dcwh is None for s in inverter.strings)

    async def test_no_per_string_operating_state(self, inverter: KacoInverter) -> None:
        assert all(s.dc_st is None for s in inverter.strings)

    async def test_current_rating_absent(self, inverter: KacoInverter) -> None:
        assert inverter.nameplate is not None
        assert inverter.nameplate.a_rtg is None

    async def test_power_factor_rating_is_out_of_range(self, inverter: KacoInverter) -> None:
        """PFRtgQ1 decodes to -14.656 on V5.53 — a power factor cannot leave
        [-1, 1], so the register is junk and must not be surfaced as a value.
        """
        assert inverter.nameplate is not None
        rating = inverter.nameplate.pf_rtg_q1
        assert rating is not None
        assert not -1.0 <= rating <= 1.0

    async def test_grid_connection_point_status_is_unreliable(
        self, inverter: KacoInverter, ac: InverterThreePhase
    ) -> None:
        """Model 122 reports the connection point DISCONNECTED (bit 0) while
        the inverter is exporting 1000 W. Use model 123's ``conn`` or the
        operating state instead.
        """
        assert inverter.status is not None
        assert inverter.status.ecp_conn == 1  # ECPConn.DISCONNECTED
        assert ac.w is not None and ac.w > 0
