"""Validation tests."""

from __future__ import annotations

from formula_registry.registry import get_registry
from validation.validators import validate_inputs


def test_validation_detects_missing_required_value() -> None:
    definition = get_registry().get("fluid_reynolds_number")
    messages = validate_inputs(definition, {"density": 1000.0}, {"density": "kg/m^3"})
    assert any(message.level == "error" for message in messages)


def test_validation_detects_invalid_unit() -> None:
    definition = get_registry().get("heat_sensible_heat")
    messages = validate_inputs(
        definition,
        {"mass": 10.0, "specific_heat": 4.18, "temperature_change": 20.0},
        {"mass": "kg", "specific_heat": "Pa", "temperature_change": "K"},
    )
    assert any("使えません" in message.message for message in messages)

