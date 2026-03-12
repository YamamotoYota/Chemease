# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Formatting helpers for result display."""

from __future__ import annotations

import pandas as pd

from formula_registry.models import CalculationResult, FormulaDefinition


def build_input_table(result: CalculationResult, definition: FormulaDefinition) -> pd.DataFrame:
    """Build a display table for user inputs and normalized values."""

    rows: list[dict[str, object]] = []
    labels = {item.key: item.label_ja for item in definition.inputs}
    target_key = str(result.solve_metadata.get("target_key", "")) if result.calculation_mode == "solve" else ""
    for key, value in result.input_values.items():
        rows.append(
            {
                "項目": labels.get(key, key),
                "区分": "逆算結果" if key == target_key else "入力値",
                "入力値": value,
                "入力単位": result.input_units.get(key, ""),
                "内部換算値": result.normalized_inputs.get(key, ""),
                "標準単位": result.normalized_input_units.get(key, ""),
            }
        )
    return pd.DataFrame(rows)


def build_output_table(result: CalculationResult, definition: FormulaDefinition) -> pd.DataFrame:
    """Build a display table for outputs."""

    rows: list[dict[str, object]] = []
    labels = {item.key: item.label_ja for item in definition.outputs}
    specified_output_key = str(result.solve_metadata.get("specified_output_key", "")) if result.calculation_mode == "solve" else ""
    for key, value in result.output_values.items():
        row = {
            "項目": labels.get(key, key),
            "内部計算値": value,
            "標準単位": result.output_units.get(key, ""),
            "表示値": result.display_output_values.get(key, value),
            "表示単位": result.display_output_units.get(key, result.output_units.get(key, "")),
        }
        if key == specified_output_key:
            row["指定値"] = result.solve_metadata.get("specified_output_value", "")
            row["指定単位"] = result.solve_metadata.get("specified_output_unit", "")
        rows.append(row)
    return pd.DataFrame(rows)

