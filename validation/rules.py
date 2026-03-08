"""Generic validation rules for formula inputs."""

from __future__ import annotations

from formula_registry.models import FormulaVariable, ValidationMessage


def validate_required(variable: FormulaVariable, value: float | None) -> ValidationMessage | None:
    """Validate required fields."""

    if variable.required and value is None:
        return ValidationMessage(level="error", field_key=variable.key, message=f"{variable.label_ja} は必須です。")
    return None


def validate_numeric(variable: FormulaVariable, value: object) -> ValidationMessage | None:
    """Validate numeric input types."""

    if value is None:
        return None
    if not isinstance(value, (int, float)):
        return ValidationMessage(level="error", field_key=variable.key, message=f"{variable.label_ja} は数値で入力してください。")
    return None


def validate_sign(variable: FormulaVariable, value: float | None) -> ValidationMessage | None:
    """Validate positive-only and nonzero constraints."""

    if value is None:
        return None
    if variable.positive_only and value < 0:
        return ValidationMessage(level="error", field_key=variable.key, message=f"{variable.label_ja} は 0 以上で入力してください。")
    if variable.nonzero and value == 0:
        return ValidationMessage(level="error", field_key=variable.key, message=f"{variable.label_ja} に 0 は指定できません。")
    return None


def validate_range(variable: FormulaVariable, value: float | None) -> ValidationMessage | None:
    """Validate optional min/max ranges."""

    if value is None:
        return None
    if variable.min_value is not None and value < variable.min_value:
        return ValidationMessage(level="warning", field_key=variable.key, message=f"{variable.label_ja} が想定範囲より小さい値です。")
    if variable.max_value is not None and value > variable.max_value:
        return ValidationMessage(level="warning", field_key=variable.key, message=f"{variable.label_ja} が想定範囲より大きい値です。")
    return None

