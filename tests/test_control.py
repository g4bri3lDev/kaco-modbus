"""Writing to model 123, and the revert timer that guards a setpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
from modbus_connection import IllegalDataValueError

from kaco_modbus import (
    KacoInverter,
    ModelMissingError,
    OutPFSetEna,
    SetpointRejectedError,
    VArPctEna,
    VArPctMod,
    WMaxLimEna,
)
from kaco_modbus.testing import BLUEPLANET_86TL3, holding, ignore_writes, without_model

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
    await inverter.async_set_power_limit(50.0, revert_seconds=300)

    assert inverter.controls is not None
    assert inverter.controls.w_max_lim_pct == 50.0
    assert inverter.controls.w_max_lim_ena is WMaxLimEna.ENABLED

    addresses = [address for address, _ in writes]
    assert addresses.index(address_of(inverter, LIMIT)) < addresses.index(
        address_of(inverter, LIMIT_ENABLE)
    )


async def test_the_limit_is_scaled_on_the_way_out(inverter: KacoInverter) -> None:
    """WMaxLimPct_SF is -1, so 50 % must land as the raw value 500."""
    await inverter.async_set_power_limit(50.0, revert_seconds=300)
    assert inverter.controls is not None
    assert inverter.controls.w_max_lim_pct == 50.0

    raw = await inverter.controls.async_read_raw(notify=False)
    assert raw["holding"][address_of(inverter, LIMIT)] == 500


async def test_clearing_a_limit_leaves_the_setpoint_alone(inverter: KacoInverter) -> None:
    """Only the enable flag is touched, so the old value stays visible."""
    await inverter.async_set_power_limit(30.0, revert_seconds=300)
    await inverter.async_clear_power_limit()

    assert inverter.controls is not None
    assert inverter.controls.w_max_lim_ena is WMaxLimEna.DISABLED
    assert inverter.controls.w_max_lim_pct == 30.0


async def test_setting_a_limit_without_enabling_it(inverter: KacoInverter) -> None:
    await inverter.async_set_power_limit(70.0, enable=False, revert_seconds=300)
    assert inverter.controls is not None
    assert inverter.controls.w_max_lim_pct == 70.0
    assert inverter.controls.w_max_lim_ena is WMaxLimEna.DISABLED


@pytest.mark.parametrize("percent", [-1.0, 100.1, 1000.0])
async def test_a_limit_outside_the_range_is_refused(inverter: KacoInverter, percent: float) -> None:
    """Caught before it reaches the wire."""
    with pytest.raises(ValueError, match="between 0 and 100"):
        await inverter.async_set_power_limit(percent, revert_seconds=300)


class TestRevertTimer:
    """The image reads a 300 s revert timer; the setters set or clear it."""

    async def test_the_device_reports_its_revert_window(self, inverter: KacoInverter) -> None:
        assert inverter.revert_seconds == 300

    async def test_a_refused_period_raises(
        self, inverter: KacoInverter, inverter_unit: MockModbusUnit
    ) -> None:
        """A limit whose period did not take would not revert when expected."""
        inverter_unit.fail_write(address_of(inverter, REVERT_TIMER), IllegalDataValueError())

        with pytest.raises(IllegalDataValueError):
            await inverter.async_set_power_limit(50.0, revert_seconds=3600)

    @pytest.mark.parametrize("seconds", [0, -1, 65536])
    async def test_a_period_outside_the_range_is_refused(
        self, inverter: KacoInverter, writes: list[tuple[int, Any]], seconds: int
    ) -> None:
        """The firmware silently refuses 0, so a limit cannot be held without resending."""
        writes.clear()
        with pytest.raises(ValueError, match="between 1 and 65535"):
            await inverter.async_set_power_limit(50.0, revert_seconds=seconds)
        with pytest.raises(ValueError, match="between 1 and 65535"):
            await inverter.async_resend_power_limit(seconds)
        assert writes == []

    async def test_the_period_is_required(self, inverter: KacoInverter) -> None:
        with pytest.raises(TypeError):
            await inverter.async_set_power_limit(50.0)  # type: ignore[call-arg]


class TestIgnoredWrites:
    """With write access off, the inverter acknowledges writes and drops them."""

    @pytest.mark.usefixtures("writes_ignored")
    async def test_an_ignored_limit_raises(self, inverter: KacoInverter) -> None:
        with pytest.raises(SetpointRejectedError, match="w_max_lim_pct_rvrt_tms"):
            await inverter.async_set_power_limit(50.0, revert_seconds=3600)

    @pytest.mark.usefixtures("writes_ignored")
    async def test_an_ignored_limit_value_raises(self, inverter: KacoInverter) -> None:
        """The period already matches here, so the setpoint is what gives it away."""
        with pytest.raises(SetpointRejectedError, match="w_max_lim_pct"):
            await inverter.async_set_power_limit(50.0, revert_seconds=300)

    @pytest.mark.usefixtures("writes_ignored")
    async def test_an_ignored_enable_raises(self, inverter: KacoInverter) -> None:
        """Period and setpoint already match, so only the enable flag differs."""
        with pytest.raises(SetpointRejectedError, match="w_max_lim_ena"):
            await inverter.async_set_power_limit(100.0, revert_seconds=300)

    async def test_an_ignored_clear_raises(
        self, inverter: KacoInverter, inverter_unit: MockModbusUnit
    ) -> None:
        await inverter.async_set_power_limit(50.0, revert_seconds=300)
        ignore_writes(inverter_unit)

        with pytest.raises(SetpointRejectedError, match="w_max_lim_ena"):
            await inverter.async_clear_power_limit()

    async def test_scaling_rounds_without_raising(self, inverter: KacoInverter) -> None:
        """WMaxLimPct_SF is -1, so 33.33 % reads back as 33.3 %."""
        await inverter.async_set_power_limit(33.33, revert_seconds=300)
        assert inverter.controls is not None
        assert inverter.controls.w_max_lim_pct == 33.3

    async def test_a_limit_can_be_stored_disabled(self, inverter: KacoInverter) -> None:
        await inverter.async_set_power_limit(40.0, enable=False, revert_seconds=300)
        assert inverter.controls is not None
        assert inverter.controls.w_max_lim_ena is WMaxLimEna.DISABLED


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

    async def test_power_factor_survives_a_refused_timer(
        self, inverter: KacoInverter, inverter_unit: MockModbusUnit
    ) -> None:
        assert inverter.models is not None
        inverter_unit.fail_write(address_of(inverter, 12), IllegalDataValueError())
        await inverter.async_set_power_factor(0.95)
        assert inverter.controls is not None
        assert inverter.controls.out_pf_set_ena is OutPFSetEna.ENABLED

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
    mock_modbus_unit.load_raw(holding(without_model(BLUEPLANET_86TL3, 123)))

    device = KacoInverter(mock_modbus_unit)
    await device.async_update()
    assert device.controls is None

    with pytest.raises(ModelMissingError, match="cannot be controlled"):
        await device.async_set_power_limit(50.0, revert_seconds=300)


class TestCallerRevertPeriod:
    """A caller that keeps a limit alive picks the period it survives a silence for."""

    async def test_set_power_limit_writes_revert_period(
        self, inverter: KacoInverter, writes: list[tuple[int, Any]]
    ) -> None:
        """The period goes out first, so the limit never runs on the old one."""
        writes.clear()
        await inverter.async_set_power_limit(50.0, revert_seconds=3600)

        assert [address for address, _ in writes] == [
            address_of(inverter, REVERT_TIMER),
            address_of(inverter, LIMIT),
            address_of(inverter, LIMIT_ENABLE),
        ]
        assert inverter.controls is not None
        assert inverter.controls.w_max_lim_pct_rvrt_tms == 3600
        assert inverter.revert_seconds == 3600

    async def test_resend_rewrites_read_value(
        self, inverter: KacoInverter, writes: list[tuple[int, Any]]
    ) -> None:
        """Writing restarts the period; the value comes from a fresh read."""
        await inverter.async_set_power_limit(70.0, revert_seconds=3600)
        writes.clear()

        assert await inverter.async_resend_power_limit(3600) is True

        assert [address for address, _ in writes] == [
            address_of(inverter, REVERT_TIMER),
            address_of(inverter, LIMIT),
            address_of(inverter, LIMIT_ENABLE),
        ]
        assert inverter.controls is not None
        assert inverter.controls.w_max_lim_pct == 70.0
        assert inverter.controls.w_max_lim_ena is WMaxLimEna.ENABLED

    async def test_resend_uses_a_value_changed_elsewhere(
        self, inverter: KacoInverter, inverter_unit: MockModbusUnit
    ) -> None:
        """Another controller's limit is kept alive as it is, not overwritten."""
        await inverter.async_set_power_limit(50.0, revert_seconds=3600)
        await inverter_unit.write_register(address_of(inverter, LIMIT), 700)

        assert await inverter.async_resend_power_limit(3600) is True

        assert inverter.controls is not None
        assert inverter.controls.w_max_lim_pct == 70.0

    async def test_resend_skips_inactive(
        self, inverter: KacoInverter, writes: list[tuple[int, Any]]
    ) -> None:
        """A limit the device already dropped is never brought back."""
        writes.clear()
        assert await inverter.async_resend_power_limit(3600) is False
        assert writes == []

    async def test_resend_without_controls(self, mock_modbus_unit: MockModbusUnit) -> None:
        mock_modbus_unit.load_raw(holding(without_model(BLUEPLANET_86TL3, 123)))
        device = KacoInverter(mock_modbus_unit)
        await device.async_update()

        with pytest.raises(ModelMissingError):
            await device.async_resend_power_limit(3600)
