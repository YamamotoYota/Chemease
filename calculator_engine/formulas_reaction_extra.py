# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Additional handbook-inspired reaction-engineering formulas."""

from __future__ import annotations

import math

from calculator_engine.common import UNIVERSAL_GAS_CONSTANT, build_single_output_formula


FUNCTIONS = {
    "rx_zero_order_rate": build_single_output_formula(
        "reaction_rate",
        lambda inputs: inputs["rate_constant"],
    ),
    "rx_second_order_rate": build_single_output_formula(
        "reaction_rate",
        lambda inputs: inputs["rate_constant"] * inputs["concentration"] ** 2,
    ),
    "rx_batch_zero_order_conversion": build_single_output_formula(
        "conversion",
        lambda inputs: inputs["rate_constant"] * inputs["time"] / inputs["initial_concentration"],
    ),
    "rx_batch_second_order_conversion": build_single_output_formula(
        "conversion",
        lambda inputs: inputs["rate_constant"] * inputs["initial_concentration"] * inputs["time"] / (1.0 + inputs["rate_constant"] * inputs["initial_concentration"] * inputs["time"]),
    ),
    "rx_half_life_first_order": build_single_output_formula(
        "half_life",
        lambda inputs: math.log(2.0) / inputs["rate_constant"],
    ),
    "rx_half_life_second_order": build_single_output_formula(
        "half_life",
        lambda inputs: 1.0 / (inputs["rate_constant"] * inputs["initial_concentration"]),
    ),
    "rx_cstr_first_order_conversion_from_tau": build_single_output_formula(
        "conversion",
        lambda inputs: inputs["rate_constant"] * inputs["space_time"] / (1.0 + inputs["rate_constant"] * inputs["space_time"]),
    ),
    "rx_pfr_first_order_conversion_from_tau": build_single_output_formula(
        "conversion",
        lambda inputs: 1.0 - math.exp(-inputs["rate_constant"] * inputs["space_time"]),
    ),
    "rx_space_time": build_single_output_formula(
        "space_time",
        lambda inputs: inputs["reactor_volume"] / inputs["volumetric_flow"],
    ),
    "rx_space_velocity": build_single_output_formula(
        "space_velocity",
        lambda inputs: inputs["volumetric_flow"] / inputs["reactor_volume"],
    ),
    "rx_rate_constant_ratio": build_single_output_formula(
        "rate_constant_ratio",
        lambda inputs: math.exp(-inputs["activation_energy"] / UNIVERSAL_GAS_CONSTANT * (1.0 / inputs["temperature_2"] - 1.0 / inputs["temperature_1"])),
    ),
    "rx_activation_energy_from_two_points": build_single_output_formula(
        "activation_energy",
        lambda inputs: UNIVERSAL_GAS_CONSTANT * math.log(inputs["rate_constant_2"] / inputs["rate_constant_1"]) / ((1.0 / inputs["temperature_1"]) - (1.0 / inputs["temperature_2"])),
    ),
    "rx_adiabatic_temperature_rise": build_single_output_formula(
        "temperature_rise",
        lambda inputs: -inputs["heat_of_reaction"] * inputs["initial_concentration"] * inputs["conversion"] / inputs["volumetric_heat_capacity"],
    ),
    "rx_vant_hoff_equilibrium_constant": build_single_output_formula(
        "equilibrium_constant_2",
        lambda inputs: inputs["equilibrium_constant_1"] * math.exp(-inputs["reaction_enthalpy"] / UNIVERSAL_GAS_CONSTANT * (1.0 / inputs["temperature_2"] - 1.0 / inputs["temperature_1"])),
    ),
    "rx_pfr_volume_from_rate": build_single_output_formula(
        "reactor_volume",
        lambda inputs: inputs["molar_feed"] * inputs["conversion"] / inputs["reaction_rate"],
    ),
    "rx_cstr_volume_from_rate": build_single_output_formula(
        "reactor_volume",
        lambda inputs: inputs["molar_feed"] * inputs["conversion"] / inputs["reaction_rate"],
    ),
    "rx_batch_time_constant_rate": build_single_output_formula(
        "reaction_time",
        lambda inputs: inputs["initial_concentration"] * inputs["conversion"] / inputs["reaction_rate"],
    ),
    "rx_thiele_modulus_slab": build_single_output_formula(
        "thiele_modulus",
        lambda inputs: inputs["characteristic_length"] * math.sqrt(inputs["rate_constant"] / inputs["effective_diffusivity"]),
    ),
    "rx_effectiveness_factor_slab": build_single_output_formula(
        "effectiveness_factor",
        lambda inputs: math.tanh(inputs["thiele_modulus"]) / inputs["thiele_modulus"],
    ),
    "rx_heat_generation_rate": build_single_output_formula(
        "heat_generation_rate",
        lambda inputs: -inputs["heat_of_reaction"] * inputs["reaction_rate"] * inputs["reactor_volume"],
    ),
    "rx_heat_removal_rate": build_single_output_formula(
        "heat_removal_rate",
        lambda inputs: inputs["overall_heat_transfer_coefficient"] * inputs["area"] * inputs["temperature_difference"],
    ),
}
