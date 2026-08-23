"""Writing to model 123, and the revert timer that guards a setpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
from modbus_connection import IllegalDataValueError

from kaco_modbus import (
    KacoInverter,
    ModelMissingError,
    OutPFSetEna,
    VArPctEna,
    VArPctMod,
    WMaxLimEna,
)
from kaco_modbus.testing import BASE_ADDRESS, BLUEPLANET_86TL3

if TYPE_CHECKING:
    from collections.abc import Iterator

    from modbus_connection.mock import MockModbusUnit


# Offsets within SunSpec model 123, taken from the generated component. They
# are relative to the model header, so the absolute address is simply
# ``model.address + offset`` — the two header registers are already counted.
LIMIT = 5
REVERT_TIMER = 7
LIMIT_ENABLE = 9


def address_of(inverter: KacoInverter, offset: int, model_id: int = 123) -> int:
    """The absolute register address of one field of a model."""
    assert inverter.models is not None
    model = inverter.models.first(model_id)
    assert model is not None
    return model.address + offset


@pytest.fixture
def writes(inverter_unit: MockModbusUnit) -> Iterator[list[tuple[int, Any]]]:
    """Every register write, in order, as ``(address, values)``."""
    recorded: list[tuple[int, Any]] = []
    inverter_unit.on_write(lambda event: recorded.append((event.address, event.values)))
    yield recorded


async def test_setting_a_limit_writes_value_before_enabling(
    inverter: KacoInverter, writes: list[tuple[int, Any]]
) -> None:
    """Order matters: enabling first would briefly apply the previous limit."""
    writes.clear()
    await inverter.async_set_power_limit(50.0)

    assert inverter.controls is not None
    assert inverter.controls.w_max_lim_pct == 50.0
    assert inverter.controls.w_max_lim_ena is WMaxLimEna.ENABLED

    addresses = [address for address, _ in writes]
    assert addresses.index(address_of(inverter, LIMIT)) < addresses.index(
        address_of(inverter, LIMIT_ENABLE)
    )


async def test_the_limit_is_scaled_on_the_way_out(inverter: KacoInverter) -> None:
    """WMaxLimPct_SF is -1, so 50 % must land as the raw value 500."""
    await inverter.async_set_power_limit(50.0)
    assert inverter.controls is not None
    assert inverter.controls.w_max_lim_pct == 50.0

    raw = await inverter.controls.async_read_raw(notify=False)
    assert raw["holding"][address_of(inverter, LIMIT)] == 500


async def test_clearing_a_limit_leaves_the_setpoint_alone(inverter: KacoInverter) -> None:
    """Only the enable flag is touched, so the old value stays visible."""
    await inverter.async_set_power_limit(30.0)
    await inverter.async_clear_power_limit()

    assert inverter.controls is not None
    assert inverter.controls.w_max_lim_ena is WMaxLimEna.DISABLED
    assert inverter.controls.w_max_lim_pct == 30.0


async def test_setting_a_limit_without_enabling_it(inverter: KacoInverter) -> None:
    await inverter.async_set_power_limit(70.0, enable=False)
    assert inverter.controls is not None
    assert inverter.controls.w_max_lim_pct == 70.0
    assert inverter.controls.w_max_lim_ena is WMaxLimEna.DISABLED


@pytest.mark.parametrize("percent", [-1.0, 100.1, 1000.0])
async def test_a_limit_outside_the_range_is_refused(inverter: KacoInverter, percent: float) -> None:
    """Caught before it reaches the wire."""
    with pytest.raises(ValueError, match="between 0 and 100"):
        await inverter.async_set_power_limit(percent)


class TestRevertTimer:
    """This hardware reverts a setpoint after 300 s unless the timer is cleared."""

    async def test_the_device_reports_its_revert_window(self, inverter: KacoInverter) -> None:
        assert inverter.revert_seconds == 300

    async def test_a_write_tries_to_clear_the_timer(self, inverter: KacoInverter) -> None:
        await inverter.async_set_power_limit(50.0)

        assert inverter.setpoints_held is True
        assert inverter.controls is not None
        assert inverter.controls.w_max_lim_pct_rvrt_tms == 0
        # With the timer cleared there is no window left to refresh within.
        assert inverter.revert_seconds is None

    async def test_a_device_refusing_to_hold_is_reported_not_raised(
        self, inverter: KacoInverter, inverter_unit: MockModbusUnit
    ) -> None:
        """Some firmware pins the revert timer. That is not an error — but the
        caller has to know, because it now must rewrite within the window.
        """
        inverter_unit.fail_write(address_of(inverter, REVERT_TIMER), IllegalDataValueError())

        await inverter.async_set_power_limit(50.0)

        assert inverter.setpoints_held is False
        assert inverter.controls is not None
        assert inverter.controls.w_max_lim_ena is WMaxLimEna.ENABLED
        assert inverter.revert_seconds == 300


class TestOtherControls:
    async def test_power_factor(self, inverter: KacoInverter) -> None:
        await inverter.async_set_power_factor(0.95)
        assert inverter.controls is not None
        assert inverter.controls.out_pf_set == 0.95
        assert inverter.controls.out_pf_set_ena is OutPFSetEna.ENABLED

    @pytest.mark.parametrize("power_factor", [-1.5, 1.5])
    async def test_power_factor_outside_the_range(
        self, inverter: KacoInverter, power_factor: float
    ) -> None:
        with pytest.raises(ValueError, match="between -1 and 1"):
            await inverter.async_set_power_factor(power_factor)

    async def test_clearing_power_factor(self, inverter: KacoInverter) -> None:
        await inverter.async_set_power_factor(0.95)
        await inverter.async_clear_power_factor()
        assert inverter.controls is not None
        assert inverter.controls.out_pf_set_ena is OutPFSetEna.DISABLED

    async def test_reactive_power_defaults_to_percent_of_wmax(self, inverter: KacoInverter) -> None:
        await inverter.async_set_reactive_power(20.0)
        assert inverter.controls is not None
        assert inverter.controls.v_ar_pct_mod is VArPctMod.WMax
        assert inverter.controls.v_ar_w_max_pct == 20.0
        assert inverter.controls.v_ar_pct_ena is VArPctEna.ENABLED

    async def test_reactive_power_accepts_negative(self, inverter: KacoInverter) -> None:
        """The sign is the direction of the reactive flow, so it is valid."""
        await inverter.async_set_reactive_power(-20.0)
        assert inverter.controls is not None
        assert inverter.controls.v_ar_w_max_pct == -20.0

    @pytest.mark.parametrize("percent", [-101.0, 101.0])
    async def test_reactive_power_outside_the_range(
        self, inverter: KacoInverter, percent: float
    ) -> None:
        with pytest.raises(ValueError, match="between -100 and 100"):
            await inverter.async_set_reactive_power(percent)

    async def test_clearing_reactive_power(self, inverter: KacoInverter) -> None:
        await inverter.async_set_reactive_power(20.0)
        await inverter.async_clear_reactive_power()
        assert inverter.controls is not None
        assert inverter.controls.v_ar_pct_ena is VArPctEna.DISABLED


async def test_control_on_an_inverter_without_model_123(
    mock_modbus_unit: MockModbusUnit,
) -> None:
    """Explain the absence rather than failing with an AttributeError."""
    without_controls = dict(BLUEPLANET_86TL3)
    controls_header = BASE_ADDRESS + 2 + 2 + 66 + 2 + 50 + 2 + 60 + 2 + 26 + 2 + 30 + 2 + 44
    assert without_controls[controls_header] == 123
    # End the chain where model 123 would start.
    without_controls[controls_header] = 0xFFFF
    without_controls[controls_header + 1] = 0
    mock_modbus_unit.load_raw({"holding": without_controls})

    device = KacoInverter(mock_modbus_unit)
    await device.async_update()
    assert device.controls is None

    with pytest.raises(ModelMissingError, match="cannot be controlled"):
        await device.async_set_power_limit(50.0)
