# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Data models for the representative property database."""

from __future__ import annotations

from pydantic import BaseModel, Field


PROPERTY_FIELD_DEFINITIONS: list[tuple[str, str, str]] = [
    ("molecular_weight", "分子量", "kg/mol"),
    ("density", "密度", "kg/m^3"),
    ("specific_heat", "比熱", "J/(kg*K)"),
    ("viscosity", "粘度", "Pas"),
    ("thermal_conductivity", "熱伝導率", "W/(m*K)"),
    ("latent_heat", "潜熱", "J/kg"),
    ("boiling_point", "沸点", "K"),
    ("melting_point", "融点", "K"),
    ("critical_temperature", "臨界温度", "K"),
    ("critical_pressure", "臨界圧力", "Pa"),
    ("surface_tension", "表面張力", "N/m"),
    ("vapor_pressure", "蒸気圧", "Pa"),
    ("prandtl_number", "Prandtl数", "fraction"),
]


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
    boiling_point: PropertyValue | None = None
    melting_point: PropertyValue | None = None
    critical_temperature: PropertyValue | None = None
    critical_pressure: PropertyValue | None = None
    surface_tension: PropertyValue | None = None
    vapor_pressure: PropertyValue | None = None
    prandtl_number: PropertyValue | None = None
    phase_reference: str = ""
    gas_constant_basis: str | None = None
    temperature_range: str = ""
    notes: str = ""
    source: str = ""
    data_origin: str = "base"
    is_user_defined: bool = False

