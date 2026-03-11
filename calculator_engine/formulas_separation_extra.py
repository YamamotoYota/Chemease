# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Additional handbook-inspired separation formulas."""

from __future__ import annotations

import math

from calculator_engine.common import FormulaComputation, build_single_output_formula


def q_line(inputs: dict[str, float]) -> FormulaComputation:
    q_value = inputs["q_value"]
    if math.isclose(q_value, 1.0, rel_tol=1e-9, abs_tol=1e-12):
        raise ValueError("q 線は q = 1 のとき傾きが発散します。")
    y_value = q_value / (q_value - 1.0) * inputs["liquid_composition"] - inputs["feed_composition"] / (q_value - 1.0)
    return FormulaComputation(outputs={"vapor_composition": y_value})


def _efficiency_warning(_: dict[str, float], efficiency: float) -> list[str]:
    if efficiency > 1.0:
        return ["効率が 1 を超えています。入力条件を確認してください。"]
    if efficiency < 0.0:
        return ["効率が負です。入力条件を確認してください。"]
    return []


FUNCTIONS = {
    "sep_k_value": build_single_output_formula("k_value", lambda inputs: inputs["vapor_composition"] / inputs["liquid_composition"]),
    "sep_vapor_composition_from_k": build_single_output_formula(
        "vapor_composition",
        lambda inputs: inputs["k_value"] * inputs["liquid_composition"],
    ),
    "sep_liquid_composition_from_k": build_single_output_formula(
        "liquid_composition",
        lambda inputs: inputs["vapor_composition"] / inputs["k_value"],
    ),
    "sep_binary_equilibrium_from_alpha": build_single_output_formula(
        "vapor_composition",
        lambda inputs: inputs["relative_volatility"] * inputs["liquid_composition"] / (1.0 + (inputs["relative_volatility"] - 1.0) * inputs["liquid_composition"]),
    ),
    "sep_liquid_composition_from_alpha": build_single_output_formula(
        "liquid_composition",
        lambda inputs: inputs["vapor_composition"] / (inputs["relative_volatility"] - inputs["vapor_composition"] * (inputs["relative_volatility"] - 1.0)),
    ),
    "sep_flash_liquid_fraction": build_single_output_formula(
        "liquid_fraction",
        lambda inputs: 1.0 - inputs["vapor_fraction"],
    ),
    "sep_flash_vapor_fraction_from_flows": build_single_output_formula(
        "vapor_fraction",
        lambda inputs: inputs["vapor_flow"] / inputs["feed_flow"],
    ),
    "sep_rectifying_operating_line": build_single_output_formula(
        "vapor_composition",
        lambda inputs: inputs["reflux_ratio"] / (inputs["reflux_ratio"] + 1.0) * inputs["liquid_composition"] + inputs["distillate_composition"] / (inputs["reflux_ratio"] + 1.0),
    ),
    "sep_stripping_operating_line": build_single_output_formula(
        "vapor_composition",
        lambda inputs: inputs["liquid_to_vapor_ratio"] * inputs["liquid_composition"] - inputs["bottoms_to_vapor_ratio"] * inputs["bottoms_composition"],
    ),
    "sep_q_line": q_line,
    "sep_fenske_minimum_stages": build_single_output_formula(
        "minimum_stages",
        lambda inputs: math.log((inputs["distillate_composition"] / (1.0 - inputs["distillate_composition"])) * ((1.0 - inputs["bottoms_composition"]) / inputs["bottoms_composition"])) / math.log(inputs["relative_volatility"]),
    ),
    "sep_actual_stages": build_single_output_formula(
        "actual_stages",
        lambda inputs: inputs["theoretical_stages"] / inputs["overall_efficiency"],
    ),
    "sep_murphree_efficiency": build_single_output_formula(
        "murphree_efficiency",
        lambda inputs: (inputs["actual_vapor_composition"] - inputs["inlet_vapor_composition"]) / (inputs["equilibrium_vapor_composition"] - inputs["inlet_vapor_composition"]),
        warning_builder=_efficiency_warning,
    ),
    "sep_overall_efficiency": build_single_output_formula(
        "overall_efficiency",
        lambda inputs: inputs["theoretical_stages"] / inputs["actual_stages"],
        warning_builder=_efficiency_warning,
    ),
    "sep_reflux_ratio": build_single_output_formula(
        "reflux_ratio",
        lambda inputs: inputs["reflux_flow"] / inputs["distillate_flow"],
    ),
    "sep_boilup_ratio": build_single_output_formula(
        "boilup_ratio",
        lambda inputs: inputs["vapor_flow"] / inputs["bottoms_flow"],
    ),
    "sep_solvent_to_feed_ratio": build_single_output_formula(
        "solvent_to_feed_ratio",
        lambda inputs: inputs["solvent_flow"] / inputs["feed_flow"],
    ),
    "sep_extraction_factor": build_single_output_formula(
        "extraction_factor",
        lambda inputs: inputs["distribution_coefficient"] * inputs["solvent_flow"] / inputs["feed_flow"],
    ),
    "sep_membrane_rejection": build_single_output_formula(
        "rejection",
        lambda inputs: 1.0 - inputs["permeate_concentration"] / inputs["feed_concentration"],
    ),
    "sep_membrane_sieving_coefficient": build_single_output_formula(
        "sieving_coefficient",
        lambda inputs: inputs["permeate_concentration"] / inputs["feed_concentration"],
    ),
    "sep_concentration_factor": build_single_output_formula(
        "concentration_factor",
        lambda inputs: inputs["retentate_concentration"] / inputs["feed_concentration"],
    ),
}
