# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Formula execution engine."""

from __future__ import annotations

from collections.abc import Callable

from calculator_engine.formulas_basic import FUNCTIONS as BASIC_FUNCTIONS
from calculator_engine.formulas_fluid import FUNCTIONS as FLUID_FUNCTIONS
from calculator_engine.formulas_heat import FUNCTIONS as HEAT_FUNCTIONS
from calculator_engine.formulas_mass_transfer import FUNCTIONS as MASS_TRANSFER_FUNCTIONS
from calculator_engine.formulas_particles import FUNCTIONS as PARTICLE_FUNCTIONS
from calculator_engine.formulas_reaction import FUNCTIONS as REACTION_FUNCTIONS
from calculator_engine.formulas_separation import FUNCTIONS as SEPARATION_FUNCTIONS
from formula_registry.models import CalculationResult, FormulaDefinition, ValidationMessage
from formula_registry.registry import FormulaRegistry, get_registry
from unit_conversion.converters import normalize_formula_input
from unit_conversion.units import UnitConversionError, UnitService, get_unit_service
from validation.validators import validate_inputs


FUNCTION_MAP: dict[str, Callable[[dict[str, float]], object]] = {
    **FLUID_FUNCTIONS,
    **HEAT_FUNCTIONS,
    **MASS_TRANSFER_FUNCTIONS,
    **SEPARATION_FUNCTIONS,
    **REACTION_FUNCTIONS,
    **PARTICLE_FUNCTIONS,
    **BASIC_FUNCTIONS,
}


class CalculationEngine:
    """Coordinate validation, normalization, execution, and output formatting."""

    def __init__(self, registry: FormulaRegistry | None = None, unit_service: UnitService | None = None) -> None:
        self.registry = registry or get_registry()
        self.unit_service = unit_service or get_unit_service()

    def calculate(
        self,
        formula_id: str,
        input_values: dict[str, float],
        input_units: dict[str, str],
        pressure_bases: dict[str, str] | None = None,
        output_units: dict[str, str] | None = None,
        *,
        selected_properties: dict[str, str] | None = None,
        overridden_properties: dict[str, dict[str, float | str]] | None = None,
    ) -> CalculationResult:
        """Execute a formula and return detailed calculation results."""

        definition = self.registry.get(formula_id)
        pressure_bases = pressure_bases or {}
        output_units = output_units or {}

        messages = validate_inputs(definition, input_values, input_units)
        if any(message.level == "error" for message in messages):
            raise ValueError("入力エラーがあるため計算できません。")

        normalized_inputs: dict[str, float] = {}
        normalized_units: dict[str, str] = {}

        for variable in definition.inputs:
            raw_value = input_values[variable.key]
            raw_unit = input_units[variable.key]
            basis = pressure_bases.get(variable.key, "absolute")
            try:
                normalized_inputs[variable.key] = normalize_formula_input(
                    variable,
                    raw_value,
                    raw_unit,
                    pressure_basis=basis,
                    unit_service=self.unit_service,
                )
            except UnitConversionError as exc:
                raise ValueError(str(exc)) from exc
            normalized_units[variable.key] = variable.standard_unit

        function = FUNCTION_MAP[definition.function_name]
        computation = function(normalized_inputs)
        messages.extend(ValidationMessage(level="warning", message=warning) for warning in computation.warnings)

        display_output_values: dict[str, float] = {}
        display_output_units: dict[str, str] = {}
        output_value_map = dict(computation.outputs)
        output_unit_map: dict[str, str] = {}

        output_meta = {item.key: item for item in definition.outputs}
        for key, value in output_value_map.items():
            variable = output_meta[key]
            target_unit = output_units.get(key) or variable.output_preferred_unit or variable.standard_unit
            display_output_values[key] = self.unit_service.denormalize_output(
                value,
                variable.standard_unit,
                target_unit,
                is_temperature_difference=variable.is_temperature_difference,
            )
            display_output_units[key] = target_unit
            output_unit_map[key] = variable.standard_unit

        return CalculationResult(
            formula_id=definition.formula_id,
            formula_name=definition.name_ja,
            category=definition.category,
            input_values=input_values,
            input_units=input_units,
            pressure_bases=pressure_bases,
            normalized_inputs=normalized_inputs,
            normalized_input_units=normalized_units,
            output_values=output_value_map,
            output_units=output_unit_map,
            display_output_values=display_output_values,
            display_output_units=display_output_units,
            messages=messages,
            selected_properties=selected_properties or {},
            overridden_properties=overridden_properties or {},
            equation_latex=definition.equation_latex,
            interpretation=definition.interpretation_hint,
        )
