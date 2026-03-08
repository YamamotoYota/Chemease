# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Basic physical-property and process formulas."""

from __future__ import annotations

from calculator_engine.common import FormulaComputation, UNIVERSAL_GAS_CONSTANT


def ideal_gas_moles(inputs: dict[str, float]) -> FormulaComputation:
    moles = inputs["pressure"] * inputs["volume"] / (UNIVERSAL_GAS_CONSTANT * inputs["temperature"])
    return FormulaComputation(outputs={"moles": moles})


def mixture_molecular_weight(inputs: dict[str, float]) -> FormulaComputation:
    molecular_weight = (
        inputs["mole_fraction_1"] * inputs["mw_1"]
        + inputs["mole_fraction_2"] * inputs["mw_2"]
        + inputs["mole_fraction_3"] * inputs["mw_3"]
    )
    warnings: list[str] = []
    mole_fraction_sum = inputs["mole_fraction_1"] + inputs["mole_fraction_2"] + inputs["mole_fraction_3"]
    if abs(mole_fraction_sum - 1.0) > 1e-6:
        warnings.append("モル分率の合計が 1 ではありません。")
    return FormulaComputation(outputs={"molecular_weight": molecular_weight}, warnings=warnings)


def mole_fraction(inputs: dict[str, float]) -> FormulaComputation:
    return FormulaComputation(outputs={"mole_fraction": inputs["component_moles"] / inputs["total_moles"]})


def mass_fraction(inputs: dict[str, float]) -> FormulaComputation:
    return FormulaComputation(outputs={"mass_fraction": inputs["component_mass"] / inputs["total_mass"]})


def concentration_conversion(inputs: dict[str, float]) -> FormulaComputation:
    mass_concentration = inputs["molar_concentration"] * inputs["molecular_weight"]
    return FormulaComputation(outputs={"mass_concentration": mass_concentration})


def standard_state_conversion(inputs: dict[str, float]) -> FormulaComputation:
    normal_flow = inputs["actual_volumetric_flow"] * (inputs["pressure"] / 101_325.0) * (273.15 / inputs["temperature"])
    return FormulaComputation(outputs={"normal_volumetric_flow": normal_flow})


def molar_to_mass_flow(inputs: dict[str, float]) -> FormulaComputation:
    return FormulaComputation(outputs={"mass_flow": inputs["molar_flow"] * inputs["molecular_weight"]})


def volumetric_to_molar_flow(inputs: dict[str, float]) -> FormulaComputation:
    molar_flow = inputs["pressure"] * inputs["volumetric_flow"] / (UNIVERSAL_GAS_CONSTANT * inputs["temperature"])
    return FormulaComputation(outputs={"molar_flow": molar_flow})


def humidity_ratio(inputs: dict[str, float]) -> FormulaComputation:
    ratio = 0.62198 * inputs["water_vapor_pressure"] / (inputs["total_pressure"] - inputs["water_vapor_pressure"])
    return FormulaComputation(outputs={"humidity_ratio": ratio})


FUNCTIONS = {
    ideal_gas_moles.__name__: ideal_gas_moles,
    mixture_molecular_weight.__name__: mixture_molecular_weight,
    mole_fraction.__name__: mole_fraction,
    mass_fraction.__name__: mass_fraction,
    concentration_conversion.__name__: concentration_conversion,
    standard_state_conversion.__name__: standard_state_conversion,
    molar_to_mass_flow.__name__: molar_to_mass_flow,
    volumetric_to_molar_flow.__name__: volumetric_to_molar_flow,
    humidity_ratio.__name__: humidity_ratio,
}

