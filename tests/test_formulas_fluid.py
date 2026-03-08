"""Fluid formula tests."""

from __future__ import annotations

import math

from calculator_engine.engine import CalculationEngine


def test_reynolds_number_formula() -> None:
    engine = CalculationEngine()
    result = engine.calculate(
        "fluid_reynolds_number",
        {"density": 1000.0, "velocity": 1.0, "diameter": 0.05, "viscosity": 1.0},
        {"density": "kg/m^3", "velocity": "m/s", "diameter": "m", "viscosity": "mPas"},
    )
    assert math.isclose(result.output_values["reynolds_number"], 50000.0, rel_tol=1e-9)


def test_darcy_weisbach_pressure_drop_formula() -> None:
    engine = CalculationEngine()
    result = engine.calculate(
        "fluid_darcy_weisbach_pressure_drop",
        {
            "friction_factor": 0.02,
            "pipe_length": 10.0,
            "diameter": 0.05,
            "density": 1000.0,
            "velocity": 2.0,
        },
        {
            "friction_factor": "fraction",
            "pipe_length": "m",
            "diameter": "m",
            "density": "kg/m^3",
            "velocity": "m/s",
        },
    )
    assert math.isclose(result.output_values["pressure_drop"], 8000.0, rel_tol=1e-9)

