"""Unit conversion service built on top of Pint."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from pint import Quantity, UnitRegistry

from unit_conversion.custom_units import register_custom_units


NORMAL_TEMPERATURE_K = 273.15
NORMAL_PRESSURE_PA = 101_325.0
UNIVERSAL_GAS_CONSTANT = 8.314_462_618

PERCENT_UNITS = {"wt%", "vol%", "mol%"}
FRACTION_LIKE_UNITS = {"fraction", *PERCENT_UNITS, "mass_ppm"}
PRESSURE_ALIAS_TO_PA = {
    "kgf/cm^2G": 98_066.5,
    "kgf/cm^2A": 98_066.5,
}


@dataclass(slots=True)
class PressureInput:
    """Pressure input with basis information."""

    value: float
    unit: str
    basis: str = "absolute"


class UnitConversionError(ValueError):
    """Raised when a conversion cannot be handled safely."""


class UnitService:
    """High-level conversion wrapper for common engineering units."""

    def __init__(self, atmosphere_pa: float = NORMAL_PRESSURE_PA) -> None:
        self.ureg = UnitRegistry(autoconvert_offset_to_baseunit=True)
        register_custom_units(self.ureg)
        self.atmosphere_pa = atmosphere_pa

    def convert_value(
        self,
        value: float,
        from_unit: str,
        to_unit: str,
        *,
        is_temperature_difference: bool = False,
        pressure_basis: str = "absolute",
    ) -> float:
        """Convert a numeric value between supported units."""

        if from_unit == to_unit:
            return float(value)

        if from_unit in FRACTION_LIKE_UNITS or to_unit in FRACTION_LIKE_UNITS:
            return self._convert_fraction(value, from_unit, to_unit)

        if from_unit.startswith("Nm^3") or to_unit.startswith("Nm^3"):
            return self._convert_normal_volume(value, from_unit, to_unit)

        if from_unit in PRESSURE_ALIAS_TO_PA or to_unit in PRESSURE_ALIAS_TO_PA:
            return self._convert_pressure_alias(value, from_unit, to_unit, pressure_basis)

        if is_temperature_difference:
            return self._convert_temperature_difference(value, from_unit, to_unit)

        try:
            quantity = self.ureg.Quantity(value, self._normalize_unit_string(from_unit))
            converted = quantity.to(self._normalize_unit_string(to_unit))
        except Exception as exc:
            raise UnitConversionError(f"単位変換に失敗しました: {from_unit} -> {to_unit}") from exc

        return float(converted.magnitude)

    def normalize_input(
        self,
        value: float,
        from_unit: str,
        standard_unit: str,
        *,
        is_temperature_difference: bool = False,
        pressure_basis: str = "absolute",
    ) -> float:
        """Convert a UI input value into the standard unit."""

        return self.convert_value(
            value,
            from_unit,
            standard_unit,
            is_temperature_difference=is_temperature_difference,
            pressure_basis=pressure_basis,
        )

    def denormalize_output(
        self,
        value: float,
        standard_unit: str,
        display_unit: str,
        *,
        is_temperature_difference: bool = False,
    ) -> float:
        """Convert a standard-unit output into a selected display unit."""

        return self.convert_value(
            value,
            standard_unit,
            display_unit,
            is_temperature_difference=is_temperature_difference,
        )

    def pressure_to_absolute_pa(self, pressure: PressureInput) -> float:
        """Convert a pressure input into absolute pascals."""

        if pressure.unit == "Pa":
            value_pa = pressure.value
        elif pressure.unit in PRESSURE_ALIAS_TO_PA:
            value_pa = pressure.value * PRESSURE_ALIAS_TO_PA[pressure.unit]
            inferred_basis = "gauge" if pressure.unit.endswith("G") else "absolute"
            if inferred_basis == "gauge":
                value_pa += self.atmosphere_pa
            return value_pa
        else:
            value_pa = self.convert_value(pressure.value, pressure.unit, "Pa")

        if pressure.basis == "gauge":
            value_pa += self.atmosphere_pa
        return value_pa

    def _normalize_unit_string(self, unit: str) -> str:
        replacements = {
            "Pas": "Pa*s",
            "m^2": "meter**2",
            "m^3": "meter**3",
            "cm^2": "centimeter**2",
            "L": "liter",
            "mL": "milliliter",
            "degC": "degC",
            "kg/h": "kilogram/hour",
            "kg/s": "kilogram/second",
            "t/h": "tonne_per_hour",
            "m^3/h": "meter**3/hour",
            "m^3/s": "meter**3/second",
            "L/min": "liter/minute",
            "mol/s": "mole/second",
            "kmol/h": "kilomole/hour",
            "kg/m^3": "kilogram/meter**3",
            "g/cm^3": "gram/centimeter**3",
            "W": "watt",
            "kW": "kilowatt",
            "J": "joule",
            "kJ": "kilojoule",
            "MJ": "megajoule",
            "cal": "4.184 * joule",
            "kcal": "4184 * joule",
            "mol/L": "mole/liter",
            "kmol/m^3": "kilomole/meter**3",
            "mmHg": "millimeter_Hg",
        }
        normalized = replacements.get(unit, unit)
        return normalized.replace("^", "**")

    def _convert_temperature_difference(self, value: float, from_unit: str, to_unit: str) -> float:
        if from_unit == to_unit:
            return float(value)

        difference_units = {"K": 1.0, "degC": 1.0}
        if from_unit in difference_units and to_unit in difference_units:
            return float(value)
        raise UnitConversionError(f"温度差単位は {from_unit} -> {to_unit} を変換できません。")

    def _convert_fraction(self, value: float, from_unit: str, to_unit: str) -> float:
        if from_unit == to_unit:
            return float(value)

        as_fraction = value
        if from_unit in PERCENT_UNITS:
            as_fraction = value / 100.0
        elif from_unit == "mass_ppm":
            as_fraction = value / 1_000_000.0
        elif from_unit == "fraction":
            as_fraction = value
        else:
            raise UnitConversionError(f"未対応の割合単位です: {from_unit}")

        if to_unit in PERCENT_UNITS:
            return as_fraction * 100.0
        if to_unit == "mass_ppm":
            return as_fraction * 1_000_000.0
        if to_unit == "fraction":
            return as_fraction
        raise UnitConversionError(f"未対応の割合単位です: {to_unit}")

    def _convert_normal_volume(self, value: float, from_unit: str, to_unit: str) -> float:
        volume_flow_conversions = {
            "Nm^3/h": (1.0 / 3600.0, "Nm^3/s"),
            "Nm^3/s": (1.0, "Nm^3/s"),
            "m^3/h": (1.0 / 3600.0, "m^3/s"),
            "m^3/s": (1.0, "m^3/s"),
        }

        if from_unit in {"Nm^3/h", "Nm^3/s"} and to_unit == "mol/s":
            factor, _ = volume_flow_conversions[from_unit]
            volumetric_flow = value * factor
            return volumetric_flow / 0.022414

        if from_unit == "mol/s" and to_unit in {"Nm^3/h", "Nm^3/s"}:
            normal_flow = value * 0.022414
            factor = 3600.0 if to_unit == "Nm^3/h" else 1.0
            return normal_flow * factor

        if from_unit in volume_flow_conversions and to_unit in volume_flow_conversions:
            factor_from, canonical_from = volume_flow_conversions[from_unit]
            factor_to, canonical_to = volume_flow_conversions[to_unit]
            if canonical_from != canonical_to:
                raise UnitConversionError("実流量と標準流量は専用式でのみ変換してください。")
            base_value = value * factor_from
            return base_value / factor_to

        raise UnitConversionError(f"標準体積流量の変換に失敗しました: {from_unit} -> {to_unit}")

    def _convert_pressure_alias(self, value: float, from_unit: str, to_unit: str, pressure_basis: str) -> float:
        if from_unit in PRESSURE_ALIAS_TO_PA:
            pa_value = value * PRESSURE_ALIAS_TO_PA[from_unit]
            if from_unit.endswith("G"):
                pa_value += self.atmosphere_pa
        else:
            pa_value = self.convert_value(value, from_unit, "Pa", pressure_basis=pressure_basis)

        if to_unit == "Pa":
            return pa_value
        if to_unit in PRESSURE_ALIAS_TO_PA:
            if to_unit.endswith("G"):
                pa_value -= self.atmosphere_pa
            return pa_value / PRESSURE_ALIAS_TO_PA[to_unit]
        return self.convert_value(pa_value, "Pa", to_unit)


@lru_cache(maxsize=1)
def get_unit_service() -> UnitService:
    """Return a cached unit service instance."""

    return UnitService()
