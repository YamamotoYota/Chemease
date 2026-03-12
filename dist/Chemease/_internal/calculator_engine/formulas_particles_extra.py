# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Additional handbook-inspired particle and mechanical-operation formulas."""

from __future__ import annotations

import math

from calculator_engine.common import STANDARD_GRAVITY, build_single_output_formula


FUNCTIONS = {
    "pt_particle_reynolds_number": build_single_output_formula(
        "particle_reynolds_number",
        lambda inputs: inputs["fluid_density"] * inputs["relative_velocity"] * inputs["particle_diameter"] / inputs["viscosity"],
    ),
    "pt_archimedes_number": build_single_output_formula(
        "archimedes_number",
        lambda inputs: STANDARD_GRAVITY * inputs["particle_diameter"] ** 3 * inputs["fluid_density"] * (inputs["particle_density"] - inputs["fluid_density"]) / inputs["viscosity"] ** 2,
    ),
    "pt_drag_coefficient_stokes": build_single_output_formula(
        "drag_coefficient",
        lambda inputs: 24.0 / inputs["particle_reynolds_number"],
    ),
    "pt_particle_surface_area_sphere": build_single_output_formula(
        "surface_area",
        lambda inputs: math.pi * inputs["particle_diameter"] ** 2,
    ),
    "pt_particle_volume_sphere": build_single_output_formula(
        "particle_volume",
        lambda inputs: math.pi * inputs["particle_diameter"] ** 3 / 6.0,
    ),
    "pt_specific_surface_area": build_single_output_formula(
        "specific_surface_area",
        lambda inputs: 6.0 / (inputs["particle_density"] * inputs["particle_diameter"]),
    ),
    "pt_porosity": build_single_output_formula(
        "porosity",
        lambda inputs: 1.0 - inputs["bulk_density"] / inputs["particle_density"],
    ),
    "pt_bulk_density_from_porosity": build_single_output_formula(
        "bulk_density",
        lambda inputs: inputs["particle_density"] * (1.0 - inputs["porosity"]),
    ),
    "pt_wet_basis_moisture": build_single_output_formula(
        "wet_basis_moisture",
        lambda inputs: inputs["water_mass"] / inputs["wet_mass"],
    ),
    "pt_dry_basis_moisture": build_single_output_formula(
        "dry_basis_moisture",
        lambda inputs: inputs["water_mass"] / inputs["dry_solid_mass"],
    ),
    "pt_wet_to_dry_moisture": build_single_output_formula(
        "dry_basis_moisture",
        lambda inputs: inputs["wet_basis_moisture"] / (1.0 - inputs["wet_basis_moisture"]),
    ),
    "pt_dry_to_wet_moisture": build_single_output_formula(
        "wet_basis_moisture",
        lambda inputs: inputs["dry_basis_moisture"] / (1.0 + inputs["dry_basis_moisture"]),
    ),
    "pt_cake_mass_from_filtrate": build_single_output_formula(
        "cake_mass",
        lambda inputs: inputs["solids_concentration"] * inputs["filtrate_volume"],
    ),
    "pt_filtration_area": build_single_output_formula(
        "filtration_area",
        lambda inputs: math.sqrt(inputs["viscosity"] * inputs["specific_cake_resistance"] * inputs["solids_concentration"] * inputs["filtrate_volume"] ** 2 / (2.0 * inputs["pressure_difference"] * inputs["filtration_time"])),
    ),
    "pt_specific_cake_resistance": build_single_output_formula(
        "specific_cake_resistance",
        lambda inputs: 2.0 * inputs["pressure_difference"] * inputs["filter_area"] ** 2 * inputs["filtration_time"] / (inputs["viscosity"] * inputs["solids_concentration"] * inputs["filtrate_volume"] ** 2),
    ),
    "pt_hindered_settling_velocity": build_single_output_formula(
        "hindered_settling_velocity",
        lambda inputs: inputs["single_particle_velocity"] * inputs["voidage"] ** inputs["richardson_zaki_exponent"],
    ),
    "pt_centrifugal_acceleration": build_single_output_formula(
        "centrifugal_acceleration",
        lambda inputs: inputs["angular_velocity"] ** 2 * inputs["radius"],
    ),
    "pt_minimum_fluidization_reynolds": build_single_output_formula(
        "minimum_fluidization_reynolds",
        lambda inputs: math.sqrt(33.7 ** 2 + 0.0408 * inputs["archimedes_number"]) - 33.7,
    ),
    "pt_minimum_fluidization_velocity": build_single_output_formula(
        "minimum_fluidization_velocity",
        lambda inputs: inputs["minimum_fluidization_reynolds"] * inputs["viscosity"] / (inputs["fluid_density"] * inputs["particle_diameter"]),
    ),
    "pt_angle_of_repose": build_single_output_formula(
        "angle_of_repose",
        lambda inputs: math.atan(inputs["pile_height"] / inputs["pile_radius"]),
    ),
}
