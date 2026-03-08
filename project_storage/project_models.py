"""Project and calculation case models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class Project(BaseModel):
    """Saved project definition."""

    project_id: str
    name: str
    description: str = ""
    created_at: datetime
    updated_at: datetime


class CalculationCase(BaseModel):
    """Saved calculation case bound to a project."""

    case_id: str
    project_id: str
    formula_id: str
    formula_name: str
    input_values: dict[str, float] = Field(default_factory=dict)
    input_units: dict[str, str] = Field(default_factory=dict)
    pressure_bases: dict[str, str] = Field(default_factory=dict)
    normalized_inputs: dict[str, float] = Field(default_factory=dict)
    output_values: dict[str, float] = Field(default_factory=dict)
    output_units: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    selected_properties: dict[str, str] = Field(default_factory=dict)
    overridden_properties: dict[str, dict[str, float | str]] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
