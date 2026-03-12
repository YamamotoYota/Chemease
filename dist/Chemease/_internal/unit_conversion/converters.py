# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Convenience wrappers for conversion use cases."""

from __future__ import annotations

from formula_registry.models import FormulaVariable
from unit_conversion.units import UnitService, get_unit_service


def normalize_formula_input(
    variable: FormulaVariable,
    value: float,
    unit: str,
    *,
    pressure_basis: str = "absolute",
    unit_service: UnitService | None = None,
) -> float:
    """Normalize a formula input value into its standard unit."""

    service = unit_service or get_unit_service()
    return service.normalize_input(
        value,
        unit,
        variable.standard_unit,
        is_temperature_difference=variable.is_temperature_difference,
        pressure_basis=pressure_basis,
    )

