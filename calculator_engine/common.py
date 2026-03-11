# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Shared types and helper functions for calculation formulas."""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field


STANDARD_GRAVITY = 9.80665
UNIVERSAL_GAS_CONSTANT = 8.314_462_618


@dataclass(slots=True)
class FormulaComputation:
    """Outputs and warnings produced by a formula function."""

    outputs: dict[str, float]
    warnings: list[str] = field(default_factory=list)


def safe_log_mean(delta_t1: float, delta_t2: float) -> float:
    """Return a log-mean difference with an equal-temperature safeguard."""

    if delta_t1 <= 0 or delta_t2 <= 0:
        raise ValueError("LMTD の温度差は正である必要があります。")
    if math.isclose(delta_t1, delta_t2, rel_tol=1e-9, abs_tol=1e-12):
        return delta_t1
    return (delta_t1 - delta_t2) / math.log(delta_t1 / delta_t2)


def build_single_output_formula(
    output_key: str,
    calculator: Callable[[dict[str, float]], float],
    warning_builder: Callable[[dict[str, float], float], list[str]] | None = None,
) -> Callable[[dict[str, float]], FormulaComputation]:
    """Create a simple one-output formula function from a calculator callback."""

    def _formula(inputs: dict[str, float]) -> FormulaComputation:
        value = calculator(inputs)
        warnings = warning_builder(inputs, value) if warning_builder is not None else []
        return FormulaComputation(outputs={output_key: value}, warnings=warnings)

    return _formula

