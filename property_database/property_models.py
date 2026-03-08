"""Data models for the representative property database."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PropertyValue(BaseModel):
    """Single property value with unit and notes."""

    value: float
    unit: str
    note: str = "代表値"


class PropertyRecord(BaseModel):
    """Representative property record for one substance."""

    substance_id: str
    name_ja: str
    aliases: list[str] = Field(default_factory=list)
    molecular_weight: PropertyValue | None = None
    density: PropertyValue | None = None
    specific_heat: PropertyValue | None = None
    viscosity: PropertyValue | None = None
    thermal_conductivity: PropertyValue | None = None
    latent_heat: PropertyValue | None = None
    gas_constant_basis: str | None = None
    temperature_range: str = ""
    notes: str = ""
    source: str = ""

