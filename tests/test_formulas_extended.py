# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Extended formula tests beyond the MVP set."""

from __future__ import annotations

import math

from calculator_engine.engine import CalculationEngine


def test_hydraulic_diameter_formula() -> None:
    engine = CalculationEngine()
    result = engine.calculate(
        "fluid_hydraulic_diameter",
        {"flow_area": 0.02, "wetted_perimeter": 0.4},
        {"flow_area": "m^2", "wetted_perimeter": "m"},
    )
    assert math.isclose(result.output_values["hydraulic_diameter"], 0.2, rel_tol=1e-9)


def test_ideal_gas_density_formula() -> None:
    engine = CalculationEngine()
    result = engine.calculate(
        "basic_ideal_gas_density",
        {"pressure": 101.325, "molecular_weight": 28.97, "temperature": 25.0},
        {"pressure": "kPa", "molecular_weight": "g/mol", "temperature": "degC"},
        {"pressure": "absolute"},
    )
    assert math.isclose(result.output_values["density"], 1.184, rel_tol=5e-2)
