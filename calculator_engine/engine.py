# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Formula execution engine."""

from __future__ import annotations

import math
from collections.abc import Callable

from calculator_engine.common import FormulaComputation
from calculator_engine.expression_evaluator import get_safe_expression
from calculator_engine.formulas_basic import FUNCTIONS as BASIC_FUNCTIONS
from calculator_engine.formulas_basic_extra import FUNCTIONS as BASIC_EXTRA_FUNCTIONS
from calculator_engine.formulas_fluid import FUNCTIONS as FLUID_FUNCTIONS
from calculator_engine.formulas_fluid_extra import FUNCTIONS as FLUID_EXTRA_FUNCTIONS
from calculator_engine.formulas_heat import FUNCTIONS as HEAT_FUNCTIONS
from calculator_engine.formulas_heat_extra import FUNCTIONS as HEAT_EXTRA_FUNCTIONS
from calculator_engine.formulas_mass_transfer import FUNCTIONS as MASS_TRANSFER_FUNCTIONS
from calculator_engine.formulas_mass_transfer_extra import FUNCTIONS as MASS_TRANSFER_EXTRA_FUNCTIONS
from calculator_engine.formulas_particles import FUNCTIONS as PARTICLE_FUNCTIONS
from calculator_engine.formulas_particles_extra import FUNCTIONS as PARTICLE_EXTRA_FUNCTIONS
from calculator_engine.formulas_reaction import FUNCTIONS as REACTION_FUNCTIONS
from calculator_engine.formulas_reaction_extra import FUNCTIONS as REACTION_EXTRA_FUNCTIONS
from calculator_engine.formulas_separation import FUNCTIONS as SEPARATION_FUNCTIONS
from calculator_engine.formulas_separation_extra import FUNCTIONS as SEPARATION_EXTRA_FUNCTIONS
from formula_registry.models import CalculationResult, FormulaDefinition, ValidationMessage
from formula_registry.registry import FormulaRegistry, get_registry
from unit_conversion.converters import normalize_formula_input
from unit_conversion.units import UnitConversionError, UnitService, get_unit_service
from validation.validators import validate_inputs


FUNCTION_MAP: dict[str, Callable[[dict[str, float]], FormulaComputation]] = {
    **FLUID_FUNCTIONS,
    **FLUID_EXTRA_FUNCTIONS,
    **HEAT_FUNCTIONS,
    **HEAT_EXTRA_FUNCTIONS,
    **MASS_TRANSFER_FUNCTIONS,
    **MASS_TRANSFER_EXTRA_FUNCTIONS,
    **SEPARATION_FUNCTIONS,
    **SEPARATION_EXTRA_FUNCTIONS,
    **REACTION_FUNCTIONS,
    **REACTION_EXTRA_FUNCTIONS,
    **PARTICLE_FUNCTIONS,
    **PARTICLE_EXTRA_FUNCTIONS,
    **BASIC_FUNCTIONS,
    **BASIC_EXTRA_FUNCTIONS,
}


class CalculationEngine:
    """Coordinate validation, normalization, execution, and output formatting."""

    def __init__(self, registry: FormulaRegistry | None = None, unit_service: UnitService | None = None) -> None:
        self.registry = registry or get_registry()
        self.unit_service = unit_service or get_unit_service()

    def _get_function(self, definition: FormulaDefinition) -> Callable[[dict[str, float]], FormulaComputation]:
        """Resolve a built-in or user-defined formula function."""

        if definition.expression:
            if len(definition.outputs) != 1:
                raise ValueError("expression 登録式は出力1変数のみ対応です。")
            evaluator = get_safe_expression(definition.expression)
            output_key = definition.outputs[0].key

            def _expression_formula(inputs: dict[str, float]) -> FormulaComputation:
                value = evaluator.evaluate(inputs)
                return FormulaComputation(outputs={output_key: value})

            return _expression_formula

        return FUNCTION_MAP[definition.function_name]

    def _normalize_variable_value(
        self,
        variable,
        value: float,
        unit: str,
        pressure_basis: str = "absolute",
    ) -> float:
        """Normalize an input or output-like variable into its standard unit."""

        return self.unit_service.normalize_input(
            value,
            unit,
            variable.standard_unit,
            is_temperature_difference=variable.is_temperature_difference,
            pressure_basis=pressure_basis,
        )

    def _solve_by_secant(
        self,
        objective: Callable[[float], float],
        *,
        initial_guess: float,
        positive_only: bool,
        nonzero: bool,
    ) -> float:
        """Solve a one-dimensional equation using secant with bracket fallback."""

        guess1 = initial_guess
        if positive_only and guess1 <= 0:
            guess1 = 1.0
        if nonzero and math.isclose(guess1, 0.0, abs_tol=1e-12):
            guess1 = 1.0

        guess2 = guess1 * 1.05 if not math.isclose(guess1, 0.0, abs_tol=1e-12) else 1.0
        if positive_only and guess2 <= 0:
            guess2 = max(1.0, abs(guess2))
        if nonzero and math.isclose(guess2, 0.0, abs_tol=1e-12):
            guess2 = 1.0

        y1 = objective(guess1)
        y2 = objective(guess2)

        for _ in range(40):
            if math.isclose(y2, 0.0, rel_tol=1e-10, abs_tol=1e-10):
                return guess2
            denominator = y2 - y1
            if math.isclose(denominator, 0.0, abs_tol=1e-16):
                break
            next_guess = guess2 - y2 * (guess2 - guess1) / denominator
            if positive_only and next_guess <= 0:
                next_guess = max(min(guess1, guess2) / 2.0, 1e-12)
            if nonzero and math.isclose(next_guess, 0.0, abs_tol=1e-12):
                next_guess = 1e-12 if positive_only else 1.0
            guess1, guess2 = guess2, next_guess
            y1, y2 = y2, objective(guess2)

        scale = max(abs(initial_guess), 1.0)
        positive_candidates = [scale * factor for factor in (1e-6, 1e-4, 1e-2, 1e-1, 1.0, 10.0, 100.0, 1e4, 1e6)]
        signed_candidates = [-item for item in reversed(positive_candidates)] + positive_candidates if not positive_only else positive_candidates
        previous_x = signed_candidates[0]
        previous_y = objective(previous_x)
        for current_x in signed_candidates[1:]:
            current_y = objective(current_x)
            if math.isclose(current_y, 0.0, rel_tol=1e-10, abs_tol=1e-10):
                return current_x
            if previous_y * current_y < 0:
                left_x, right_x = previous_x, current_x
                left_y, right_y = previous_y, current_y
                for _ in range(60):
                    middle_x = (left_x + right_x) / 2.0
                    middle_y = objective(middle_x)
                    if math.isclose(middle_y, 0.0, rel_tol=1e-10, abs_tol=1e-10):
                        return middle_x
                    if left_y * middle_y < 0:
                        right_x, right_y = middle_x, middle_y
                    else:
                        left_x, left_y = middle_x, middle_y
                return (left_x + right_x) / 2.0
            previous_x, previous_y = current_x, current_y

        raise ValueError("指定した変数を逆算できませんでした。初期推定値や入力条件を見直してください。")

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

        function = self._get_function(definition)
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

    def solve_for_variable(
        self,
        formula_id: str,
        target_key: str,
        known_input_values: dict[str, float],
        known_input_units: dict[str, str],
        specified_output_value: float,
        specified_output_unit: str,
        *,
        target_display_unit: str,
        initial_guess_value: float,
        initial_guess_unit: str,
        pressure_bases: dict[str, str] | None = None,
        specified_output_pressure_basis: str = "absolute",
        selected_properties: dict[str, str] | None = None,
        overridden_properties: dict[str, dict[str, float | str]] | None = None,
    ) -> CalculationResult:
        """Solve a single-output formula for one selected input variable."""

        definition = self.registry.get(formula_id)
        if len(definition.outputs) != 1:
            raise ValueError("任意変数の逆算は出力1変数の式のみ対応です。")

        output_variable = definition.outputs[0]
        if target_key == output_variable.key:
            output_units = {output_variable.key: target_display_unit}
            return self.calculate(
                formula_id,
                known_input_values,
                known_input_units,
                pressure_bases=pressure_bases,
                output_units=output_units,
                selected_properties=selected_properties,
                overridden_properties=overridden_properties,
            )

        input_meta = {item.key: item for item in definition.inputs}
        if target_key not in input_meta:
            raise ValueError("指定した変数は逆算対象にできません。")
        target_variable = input_meta[target_key]
        pressure_bases = pressure_bases or {}

        messages = validate_inputs(
            definition.model_copy(update={"inputs": [item for item in definition.inputs if item.key != target_key]}),
            known_input_values,
            known_input_units,
        )
        if any(message.level == "error" for message in messages):
            raise ValueError("入力エラーがあるため逆算できません。")

        normalized_inputs: dict[str, float] = {}
        normalized_units: dict[str, str] = {}
        for variable in definition.inputs:
            if variable.key == target_key:
                continue
            raw_value = known_input_values[variable.key]
            raw_unit = known_input_units[variable.key]
            basis = pressure_bases.get(variable.key, "absolute")
            normalized_inputs[variable.key] = normalize_formula_input(
                variable,
                raw_value,
                raw_unit,
                pressure_basis=basis,
                unit_service=self.unit_service,
            )
            normalized_units[variable.key] = variable.standard_unit

        specified_output_normalized = self._normalize_variable_value(
            output_variable,
            specified_output_value,
            specified_output_unit,
            specified_output_pressure_basis,
        )
        initial_guess_normalized = self._normalize_variable_value(
            target_variable,
            initial_guess_value,
            initial_guess_unit,
            pressure_bases.get(target_key, "absolute"),
        )
        function = self._get_function(definition)

        def objective(candidate_value: float) -> float:
            computation = function({**normalized_inputs, target_key: candidate_value})
            return computation.outputs[output_variable.key] - specified_output_normalized

        solved_target = self._solve_by_secant(
            objective,
            initial_guess=initial_guess_normalized,
            positive_only=target_variable.positive_only,
            nonzero=target_variable.nonzero,
        )

        normalized_inputs[target_key] = solved_target
        normalized_units[target_key] = target_variable.standard_unit
        computation = function(normalized_inputs)
        messages.extend(ValidationMessage(level="warning", message=warning) for warning in computation.warnings)

        input_values = dict(known_input_values)
        input_units = dict(known_input_units)
        input_values[target_key] = self.unit_service.denormalize_output(
            solved_target,
            target_variable.standard_unit,
            target_display_unit,
            is_temperature_difference=target_variable.is_temperature_difference,
        )
        input_units[target_key] = target_display_unit

        display_output_values: dict[str, float] = {}
        display_output_units: dict[str, str] = {}
        output_value_map = dict(computation.outputs)
        output_unit_map: dict[str, str] = {}
        display_unit = specified_output_unit
        display_output_values[output_variable.key] = self.unit_service.denormalize_output(
            output_value_map[output_variable.key],
            output_variable.standard_unit,
            display_unit,
            is_temperature_difference=output_variable.is_temperature_difference,
        )
        display_output_units[output_variable.key] = display_unit
        output_unit_map[output_variable.key] = output_variable.standard_unit

        solve_metadata: dict[str, float | str] = {
            "target_key": target_key,
            "target_label": target_variable.label_ja,
            "target_display_unit": target_display_unit,
            "specified_output_key": output_variable.key,
            "specified_output_label": output_variable.label_ja,
            "specified_output_value": specified_output_value,
            "specified_output_unit": specified_output_unit,
        }

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
            calculation_mode="solve",
            solve_metadata=solve_metadata,
        )
