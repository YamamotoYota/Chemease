"""Mass-transfer formulas."""

from __future__ import annotations

from calculator_engine.common import FormulaComputation


def fick_law(inputs: dict[str, float]) -> FormulaComputation:
    return FormulaComputation(outputs={"molar_flux": -inputs["diffusivity"] * inputs["concentration_gradient"]})


def mass_transfer_rate(inputs: dict[str, float]) -> FormulaComputation:
    rate = inputs["mass_transfer_coefficient"] * inputs["area"] * inputs["concentration_difference"]
    return FormulaComputation(outputs={"mass_transfer_rate": rate})


def sherwood_number(inputs: dict[str, float]) -> FormulaComputation:
    sherwood = inputs["mass_transfer_coefficient"] * inputs["characteristic_length"] / inputs["diffusivity"]
    return FormulaComputation(outputs={"sherwood_number": sherwood})


def schmidt_number(inputs: dict[str, float]) -> FormulaComputation:
    schmidt = inputs["viscosity"] / (inputs["density"] * inputs["diffusivity"])
    warnings: list[str] = []
    if schmidt < 0.1 or schmidt > 10_000:
        warnings.append("Schmidt 数が一般的な近似範囲を外れています。")
    return FormulaComputation(outputs={"schmidt_number": schmidt}, warnings=warnings)


def henry_law(inputs: dict[str, float]) -> FormulaComputation:
    return FormulaComputation(outputs={"partial_pressure": inputs["henry_constant"] * inputs["mole_fraction"]})


def raoult_law_simple(inputs: dict[str, float]) -> FormulaComputation:
    return FormulaComputation(outputs={"partial_pressure": inputs["liquid_mole_fraction"] * inputs["saturation_pressure"]})


def molar_flux_basic(inputs: dict[str, float]) -> FormulaComputation:
    return FormulaComputation(outputs={"molar_flux": inputs["molar_flow_rate"] / inputs["area"]})


FUNCTIONS = {
    fick_law.__name__: fick_law,
    mass_transfer_rate.__name__: mass_transfer_rate,
    sherwood_number.__name__: sherwood_number,
    schmidt_number.__name__: schmidt_number,
    henry_law.__name__: henry_law,
    raoult_law_simple.__name__: raoult_law_simple,
    molar_flux_basic.__name__: molar_flux_basic,
}

