"""Basic formula tests."""

from __future__ import annotations

import math

from calculator_engine.engine import CalculationEngine


def test_ideal_gas_state_equation() -> None:
    engine = CalculationEngine()
    result = engine.calculate(
        "basic_ideal_gas_moles",
        {"pressure": 101.325, "volume": 1.0, "temperature": 0.0},
        {"pressure": "kPa", "volume": "m^3", "temperature": "degC"},
        {"pressure": "absolute"},
    )
    assert math.isclose(result.output_values["moles"], 44.615, rel_tol=1e-3)

