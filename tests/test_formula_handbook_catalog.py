# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Regression tests for the expanded handbook formula catalog."""

from __future__ import annotations

import math

from calculator_engine.engine import CalculationEngine


def test_fluid_handbook_formula() -> None:
    engine = CalculationEngine()
    result = engine.calculate(
        "fluid_hagen_poiseuille_flow",
        {"diameter": 0.01, "pressure_difference": 1.0, "viscosity": 1.0, "pipe_length": 1.0},
        {"diameter": "m", "pressure_difference": "kPa", "viscosity": "mPas", "pipe_length": "m"},
    )
    assert math.isclose(result.output_values["volumetric_flow"], 2.4543692606170263e-4, rel_tol=1e-9)


def test_heat_handbook_formula() -> None:
    engine = CalculationEngine()
    result = engine.calculate(
        "heat_thermal_diffusivity",
        {"thermal_conductivity": 0.6, "density": 1000.0, "specific_heat": 4.18},
        {"thermal_conductivity": "W/(m*K)", "density": "kg/m^3", "specific_heat": "kJ/(kg*K)"},
    )
    assert math.isclose(result.output_values["thermal_diffusivity"], 1.4354066985645934e-7, rel_tol=1e-9)


def test_mass_transfer_handbook_formula() -> None:
    engine = CalculationEngine()
    result = engine.calculate(
        "mass_peclet_number",
        {"velocity": 0.01, "characteristic_length": 0.1, "diffusivity": 1.0e-9},
        {"velocity": "m/s", "characteristic_length": "m", "diffusivity": "m^2/s"},
    )
    assert math.isclose(result.output_values["peclet_number"], 1.0e6, rel_tol=1e-12)


def test_separation_handbook_formula() -> None:
    engine = CalculationEngine()
    result = engine.calculate(
        "sep_fenske_minimum_stages",
        {"distillate_composition": 0.95, "bottoms_composition": 0.05, "relative_volatility": 2.0},
        {"distillate_composition": "fraction", "bottoms_composition": "fraction", "relative_volatility": "fraction"},
    )
    assert math.isclose(result.output_values["minimum_stages"], 8.49585502688717, rel_tol=1e-9)


def test_reaction_handbook_formula() -> None:
    engine = CalculationEngine()
    result = engine.calculate(
        "rx_space_velocity",
        {"volumetric_flow": 1.0, "reactor_volume": 0.5},
        {"volumetric_flow": "m^3/h", "reactor_volume": "m^3"},
        output_units={"space_velocity": "1/h"},
    )
    assert math.isclose(result.display_output_values["space_velocity"], 2.0, rel_tol=1e-12)


def test_particle_handbook_formula() -> None:
    engine = CalculationEngine()
    result = engine.calculate(
        "pt_angle_of_repose",
        {"pile_height": 1.0, "pile_radius": 1.0},
        {"pile_height": "m", "pile_radius": "m"},
        output_units={"angle_of_repose": "degree"},
    )
    assert math.isclose(result.display_output_values["angle_of_repose"], 45.0, rel_tol=1e-9)


def test_basic_handbook_formula() -> None:
    engine = CalculationEngine()
    result = engine.calculate(
        "basic_compressibility_factor",
        {"pressure": 101.325, "volume": 1.0, "moles": 44.615, "temperature": 0.0},
        {"pressure": "kPa", "volume": "m^3", "moles": "mol", "temperature": "degC"},
        {"pressure": "absolute"},
    )
    assert math.isclose(result.output_values["compressibility_factor"], 1.0, rel_tol=1e-4)
