# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Additional handbook-inspired fluid-mechanics formulas."""

from __future__ import annotations

import math

from calculator_engine.common import STANDARD_GRAVITY, build_single_output_formula


def _mach_warning(_: dict[str, float], mach_number: float) -> list[str]:
    if mach_number >= 1.0:
        return ["超音速域です。圧縮性の影響を必ず考慮してください。"]
    if mach_number >= 0.3:
        return ["圧縮性の影響が無視しにくい範囲です。"]
    return []


def _reynolds_warning(_: dict[str, float], reynolds_number: float) -> list[str]:
    if reynolds_number < 2_300:
        return ["層流域の目安です。"]
    if reynolds_number > 4_000:
        return ["乱流域の目安です。"]
    return ["遷移域の目安です。"]


FUNCTIONS = {
    "fluid_mass_flux": build_single_output_formula("mass_flux", lambda inputs: inputs["mass_flow"] / inputs["area"]),
    "fluid_superficial_velocity": build_single_output_formula(
        "superficial_velocity",
        lambda inputs: inputs["volumetric_flow"] / inputs["superficial_area"],
    ),
    "fluid_kinematic_viscosity": build_single_output_formula(
        "kinematic_viscosity",
        lambda inputs: inputs["viscosity"] / inputs["density"],
    ),
    "fluid_euler_number": build_single_output_formula(
        "euler_number",
        lambda inputs: inputs["pressure_difference"] / (inputs["density"] * inputs["velocity"] ** 2),
    ),
    "fluid_weber_number": build_single_output_formula(
        "weber_number",
        lambda inputs: inputs["density"] * inputs["velocity"] ** 2 * inputs["diameter"] / inputs["surface_tension"],
    ),
    "fluid_mach_number": build_single_output_formula(
        "mach_number",
        lambda inputs: inputs["velocity"] / inputs["sound_speed"],
        warning_builder=_mach_warning,
    ),
    "fluid_pressure_head": build_single_output_formula(
        "pressure_head",
        lambda inputs: inputs["pressure_difference"] / (inputs["density"] * STANDARD_GRAVITY),
    ),
    "fluid_velocity_head": build_single_output_formula(
        "velocity_head",
        lambda inputs: inputs["velocity"] ** 2 / (2.0 * STANDARD_GRAVITY),
    ),
    "fluid_total_head": build_single_output_formula(
        "total_head",
        lambda inputs: inputs["pressure_head"] + inputs["velocity_head"] + inputs["elevation_head"],
    ),
    "fluid_pressure_from_head": build_single_output_formula(
        "pressure_difference",
        lambda inputs: inputs["density"] * STANDARD_GRAVITY * inputs["head"],
    ),
    "fluid_hagen_poiseuille_flow": build_single_output_formula(
        "volumetric_flow",
        lambda inputs: math.pi * inputs["diameter"] ** 4 * inputs["pressure_difference"] / (128.0 * inputs["viscosity"] * inputs["pipe_length"]),
    ),
    "fluid_hagen_poiseuille_pressure_drop": build_single_output_formula(
        "pressure_drop",
        lambda inputs: 128.0 * inputs["viscosity"] * inputs["pipe_length"] * inputs["volumetric_flow"] / (math.pi * inputs["diameter"] ** 4),
    ),
    "fluid_reynolds_from_kinematic": build_single_output_formula(
        "reynolds_number",
        lambda inputs: inputs["velocity"] * inputs["diameter"] / inputs["kinematic_viscosity"],
        warning_builder=_reynolds_warning,
    ),
    "fluid_volumetric_flow_from_mass": build_single_output_formula(
        "volumetric_flow",
        lambda inputs: inputs["mass_flow"] / inputs["density"],
    ),
    "fluid_pipe_residence_time": build_single_output_formula(
        "residence_time",
        lambda inputs: inputs["pipe_length"] * inputs["area"] / inputs["volumetric_flow"],
    ),
    "fluid_capillary_number": build_single_output_formula(
        "capillary_number",
        lambda inputs: inputs["viscosity"] * inputs["velocity"] / inputs["surface_tension"],
    ),
    "fluid_hydrostatic_absolute_pressure": build_single_output_formula(
        "absolute_pressure",
        lambda inputs: inputs["reference_pressure"] + inputs["density"] * STANDARD_GRAVITY * inputs["height"],
    ),
    "fluid_manometer_pressure_difference": build_single_output_formula(
        "pressure_difference",
        lambda inputs: (inputs["manometer_density"] - inputs["process_density"]) * STANDARD_GRAVITY * inputs["height_difference"],
    ),
    "fluid_drag_force": build_single_output_formula(
        "drag_force",
        lambda inputs: 0.5 * inputs["drag_coefficient"] * inputs["density"] * inputs["velocity"] ** 2 * inputs["projected_area"],
    ),
    "fluid_power_from_pressure_flow": build_single_output_formula(
        "power",
        lambda inputs: inputs["pressure_difference"] * inputs["volumetric_flow"],
    ),
}
