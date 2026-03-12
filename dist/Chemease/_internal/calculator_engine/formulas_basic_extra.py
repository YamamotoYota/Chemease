# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Additional handbook-inspired basic physical-property formulas."""

from __future__ import annotations

import math

from calculator_engine.common import UNIVERSAL_GAS_CONSTANT, build_single_output_formula


FUNCTIONS = {
    "basic_compressibility_factor": build_single_output_formula(
        "compressibility_factor",
        lambda inputs: inputs["pressure"] * inputs["volume"] / (inputs["moles"] * UNIVERSAL_GAS_CONSTANT * inputs["temperature"]),
    ),
    "basic_specific_gas_constant": build_single_output_formula(
        "specific_gas_constant",
        lambda inputs: UNIVERSAL_GAS_CONSTANT / inputs["molecular_weight"],
    ),
    "basic_specific_gravity": build_single_output_formula(
        "specific_gravity",
        lambda inputs: inputs["density"] / inputs["reference_density"],
    ),
    "basic_api_gravity": build_single_output_formula(
        "api_gravity",
        lambda inputs: 141.5 / inputs["specific_gravity"] - 131.5,
    ),
    "basic_specific_volume": build_single_output_formula(
        "specific_volume",
        lambda inputs: 1.0 / inputs["density"],
    ),
    "basic_density_from_specific_volume": build_single_output_formula(
        "density",
        lambda inputs: 1.0 / inputs["specific_volume"],
    ),
    "basic_ppm_to_mass_fraction": build_single_output_formula(
        "mass_fraction",
        lambda inputs: inputs["mass_ppm"] / 1_000_000.0,
    ),
    "basic_mass_fraction_to_ppm": build_single_output_formula(
        "mass_ppm",
        lambda inputs: inputs["mass_fraction"] * 1_000_000.0,
    ),
    "basic_partial_pressure": build_single_output_formula(
        "partial_pressure",
        lambda inputs: inputs["mole_fraction"] * inputs["total_pressure"],
    ),
    "basic_total_pressure_from_partials": build_single_output_formula(
        "total_pressure",
        lambda inputs: inputs["partial_pressure_1"] + inputs["partial_pressure_2"] + inputs["partial_pressure_3"],
    ),
    "basic_mole_percent_to_fraction": build_single_output_formula(
        "mole_fraction",
        lambda inputs: inputs["mole_percent"] / 100.0,
    ),
    "basic_weight_percent_to_fraction": build_single_output_formula(
        "mass_fraction",
        lambda inputs: inputs["weight_percent"] / 100.0,
    ),
    "basic_fraction_to_weight_percent": build_single_output_formula(
        "weight_percent",
        lambda inputs: inputs["mass_fraction"] * 100.0,
    ),
    "basic_molar_concentration_from_mass": build_single_output_formula(
        "molar_concentration",
        lambda inputs: inputs["mass_concentration"] / inputs["molecular_weight"],
    ),
    "basic_mass_concentration_from_density_fraction": build_single_output_formula(
        "mass_concentration",
        lambda inputs: inputs["density"] * inputs["mass_fraction"],
    ),
    "basic_mixture_density": build_single_output_formula(
        "mixture_density",
        lambda inputs: inputs["total_mass"] / inputs["total_volume"],
    ),
    "basic_clausius_clapeyron_pressure": build_single_output_formula(
        "pressure_2",
        lambda inputs: inputs["pressure_1"] * math.exp(-inputs["latent_heat_molar"] / UNIVERSAL_GAS_CONSTANT * (1.0 / inputs["temperature_2"] - 1.0 / inputs["temperature_1"])),
    ),
    "basic_clausius_clapeyron_latent_heat": build_single_output_formula(
        "latent_heat_molar",
        lambda inputs: -UNIVERSAL_GAS_CONSTANT * math.log(inputs["pressure_2"] / inputs["pressure_1"]) / (1.0 / inputs["temperature_2"] - 1.0 / inputs["temperature_1"]),
    ),
    "basic_antoine_vapor_pressure": build_single_output_formula(
        "vapor_pressure",
        lambda inputs: 10.0 ** (inputs["antoine_a"] - inputs["antoine_b"] / (inputs["temperature"] + inputs["antoine_c"])),
    ),
    "basic_antoine_temperature": build_single_output_formula(
        "temperature",
        lambda inputs: inputs["antoine_b"] / (inputs["antoine_a"] - math.log10(inputs["vapor_pressure"])) - inputs["antoine_c"],
    ),
}
