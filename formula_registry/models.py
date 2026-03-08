# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Data models for formula definitions."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class FormulaVariable(BaseModel):
    """Variable metadata used for inputs and outputs."""

    key: str
    label_ja: str
    description: str
    standard_unit: str
    allowed_units: list[str] = Field(default_factory=list)
    required: bool = True
    positive_only: bool = False
    nonzero: bool = False
    min_value: float | None = None
    max_value: float | None = None
    default_value: float | None = None
    suggested_property_key: str | None = None
    pressure_basis_supported: bool = False
    is_temperature_difference: bool = False
    output_preferred_unit: str | None = None


class FormulaDefinition(BaseModel):
    """Complete metadata of a formula entry."""

    formula_id: str
    name_ja: str
    category: str
    summary: str
    description: str
    equation_latex: str
    inputs: list[FormulaVariable]
    outputs: list[FormulaVariable]
    variable_definitions: dict[str, str] = Field(default_factory=dict)
    standard_units: dict[str, str] = Field(default_factory=dict)
    allowed_units: dict[str, list[str]] = Field(default_factory=dict)
    applicability: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    cautions: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)
    function_name: str
    keywords: list[str] = Field(default_factory=list)
    interpretation_hint: str = ""

    @model_validator(mode="after")
    def populate_unit_maps(self) -> "FormulaDefinition":
        """Populate derived unit maps when omitted from JSON."""

        if not self.standard_units:
            self.standard_units = {item.key: item.standard_unit for item in [*self.inputs, *self.outputs]}
        if not self.allowed_units:
            self.allowed_units = {item.key: item.allowed_units for item in [*self.inputs, *self.outputs]}
        return self


class ValidationMessage(BaseModel):
    """Error or warning emitted during validation or calculation."""

    level: Literal["error", "warning"]
    message: str
    field_key: str | None = None


class CalculationResult(BaseModel):
    """Calculated outputs and intermediate information."""

    formula_id: str
    formula_name: str
    category: str
    input_values: dict[str, float]
    input_units: dict[str, str]
    pressure_bases: dict[str, str] = Field(default_factory=dict)
    normalized_inputs: dict[str, float]
    normalized_input_units: dict[str, str]
    output_values: dict[str, float]
    output_units: dict[str, str]
    display_output_values: dict[str, float] = Field(default_factory=dict)
    display_output_units: dict[str, str] = Field(default_factory=dict)
    messages: list[ValidationMessage] = Field(default_factory=list)
    selected_properties: dict[str, str] = Field(default_factory=dict)
    overridden_properties: dict[str, dict[str, float | str]] = Field(default_factory=dict)
    equation_latex: str = ""
    interpretation: str = ""
