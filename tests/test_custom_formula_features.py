# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Tests for custom formulas and arbitrary target solving."""

from __future__ import annotations

import math
from pathlib import Path

from calculator_engine.engine import CalculationEngine
from formula_registry.custom_formula_repository import CustomFormulaRepository
from formula_registry.custom_formula_service import CustomFormulaService
from formula_registry.models import FormulaDefinition
from formula_registry.registry import FormulaRegistry, get_registry


def _build_custom_reynolds_formula() -> FormulaDefinition:
    return FormulaDefinition.model_validate(
        {
            "formula_id": "custom_reynolds",
            "name_ja": "カスタムReynolds数",
            "category": "流体",
            "summary": "ユーザー登録のReynolds数式です。",
            "description": "テスト用のカスタム式です。",
            "equation_latex": r"Re = \rho v D / \mu",
            "inputs": [
                {"key": "density", "label_ja": "密度", "description": "密度", "standard_unit": "kg/m^3", "allowed_units": ["kg/m^3"], "positive_only": True, "nonzero": True},
                {"key": "velocity", "label_ja": "流速", "description": "流速", "standard_unit": "m/s", "allowed_units": ["m/s"], "positive_only": True, "nonzero": True},
                {"key": "diameter", "label_ja": "径", "description": "径", "standard_unit": "m", "allowed_units": ["m"], "positive_only": True, "nonzero": True},
                {"key": "viscosity", "label_ja": "粘度", "description": "粘度", "standard_unit": "Pas", "allowed_units": ["Pas"], "positive_only": True, "nonzero": True},
            ],
            "outputs": [
                {"key": "reynolds_number", "label_ja": "Reynolds数", "description": "Re", "standard_unit": "fraction", "allowed_units": ["fraction"], "required": False}
            ],
            "function_name": "custom:custom_reynolds",
            "expression": "density * velocity * diameter / viscosity",
            "keywords": ["カスタム", "Reynolds"],
            "interpretation_hint": "ユーザー定義式のテストです。",
            "is_user_defined": True,
        }
    )


def test_custom_formula_service_save_and_load(tmp_path: Path) -> None:
    repository = CustomFormulaRepository(custom_path=tmp_path / "custom_formulas.json", base_dir=tmp_path / "base")
    repository.base_dir.mkdir(parents=True, exist_ok=True)
    service = CustomFormulaService(repository)

    stored = service.save_formula(_build_custom_reynolds_formula())

    assert stored.formula_id == "custom_reynolds"
    assert len(service.list_custom_formulas()) == 1


def test_custom_formula_engine_calculation() -> None:
    definition = _build_custom_reynolds_formula()
    registry = FormulaRegistry(definitions={definition.formula_id: definition})
    engine = CalculationEngine(registry=registry)

    result = engine.calculate(
        definition.formula_id,
        {"density": 1000.0, "velocity": 1.0, "diameter": 0.1, "viscosity": 0.001},
        {"density": "kg/m^3", "velocity": "m/s", "diameter": "m", "viscosity": "Pas"},
    )

    assert math.isclose(result.output_values["reynolds_number"], 100000.0, rel_tol=1e-12)


def test_engine_can_solve_builtin_formula_for_input_variable() -> None:
    engine = CalculationEngine()
    result = engine.solve_for_variable(
        "fluid_average_velocity",
        "volumetric_flow",
        {"area": 1.0},
        {"area": "m^2"},
        2.0,
        "m/s",
        target_display_unit="m^3/s",
        initial_guess_value=1.0,
        initial_guess_unit="m^3/s",
    )

    assert result.calculation_mode == "solve"
    assert math.isclose(result.input_values["volumetric_flow"], 2.0, rel_tol=1e-9)
    assert math.isclose(result.output_values["velocity"], 2.0, rel_tol=1e-9)
