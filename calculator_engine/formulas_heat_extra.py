# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Additional handbook-inspired heat-transfer formulas."""

from __future__ import annotations

import math

from calculator_engine.common import STANDARD_GRAVITY, build_single_output_formula


STEFAN_BOLTZMANN_CONSTANT = 5.670_374_419e-8


def _effectiveness_warning(_: dict[str, float], effectiveness: float) -> list[str]:
    if effectiveness > 1.0:
        return ["有効度が 1 を超えています。入力条件を確認してください。"]
    if effectiveness < 0.0:
        return ["有効度が負です。入力条件を確認してください。"]
    return []


FUNCTIONS = {
    "heat_thermal_diffusivity": build_single_output_formula(
        "thermal_diffusivity",
        lambda inputs: inputs["thermal_conductivity"] / (inputs["density"] * inputs["specific_heat"]),
    ),
    "heat_biot_number": build_single_output_formula(
        "biot_number",
        lambda inputs: inputs["heat_transfer_coefficient"] * inputs["characteristic_length"] / inputs["thermal_conductivity"],
    ),
    "heat_fourier_number": build_single_output_formula(
        "fourier_number",
        lambda inputs: inputs["thermal_diffusivity"] * inputs["time"] / inputs["characteristic_length"] ** 2,
    ),
    "heat_plane_wall_heat_rate": build_single_output_formula(
        "heat_rate",
        lambda inputs: inputs["thermal_conductivity"] * inputs["area"] * inputs["temperature_difference"] / inputs["thickness"],
    ),
    "heat_cylindrical_conduction_heat_rate": build_single_output_formula(
        "heat_rate",
        lambda inputs: 2.0 * math.pi * inputs["thermal_conductivity"] * inputs["length"] * inputs["temperature_difference"] / math.log(inputs["outer_radius"] / inputs["inner_radius"]),
    ),
    "heat_spherical_conduction_heat_rate": build_single_output_formula(
        "heat_rate",
        lambda inputs: 4.0 * math.pi * inputs["thermal_conductivity"] * inputs["temperature_difference"] / ((1.0 / inputs["inner_radius"]) - (1.0 / inputs["outer_radius"])),
    ),
    "heat_convective_resistance": build_single_output_formula(
        "thermal_resistance",
        lambda inputs: 1.0 / (inputs["heat_transfer_coefficient"] * inputs["area"]),
    ),
    "heat_cylindrical_wall_resistance": build_single_output_formula(
        "thermal_resistance",
        lambda inputs: math.log(inputs["outer_radius"] / inputs["inner_radius"]) / (2.0 * math.pi * inputs["thermal_conductivity"] * inputs["length"]),
    ),
    "heat_spherical_wall_resistance": build_single_output_formula(
        "thermal_resistance",
        lambda inputs: ((1.0 / inputs["inner_radius"]) - (1.0 / inputs["outer_radius"])) / (4.0 * math.pi * inputs["thermal_conductivity"]),
    ),
    "heat_blackbody_emissive_power": build_single_output_formula(
        "emissive_power",
        lambda inputs: STEFAN_BOLTZMANN_CONSTANT * inputs["temperature"] ** 4,
    ),
    "heat_radiative_heat_flux": build_single_output_formula(
        "heat_flux",
        lambda inputs: inputs["emissivity"] * STEFAN_BOLTZMANN_CONSTANT * (inputs["surface_temperature"] ** 4 - inputs["surroundings_temperature"] ** 4),
    ),
    "heat_radiative_heat_rate": build_single_output_formula(
        "heat_rate",
        lambda inputs: inputs["emissivity"] * STEFAN_BOLTZMANN_CONSTANT * inputs["area"] * (inputs["surface_temperature"] ** 4 - inputs["surroundings_temperature"] ** 4),
    ),
    "heat_capacity_rate": build_single_output_formula(
        "heat_capacity_rate",
        lambda inputs: inputs["mass_flow"] * inputs["specific_heat"],
    ),
    "heat_maximum_transfer": build_single_output_formula(
        "maximum_heat_transfer",
        lambda inputs: inputs["minimum_heat_capacity_rate"] * (inputs["hot_inlet_temperature"] - inputs["cold_inlet_temperature"]),
    ),
    "heat_effectiveness": build_single_output_formula(
        "effectiveness",
        lambda inputs: inputs["actual_heat_transfer"] / inputs["maximum_heat_transfer"],
        warning_builder=_effectiveness_warning,
    ),
    "heat_ntu": build_single_output_formula(
        "ntu",
        lambda inputs: inputs["overall_heat_transfer_coefficient"] * inputs["area"] / inputs["minimum_heat_capacity_rate"],
    ),
    "heat_prandtl_number": build_single_output_formula(
        "prandtl_number",
        lambda inputs: inputs["specific_heat"] * inputs["viscosity"] / inputs["thermal_conductivity"],
    ),
    "heat_grashof_number": build_single_output_formula(
        "grashof_number",
        lambda inputs: STANDARD_GRAVITY * inputs["thermal_expansion_coefficient"] * inputs["temperature_difference"] * inputs["characteristic_length"] ** 3 / inputs["kinematic_viscosity"] ** 2,
    ),
    "heat_rayleigh_number": build_single_output_formula(
        "rayleigh_number",
        lambda inputs: inputs["grashof_number"] * inputs["prandtl_number"],
    ),
    "heat_lumped_body_temperature": build_single_output_formula(
        "body_temperature",
        lambda inputs: inputs["ambient_temperature"] + (inputs["initial_temperature"] - inputs["ambient_temperature"]) * math.exp(-inputs["heat_transfer_coefficient"] * inputs["area"] * inputs["time"] / (inputs["mass"] * inputs["specific_heat"])),
    ),
}
