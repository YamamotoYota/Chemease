"""Reaction formula tests."""

from __future__ import annotations

import math

from calculator_engine.engine import CalculationEngine


def test_conversion_formula() -> None:
    engine = CalculationEngine()
    result = engine.calculate(
        "rx_conversion",
        {"feed_molar_flow": 10.0, "outlet_molar_flow": 2.0},
        {"feed_molar_flow": "mol/s", "outlet_molar_flow": "mol/s"},
    )
    assert math.isclose(result.output_values["conversion"], 0.8, rel_tol=1e-9)


def test_yield_formula() -> None:
    engine = CalculationEngine()
    result = engine.calculate(
        "rx_yield_value",
        {"actual_product": 80.0, "theoretical_product": 100.0},
        {"actual_product": "kg", "theoretical_product": "kg"},
    )
    assert math.isclose(result.output_values["yield"], 0.8, rel_tol=1e-9)


def test_arrhenius_formula() -> None:
    engine = CalculationEngine()
    result = engine.calculate(
        "rx_arrhenius_rate_constant",
        {"pre_exponential_factor": 1.0e6, "activation_energy": 50.0, "temperature": 350.0},
        {"pre_exponential_factor": "1/s", "activation_energy": "kJ/mol", "temperature": "K"},
    )
    assert math.isclose(result.output_values["rate_constant"], 0.034486, rel_tol=1e-3)

