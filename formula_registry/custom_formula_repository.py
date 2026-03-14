# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Repository for user-defined formula definitions."""

from __future__ import annotations

import json
from pathlib import Path

from formula_registry.models import FormulaDefinition
from runtime_paths import get_custom_formula_data_path, get_formula_data_dir


class CustomFormulaRepository:
    """Load, validate, and persist user-defined formulas."""

    def __init__(
        self,
        custom_path: Path | None = None,
        base_dir: Path | None = None,
    ) -> None:
        self.custom_path = custom_path or get_custom_formula_data_path()
        self.base_dir = base_dir or get_formula_data_dir()
        self.custom_path.parent.mkdir(parents=True, exist_ok=True)

    def load_custom_formulas(self) -> list[FormulaDefinition]:
        """Return user-managed formulas."""

        if not self.custom_path.exists():
            return []
        raw_items = json.loads(self.custom_path.read_text(encoding="utf-8"))
        return [FormulaDefinition.model_validate({**item, "is_user_defined": True}) for item in raw_items]

    def list_base_formula_ids(self) -> set[str]:
        """Return bundled formula identifiers."""

        formula_ids: set[str] = set()
        for path in sorted(self.base_dir.glob("*.json")):
            raw_items = json.loads(path.read_text(encoding="utf-8"))
            formula_ids.update(str(item["formula_id"]) for item in raw_items)
        return formula_ids

    def save_custom_formula(self, definition: FormulaDefinition) -> FormulaDefinition:
        """Insert or update a custom formula definition."""

        formulas = {item.formula_id: item for item in self.load_custom_formulas()}
        stored = FormulaDefinition.model_validate({**definition.model_dump(), "is_user_defined": True})
        formulas[stored.formula_id] = stored
        payload = [self._to_storage_dict(item) for item in sorted(formulas.values(), key=lambda value: value.name_ja)]
        self.custom_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return stored

    def delete_custom_formula(self, formula_id: str) -> bool:
        """Delete a custom formula."""

        formulas = {item.formula_id: item for item in self.load_custom_formulas()}
        removed = formulas.pop(formula_id, None)
        payload = [self._to_storage_dict(item) for item in sorted(formulas.values(), key=lambda value: value.name_ja)]
        self.custom_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return removed is not None

    def _to_storage_dict(self, definition: FormulaDefinition) -> dict[str, object]:
        data = definition.model_dump()
        data.pop("is_user_defined", None)
        return data
