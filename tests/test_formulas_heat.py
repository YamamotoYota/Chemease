"""Heat formula tests."""

from __future__ import annotations

import math

from calculator_engine.engine import CalculationEngine


def test_sensible_heat_formula() -> None:
    engine = CalculationEngine()
    result = engine.calculate(
        "heat_sensible_heat",
        {"mass": 10.0, "specific_heat": 4.18, "temperature_change": 20.0},
        {"mass": "kg", "specific_heat": "kJ/(kg*K)", "temperature_change": "degC"},
    )
    assert math.isclose(result.output_values["heat_duty"], 836000.0, rel_tol=1e-9)


def test_lmtd_formula() -> None:
    engine = CalculationEngine()
    result = engine.calculate(
        "heat_lmtd",
        {"delta_t1": 40.0, "delta_t2": 20.0},
        {"delta_t1": "K", "delta_t2": "K"},
    )
    assert math.isclose(result.output_values["lmtd"], 28.8539008178, rel_tol=1e-9)

