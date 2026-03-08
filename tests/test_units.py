"""Unit conversion tests."""

from __future__ import annotations

import math

from unit_conversion.units import PressureInput, UnitService


def test_length_conversion() -> None:
    service = UnitService()
    assert service.convert_value(1000.0, "mm", "m") == 1.0


def test_temperature_conversion() -> None:
    service = UnitService()
    assert math.isclose(service.convert_value(25.0, "degC", "K"), 298.15, rel_tol=1e-9)
    assert math.isclose(service.convert_value(20.0, "degC", "K", is_temperature_difference=True), 20.0, rel_tol=1e-9)


def test_pressure_conversion() -> None:
    service = UnitService()
    assert math.isclose(service.convert_value(1.0, "bar", "kPa"), 100.0, rel_tol=1e-9)


def test_gauge_to_absolute_pressure_conversion() -> None:
    service = UnitService()
    absolute = service.pressure_to_absolute_pa(PressureInput(value=100.0, unit="kPa", basis="gauge"))
    assert math.isclose(absolute, 201325.0, rel_tol=1e-9)


def test_normal_volume_to_molar_flow_conversion() -> None:
    service = UnitService()
    molar_flow = service.convert_value(22.414, "Nm^3/h", "mol/s")
    assert math.isclose(molar_flow, 1000.0 / 3600.0, rel_tol=1e-6)

