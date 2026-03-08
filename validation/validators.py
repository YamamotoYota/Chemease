"""Formula-level validation helpers."""

from __future__ import annotations

from formula_registry.models import FormulaDefinition, ValidationMessage
from validation.rules import validate_numeric, validate_range, validate_required, validate_sign


def validate_inputs(definition: FormulaDefinition, inputs: dict[str, object], units: dict[str, str]) -> list[ValidationMessage]:
    """Validate user inputs against variable metadata and chosen units."""

    messages: list[ValidationMessage] = []

    for variable in definition.inputs:
        value = inputs.get(variable.key)
        unit = units.get(variable.key)

        for validator in (validate_required, validate_numeric):
            message = validator(variable, value)
            if message:
                messages.append(message)

        if isinstance(value, (int, float)):
            numeric_value = float(value)
            is_absolute_temperature_in_celsius = (
                variable.standard_unit == "K"
                and not variable.is_temperature_difference
                and unit == "degC"
            )
            if is_absolute_temperature_in_celsius:
                if numeric_value <= -273.15:
                    messages.append(
                        ValidationMessage(
                            level="error",
                            field_key=variable.key,
                            message=f"{variable.label_ja} は絶対零度未満にできません。",
                        )
                    )
            else:
                for validator in (validate_sign, validate_range):
                    message = validator(variable, numeric_value)
                    if message:
                        messages.append(message)

        if unit and variable.allowed_units and unit not in variable.allowed_units:
            messages.append(
                ValidationMessage(
                    level="error",
                    field_key=variable.key,
                    message=f"{variable.label_ja} に単位 {unit} は使えません。",
                )
            )

    return messages
