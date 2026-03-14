# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Loading helpers for formula definitions."""

from __future__ import annotations

import json
from pathlib import Path

from formula_registry.models import FormulaDefinition
from runtime_paths import get_custom_formula_data_path, get_formula_data_dir


FORMULA_DATA_DIR = get_formula_data_dir()
CUSTOM_FORMULA_DATA_PATH = get_custom_formula_data_path()


def load_formula_definitions(data_dir: Path | None = None) -> list[FormulaDefinition]:
    """Load all formula definitions from JSON files."""

    directory = data_dir or get_formula_data_dir()
    custom_formula_path = get_custom_formula_data_path()
    definitions: list[FormulaDefinition] = []

    for path in sorted(directory.glob("*.json")):
        raw_items = json.loads(path.read_text(encoding="utf-8"))
        definitions.extend(FormulaDefinition.model_validate(item) for item in raw_items)

    if custom_formula_path.exists():
        raw_items = json.loads(custom_formula_path.read_text(encoding="utf-8"))
        definitions.extend(FormulaDefinition.model_validate({**item, "is_user_defined": True}) for item in raw_items)

    return definitions

