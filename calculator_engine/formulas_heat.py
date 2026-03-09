# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Heat-transfer formulas."""

from __future__ import annotations

from calculator_engine.common import FormulaComputation, safe_log_mean


def sensible_heat(inputs: dict[str, float]) -> FormulaComputation:
    return FormulaComputation(outputs={"heat_duty": inputs["mass"] * inputs["specific_heat"] * inputs["temperature_change"]})


def latent_heat(inputs: dict[str, float]) -> FormulaComputation:
    return FormulaComputation(outputs={"heat_duty": inputs["mass"] * inputs["latent_heat"]})


def heat_balance(inputs: dict[str, float]) -> FormulaComputation:
    net_heat = inputs["heat_in"] - inputs["heat_out"]
    return FormulaComputation(outputs={"net_heat": net_heat})


def heat_flux(inputs: dict[str, float]) -> FormulaComputation:
    return FormulaComputation(outputs={"heat_flux": inputs["heat_duty"] / inputs["area"]})


def conduction_basic(inputs: dict[str, float]) -> FormulaComputation:
    heat_rate = inputs["thermal_conductivity"] * inputs["area"] * inputs["temperature_difference"] / inputs["thickness"]
    return FormulaComputation(outputs={"heat_duty": heat_rate})


def newton_cooling(inputs: dict[str, float]) -> FormulaComputation:
    heat_rate = inputs["heat_transfer_coefficient"] * inputs["area"] * inputs["temperature_difference"]
    return FormulaComputation(outputs={"heat_duty": heat_rate})


def overall_heat_transfer(inputs: dict[str, float]) -> FormulaComputation:
    return FormulaComputation(outputs={"heat_duty": inputs["overall_u"] * inputs["area"] * inputs["lmtd"]})


def lmtd(inputs: dict[str, float]) -> FormulaComputation:
    mean_difference = safe_log_mean(inputs["delta_t1"], inputs["delta_t2"])
    return FormulaComputation(outputs={"lmtd": mean_difference})


def overall_heat_transfer_coefficient(inputs: dict[str, float]) -> FormulaComputation:
    coefficient = inputs["heat_duty"] / (inputs["area"] * inputs["temperature_difference"])
    return FormulaComputation(outputs={"overall_u": coefficient})


def wall_resistance_series(inputs: dict[str, float]) -> FormulaComputation:
    total_resistance = 1.0 / inputs["h_inner"] + inputs["wall_thickness"] / inputs["wall_conductivity"] + 1.0 / inputs["h_outer"]
    return FormulaComputation(outputs={"total_resistance": total_resistance, "overall_u": 1.0 / total_resistance})


def thermal_resistance_basic(inputs: dict[str, float]) -> FormulaComputation:
    resistance = inputs["thickness"] / (inputs["thermal_conductivity"] * inputs["area"])
    return FormulaComputation(outputs={"thermal_resistance": resistance})


def nusselt_number(inputs: dict[str, float]) -> FormulaComputation:
    nusselt = inputs["heat_transfer_coefficient"] * inputs["characteristic_length"] / inputs["thermal_conductivity"]
    return FormulaComputation(outputs={"nusselt_number": nusselt})


FUNCTIONS = {
    sensible_heat.__name__: sensible_heat,
    latent_heat.__name__: latent_heat,
    heat_balance.__name__: heat_balance,
    heat_flux.__name__: heat_flux,
    conduction_basic.__name__: conduction_basic,
    newton_cooling.__name__: newton_cooling,
    overall_heat_transfer.__name__: overall_heat_transfer,
    lmtd.__name__: lmtd,
    overall_heat_transfer_coefficient.__name__: overall_heat_transfer_coefficient,
    wall_resistance_series.__name__: wall_resistance_series,
    thermal_resistance_basic.__name__: thermal_resistance_basic,
    nusselt_number.__name__: nusselt_number,
}

