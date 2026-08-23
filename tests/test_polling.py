"""Partial failure: one broken block must not cost every reading."""

from __future__ import annotations

from typing import TYPE_CHECKING

from modbus_connection import IllegalDataAddressError, ModbusTimeoutError

from kaco_modbus import KacoInverter

if TYPE_CHECKING:
    from modbus_connection.mock import MockModbusUnit


def break_model(
    unit: MockModbusUnit, device: KacoInverter, model_id: int, error: Exception
) -> None:
    """Make every read of one SunSpec model fail, and nothing else."""
    assert device.models is not None
    model = device.models.first(model_id)
    assert model is not None
    for address in range(model.address, model.address + model.span):
        unit.fail_read(address, error)


async def test_a_clean_poll_reports_everything(inverter: KacoInverter) -> None:
    report = await inverter.async_update()
    assert report.updated == ["inverter", "mppt", "status", "nameplate", "settings",
                              "controls", "volt_var"]
    assert report.failed == {}


async def test_readings_and_settings_poll_separately(inverter: KacoInverter) -> None:
    """They run on different intervals, so each must stand alone."""
    readings = await inverter.async_update_readings()
    assert readings.updated == ["inverter", "mppt", "status"]

    settings = await inverter.async_update_settings()
    assert settings.updated == ["nameplate", "settings", "controls", "volt_var"]


async def test_one_failing_block_does_not_take_down_the_rest(
    inverter_unit: MockModbusUnit,
) -> None:
    """The whole reason components are polled one at a time.

    A slow or broken register range costs its own entities and nothing else.
    """
    device = KacoInverter(inverter_unit)
    await device.async_update()
    assert device.mppt is not None

    # Break the MPPT block only.
    break_model(inverter_unit, device, 160, ModbusTimeoutError("slow block"))

    report = await device.async_update_readings()

    assert "mppt" in report.failed
    assert "inverter" in report.updated
    assert "status" in report.updated
    assert isinstance(report.failed["mppt"], ModbusTimeoutError)


async def test_readings_survive_broken_settings(inverter_unit: MockModbusUnit) -> None:
    device = KacoInverter(inverter_unit)
    await device.async_update()
    assert device.controls is not None

    break_model(inverter_unit, device, 123, IllegalDataAddressError())

    report = await device.async_update()
    assert "controls" in report.failed
    assert "inverter" in report.updated


async def test_a_dead_device_reports_everything_failed(
    inverter_unit: MockModbusUnit,
) -> None:
    """What a sleeping inverter looks like after dark: connected, silent."""
    device = KacoInverter(inverter_unit)
    await device.async_update()

    inverter_unit.fail_requests(ModbusTimeoutError("asleep"))
    report = await device.async_update_readings()

    assert report.updated == []
    assert set(report.failed) == {"inverter", "mppt", "status"}


async def test_recovers_without_re_running_setup(inverter_unit: MockModbusUnit) -> None:
    """Sunrise: the same object must come back without rediscovery."""
    device = KacoInverter(inverter_unit)
    await device.async_update()
    models_before = device.models

    inverter_unit.fail_requests(ModbusTimeoutError("asleep"))
    assert (await device.async_update_readings()).updated == []

    inverter_unit.fail_requests(None)
    report = await device.async_update_readings()

    assert report.updated == ["inverter", "mppt", "status"]
    assert device.models is models_before


async def test_read_raw_covers_every_polled_component(inverter: KacoInverter) -> None:
    """Diagnostics must dump what the device actually reads."""
    raw = await inverter.async_read_raw()
    assert set(raw) == {"holding"}
    assert len(raw["holding"]) > 200


async def test_curves_are_not_polled_but_can_be_read(inverter: KacoInverter) -> None:
    report = await inverter.async_update_curves()
    assert sorted(report.updated) == ["hfrt", "hvrt", "lfrt", "lvrt", "volt_watt"]
    assert report.failed == {}
