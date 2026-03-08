"""Fluid-mechanics formulas."""

from __future__ import annotations

import math

from calculator_engine.common import FormulaComputation, STANDARD_GRAVITY


def average_velocity(inputs: dict[str, float]) -> FormulaComputation:
    area = inputs["area"]
    volumetric_flow = inputs["volumetric_flow"]
    return FormulaComputation(outputs={"velocity": volumetric_flow / area})


def reynolds_number(inputs: dict[str, float]) -> FormulaComputation:
    reynolds = inputs["density"] * inputs["velocity"] * inputs["diameter"] / inputs["viscosity"]
    warnings: list[str] = []
    if reynolds < 2_300:
        warnings.append("層流域の可能性が高いです。")
    elif reynolds > 4_000:
        warnings.append("乱流域の近似式を用いる条件に近い値です。")
    else:
        warnings.append("遷移域です。摩擦係数や熱物質移動相関の扱いに注意してください。")
    return FormulaComputation(outputs={"reynolds_number": reynolds}, warnings=warnings)


def froude_number(inputs: dict[str, float]) -> FormulaComputation:
    value = inputs["velocity"] / math.sqrt(STANDARD_GRAVITY * inputs["characteristic_length"])
    return FormulaComputation(outputs={"froude_number": value})


def darcy_weisbach_pressure_drop(inputs: dict[str, float]) -> FormulaComputation:
    pressure_drop = inputs["friction_factor"] * (inputs["pipe_length"] / inputs["diameter"]) * (
        inputs["density"] * inputs["velocity"] ** 2 / 2.0
    )
    return FormulaComputation(outputs={"pressure_drop": pressure_drop})


def pipe_friction_factor(inputs: dict[str, float]) -> FormulaComputation:
    reynolds = inputs["reynolds_number"]
    relative_roughness = inputs["roughness"] / inputs["diameter"]
    warnings: list[str] = []
    if reynolds <= 0:
        raise ValueError("Reynolds 数は正である必要があります。")

    if reynolds < 2_300:
        factor = 64.0 / reynolds
        warnings.append("層流域の式 f = 64/Re を使用しました。")
    else:
        factor = (-1.8 * math.log10((relative_roughness / 3.7) ** 1.11 + 6.9 / reynolds)) ** -2
        warnings.append("乱流域の近似として Haaland 式を使用しました。")
        if reynolds < 4_000:
            warnings.append("遷移域では近似精度が低下する可能性があります。")

    return FormulaComputation(outputs={"friction_factor": factor}, warnings=warnings)


def continuity_equation(inputs: dict[str, float]) -> FormulaComputation:
    return FormulaComputation(outputs={"volumetric_flow": inputs["area"] * inputs["velocity"]})


def pump_power(inputs: dict[str, float]) -> FormulaComputation:
    shaft_power = inputs["density"] * STANDARD_GRAVITY * inputs["volumetric_flow"] * inputs["head"] / inputs["efficiency"]
    warnings: list[str] = []
    if inputs["efficiency"] > 1.0:
        warnings.append("効率が 1 を超えています。入力条件を確認してください。")
    return FormulaComputation(outputs={"pump_power": shaft_power}, warnings=warnings)


def static_pressure_difference(inputs: dict[str, float]) -> FormulaComputation:
    return FormulaComputation(outputs={"pressure_difference": inputs["density"] * STANDARD_GRAVITY * inputs["height_difference"]})


def dynamic_pressure(inputs: dict[str, float]) -> FormulaComputation:
    return FormulaComputation(outputs={"dynamic_pressure": inputs["density"] * inputs["velocity"] ** 2 / 2.0})


def pipe_cross_section_area(inputs: dict[str, float]) -> FormulaComputation:
    diameter = inputs["diameter"]
    return FormulaComputation(outputs={"area": math.pi * diameter ** 2 / 4.0})


FUNCTIONS = {
    average_velocity.__name__: average_velocity,
    reynolds_number.__name__: reynolds_number,
    froude_number.__name__: froude_number,
    darcy_weisbach_pressure_drop.__name__: darcy_weisbach_pressure_drop,
    pipe_friction_factor.__name__: pipe_friction_factor,
    continuity_equation.__name__: continuity_equation,
    pump_power.__name__: pump_power,
    static_pressure_difference.__name__: static_pressure_difference,
    dynamic_pressure.__name__: dynamic_pressure,
    pipe_cross_section_area.__name__: pipe_cross_section_area,
}

