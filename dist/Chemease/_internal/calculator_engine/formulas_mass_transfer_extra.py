# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Additional handbook-inspired mass-transfer formulas."""

from __future__ import annotations

import math

from calculator_engine.common import UNIVERSAL_GAS_CONSTANT, build_single_output_formula, safe_log_mean


FUNCTIONS = {
    "mass_peclet_number": build_single_output_formula(
        "peclet_number",
        lambda inputs: inputs["velocity"] * inputs["characteristic_length"] / inputs["diffusivity"],
    ),
    "mass_biot_number": build_single_output_formula(
        "biot_number",
        lambda inputs: inputs["mass_transfer_coefficient"] * inputs["characteristic_length"] / inputs["diffusivity"],
    ),
    "mass_knudsen_diffusivity": build_single_output_formula(
        "knudsen_diffusivity",
        lambda inputs: (2.0 / 3.0) * inputs["pore_radius"] * math.sqrt(8.0 * UNIVERSAL_GAS_CONSTANT * inputs["temperature"] / (math.pi * inputs["molecular_weight"])),
    ),
    "mass_effective_diffusivity": build_single_output_formula(
        "effective_diffusivity",
        lambda inputs: inputs["porosity"] * inputs["diffusivity"] / inputs["tortuosity"],
    ),
    "mass_individual_flux": build_single_output_formula(
        "molar_flux",
        lambda inputs: inputs["mass_transfer_coefficient"] * inputs["concentration_difference"],
    ),
    "mass_log_mean_driving_force": build_single_output_formula(
        "log_mean_driving_force",
        lambda inputs: safe_log_mean(inputs["driving_force_1"], inputs["driving_force_2"]),
    ),
    "mass_absorption_factor": build_single_output_formula(
        "absorption_factor",
        lambda inputs: inputs["liquid_flow"] / (inputs["equilibrium_slope"] * inputs["gas_flow"]),
    ),
    "mass_stripping_factor": build_single_output_formula(
        "stripping_factor",
        lambda inputs: inputs["equilibrium_slope"] * inputs["gas_flow"] / inputs["liquid_flow"],
    ),
    "mass_distribution_coefficient": build_single_output_formula(
        "distribution_coefficient",
        lambda inputs: inputs["phase_1_concentration"] / inputs["phase_2_concentration"],
    ),
    "mass_partition_ratio": build_single_output_formula(
        "partition_ratio",
        lambda inputs: inputs["solute_concentration_phase_a"] / inputs["solute_concentration_phase_b"],
    ),
    "mass_overall_gas_coefficient": build_single_output_formula(
        "overall_gas_coefficient",
        lambda inputs: 1.0 / ((1.0 / inputs["gas_side_coefficient"]) + inputs["equilibrium_slope"] / inputs["liquid_side_coefficient"]),
    ),
    "mass_overall_liquid_coefficient": build_single_output_formula(
        "overall_liquid_coefficient",
        lambda inputs: 1.0 / ((1.0 / inputs["liquid_side_coefficient"]) + 1.0 / (inputs["equilibrium_slope"] * inputs["gas_side_coefficient"])),
    ),
    "mass_transfer_coefficient_from_sherwood": build_single_output_formula(
        "mass_transfer_coefficient",
        lambda inputs: inputs["sherwood_number"] * inputs["diffusivity"] / inputs["characteristic_length"],
    ),
    "mass_sherwood_from_coefficient": build_single_output_formula(
        "sherwood_number",
        lambda inputs: inputs["mass_transfer_coefficient"] * inputs["characteristic_length"] / inputs["diffusivity"],
    ),
    "mass_diffusion_time_scale": build_single_output_formula(
        "diffusion_time",
        lambda inputs: inputs["characteristic_length"] ** 2 / inputs["diffusivity"],
    ),
    "mass_fourier_number": build_single_output_formula(
        "mass_fourier_number",
        lambda inputs: inputs["diffusivity"] * inputs["time"] / inputs["characteristic_length"] ** 2,
    ),
    "mass_higbie_coefficient": build_single_output_formula(
        "mass_transfer_coefficient",
        lambda inputs: 2.0 * math.sqrt(inputs["diffusivity"] / (math.pi * inputs["contact_time"])),
    ),
    "mass_surface_renewal_coefficient": build_single_output_formula(
        "mass_transfer_coefficient",
        lambda inputs: math.sqrt(inputs["diffusivity"] * inputs["surface_renewal_rate"]),
    ),
    "mass_saturation_ratio": build_single_output_formula(
        "saturation_ratio",
        lambda inputs: inputs["partial_pressure"] / inputs["vapor_pressure"],
    ),
    "mass_interfacial_transfer_rate": build_single_output_formula(
        "transfer_rate",
        lambda inputs: inputs["molar_flux"] * inputs["interfacial_area"],
    ),
}
