# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Service layer for user-managed formulas."""

from __future__ import annotations

from functools import lru_cache

from calculator_engine.expression_evaluator import ExpressionValidationError, get_safe_expression
from formula_registry.custom_formula_repository import CustomFormulaRepository
from formula_registry.models import FormulaDefinition
from formula_registry.registry import get_registry


class CustomFormulaService:
    """Validate and persist custom formulas."""

    def __init__(self, repository: CustomFormulaRepository | None = None) -> None:
        self.repository = repository or CustomFormulaRepository()

    def list_custom_formulas(self) -> list[FormulaDefinition]:
        """Return stored custom formulas."""

        return self.repository.load_custom_formulas()

    def save_formula(self, definition: FormulaDefinition) -> FormulaDefinition:
        """Persist a custom formula after basic consistency checks."""

        base_formula_ids = self.repository.list_base_formula_ids()
        custom_formula_ids = {item.formula_id for item in self.repository.load_custom_formulas()}

        if definition.formula_id in base_formula_ids and definition.formula_id not in custom_formula_ids:
            raise ValueError("同じ formula_id の同梱式が存在するため保存できません。")
        if not definition.expression:
            raise ValueError("ユーザー登録式には計算用 expression が必要です。")
        if len(definition.outputs) != 1:
            raise ValueError("ユーザー登録式は現時点では出力1変数のみ対応です。")

        input_keys = {item.key for item in definition.inputs}
        output_key = definition.outputs[0].key
        if output_key in input_keys:
            raise ValueError("出力変数キーは入力変数キーと重複できません。")
        if not input_keys:
            raise ValueError("少なくとも1つの入力変数が必要です。")
        try:
            evaluator = get_safe_expression(definition.expression)
        except ExpressionValidationError as exc:
            raise ValueError(str(exc)) from exc
        unknown_names = [item for item in evaluator.variable_names if item not in input_keys]
        if unknown_names:
            raise ValueError(f"expression に未定義の変数があります: {', '.join(unknown_names)}")

        stored = self.repository.save_custom_formula(definition)
        get_registry.cache_clear()
        return stored

    def delete_formula(self, formula_id: str) -> bool:
        """Delete a custom formula."""

        removed = self.repository.delete_custom_formula(formula_id)
        get_registry.cache_clear()
        return removed


@lru_cache(maxsize=1)
def get_custom_formula_service() -> CustomFormulaService:
    """Return a cached custom formula service."""

    return CustomFormulaService()
