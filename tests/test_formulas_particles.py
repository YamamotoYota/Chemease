"""Particle-operation formula tests."""

from __future__ import annotations

import math

from calculator_engine.engine import CalculationEngine


def test_stokes_settling_velocity_formula() -> None:
    engine = CalculationEngine()
    result = engine.calculate(
        "pt_stokes_settling_velocity",
        {
            "particle_density": 2500.0,
            "fluid_density": 1000.0,
            "particle_diameter": 0.1,
            "viscosity": 1.0,
        },
        {
            "particle_density": "kg/m^3",
            "fluid_density": "kg/m^3",
            "particle_diameter": "mm",
            "viscosity": "mPas",
        },
    )
    assert math.isclose(result.output_values["settling_velocity"], 0.008172208333, rel_tol=1e-6)


def test_filtration_basic_formula() -> None:
    engine = CalculationEngine()
    result = engine.calculate(
        "pt_filtration_basic",
        {
            "viscosity": 1.0,
            "specific_cake_resistance": 1.0e10,
            "cake_solids_concentration": 10.0,
            "filter_area": 1.0,
            "pressure_drop": 100.0,
            "filtrate_volume": 0.01,
            "medium_resistance": 1.0e9,
        },
        {
            "viscosity": "mPas",
            "specific_cake_resistance": "m/kg",
            "cake_solids_concentration": "kg/m^3",
            "filter_area": "m^2",
            "pressure_drop": "kPa",
            "filtrate_volume": "m^3",
            "medium_resistance": "1/m",
        },
    )
    assert math.isclose(result.output_values["filtration_time"], 0.15, rel_tol=1e-6)
