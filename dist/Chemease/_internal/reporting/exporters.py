# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Export helpers for result and case data."""

from __future__ import annotations

import json

import pandas as pd

from formula_registry.models import CalculationResult, FormulaDefinition
from reporting.formatters import build_input_table, build_output_table


def result_to_json_bytes(result: CalculationResult) -> bytes:
    """Serialize a calculation result into JSON bytes."""

    return json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2).encode("utf-8")


def result_to_csv_bytes(result: CalculationResult, definition: FormulaDefinition) -> bytes:
    """Serialize input and output tables into a CSV blob."""

    input_table = build_input_table(result, definition)
    output_table = build_output_table(result, definition)
    separator = pd.DataFrame([{"項目": "---", "入力値": "", "入力単位": "", "内部換算値": "", "標準単位": ""}])
    merged = pd.concat([input_table, separator, output_table], ignore_index=True, sort=False)
    return merged.to_csv(index=False).encode("utf-8-sig")

