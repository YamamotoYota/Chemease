"""Particle and mechanical-operation formulas."""

from __future__ import annotations

import math

from calculator_engine.common import FormulaComputation, STANDARD_GRAVITY


def stokes_settling_velocity(inputs: dict[str, float]) -> FormulaComputation:
    velocity = STANDARD_GRAVITY * (inputs["particle_density"] - inputs["fluid_density"]) * inputs["particle_diameter"] ** 2 / (18.0 * inputs["viscosity"])
    warnings: list[str] = []
    if velocity < 0:
        warnings.append("粒子密度が流体密度より小さいため、浮上方向を示しています。")
    return FormulaComputation(outputs={"settling_velocity": velocity}, warnings=warnings)


def filtration_basic(inputs: dict[str, float]) -> FormulaComputation:
    mu = inputs["viscosity"]
    alpha = inputs["specific_cake_resistance"]
    cake_conc = inputs["cake_solids_concentration"]
    area = inputs["filter_area"]
    pressure_drop = inputs["pressure_drop"]
    filtrate_volume = inputs["filtrate_volume"]
    medium_resistance = inputs["medium_resistance"]
    time_required = mu * alpha * cake_conc * filtrate_volume ** 2 / (2.0 * area ** 2 * pressure_drop) + mu * medium_resistance * filtrate_volume / (area * pressure_drop)
    return FormulaComputation(outputs={"filtration_time": time_required})


def centrifuge_simple(inputs: dict[str, float]) -> FormulaComputation:
    omega = 2.0 * math.pi * inputs["rotational_speed"] / 60.0
    acceleration = omega ** 2 * inputs["radius"]
    return FormulaComputation(outputs={"centrifugal_acceleration": acceleration, "g_factor": acceleration / STANDARD_GRAVITY})


def drying_rate_basic(inputs: dict[str, float]) -> FormulaComputation:
    return FormulaComputation(outputs={"drying_rate": inputs["drying_coefficient"] * (inputs["surface_humidity"] - inputs["bulk_humidity"])})


def mixing_ratio(inputs: dict[str, float]) -> FormulaComputation:
    mixed_concentration = (
        inputs["stream1_flow"] * inputs["stream1_concentration"]
        + inputs["stream2_flow"] * inputs["stream2_concentration"]
    ) / (inputs["stream1_flow"] + inputs["stream2_flow"])
    return FormulaComputation(outputs={"mixed_concentration": mixed_concentration})


FUNCTIONS = {
    stokes_settling_velocity.__name__: stokes_settling_velocity,
    filtration_basic.__name__: filtration_basic,
    centrifuge_simple.__name__: centrifuge_simple,
    drying_rate_basic.__name__: drying_rate_basic,
    mixing_ratio.__name__: mixing_ratio,
}

