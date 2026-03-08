# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Loading helpers for formula definitions."""

from __future__ import annotations

import json
from pathlib import Path

from formula_registry.models import FormulaDefinition


FORMULA_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "formulas"


def load_formula_definitions(data_dir: Path | None = None) -> list[FormulaDefinition]:
    """Load all formula definitions from JSON files."""

    directory = data_dir or FORMULA_DATA_DIR
    definitions: list[FormulaDefinition] = []

    for path in sorted(directory.glob("*.json")):
        raw_items = json.loads(path.read_text(encoding="utf-8"))
        definitions.extend(FormulaDefinition.model_validate(item) for item in raw_items)

    return definitions

