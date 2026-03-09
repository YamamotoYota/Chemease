# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Separation-process formulas."""

from __future__ import annotations

import math

from calculator_engine.common import FormulaComputation


def relative_volatility(inputs: dict[str, float]) -> FormulaComputation:
    return FormulaComputation(outputs={"relative_volatility": inputs["k_light"] / inputs["k_heavy"]})


def simple_flash(inputs: dict[str, float]) -> FormulaComputation:
    vapor_fraction = (inputs["feed_mole_fraction"] - inputs["liquid_mole_fraction"]) / (
        inputs["vapor_mole_fraction"] - inputs["liquid_mole_fraction"]
    )
    warnings: list[str] = []
    if vapor_fraction < 0 or vapor_fraction > 1:
        warnings.append("算出されたフラッシュ蒸発率が 0～1 を外れています。相平衡条件を確認してください。")
    return FormulaComputation(
        outputs={"vapor_fraction": vapor_fraction, "liquid_fraction": 1.0 - vapor_fraction},
        warnings=warnings,
    )


def theoretical_stages_simple(inputs: dict[str, float]) -> FormulaComputation:
    numerator = (inputs["x_distillate"] / (1.0 - inputs["x_distillate"])) * ((1.0 - inputs["x_bottom"]) / inputs["x_bottom"])
    stages = math.log(numerator) / math.log(inputs["relative_volatility"])
    return FormulaComputation(outputs={"theoretical_stages": stages})


def minimum_reflux_ratio_simple(inputs: dict[str, float]) -> FormulaComputation:
    x_feed = inputs["x_feed"]
    alpha = inputs["relative_volatility"]
    y_feed_star = alpha * x_feed / (1.0 + (alpha - 1.0) * x_feed)
    reflux_ratio = (inputs["x_distillate"] - y_feed_star) / (y_feed_star - x_feed)
    warnings: list[str] = []
    if reflux_ratio < 0:
        warnings.append("簡易推算の結果が負値です。組成条件と相対揮発度を確認してください。")
    return FormulaComputation(outputs={"minimum_reflux_ratio": reflux_ratio}, warnings=warnings)


def separation_factor_basic(inputs: dict[str, float]) -> FormulaComputation:
    numerator = inputs["y_light"] / (1.0 - inputs["y_light"])
    denominator = inputs["x_light"] / (1.0 - inputs["x_light"])
    return FormulaComputation(outputs={"separation_factor": numerator / denominator})


def stage_cut(inputs: dict[str, float]) -> FormulaComputation:
    return FormulaComputation(outputs={"stage_cut": inputs["distillate_flow"] / inputs["feed_flow"]})


def component_recovery(inputs: dict[str, float]) -> FormulaComputation:
    recovery = inputs["distillate_flow"] * inputs["distillate_composition"] / (inputs["feed_flow"] * inputs["feed_composition"])
    return FormulaComputation(outputs={"recovery": recovery})


FUNCTIONS = {
    relative_volatility.__name__: relative_volatility,
    simple_flash.__name__: simple_flash,
    theoretical_stages_simple.__name__: theoretical_stages_simple,
    minimum_reflux_ratio_simple.__name__: minimum_reflux_ratio_simple,
    separation_factor_basic.__name__: separation_factor_basic,
    stage_cut.__name__: stage_cut,
    component_recovery.__name__: component_recovery,
}

