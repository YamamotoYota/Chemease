"""Reaction-engineering formulas."""

from __future__ import annotations

import math

from calculator_engine.common import FormulaComputation, UNIVERSAL_GAS_CONSTANT


def conversion(inputs: dict[str, float]) -> FormulaComputation:
    value = (inputs["feed_molar_flow"] - inputs["outlet_molar_flow"]) / inputs["feed_molar_flow"]
    return FormulaComputation(outputs={"conversion": value})


def yield_value(inputs: dict[str, float]) -> FormulaComputation:
    return FormulaComputation(outputs={"yield": inputs["actual_product"] / inputs["theoretical_product"]})


def selectivity(inputs: dict[str, float]) -> FormulaComputation:
    return FormulaComputation(outputs={"selectivity": inputs["desired_product"] / inputs["byproduct"]})


def arrhenius_rate_constant(inputs: dict[str, float]) -> FormulaComputation:
    value = inputs["pre_exponential_factor"] * math.exp(-inputs["activation_energy"] / (UNIVERSAL_GAS_CONSTANT * inputs["temperature"]))
    return FormulaComputation(outputs={"rate_constant": value})


def batch_reactor_first_order(inputs: dict[str, float]) -> FormulaComputation:
    conversion_value = 1.0 - math.exp(-inputs["rate_constant"] * inputs["time"])
    return FormulaComputation(outputs={"conversion": conversion_value})


def cstr_first_order(inputs: dict[str, float]) -> FormulaComputation:
    da = inputs["rate_constant"] * inputs["residence_time"]
    return FormulaComputation(outputs={"conversion": da / (1.0 + da)})


def pfr_first_order(inputs: dict[str, float]) -> FormulaComputation:
    conversion_value = 1.0 - math.exp(-inputs["rate_constant"] * inputs["residence_time"])
    return FormulaComputation(outputs={"conversion": conversion_value})


def residence_time(inputs: dict[str, float]) -> FormulaComputation:
    return FormulaComputation(outputs={"residence_time": inputs["reactor_volume"] / inputs["volumetric_flow"]})


FUNCTIONS = {
    conversion.__name__: conversion,
    yield_value.__name__: yield_value,
    selectivity.__name__: selectivity,
    arrhenius_rate_constant.__name__: arrhenius_rate_constant,
    batch_reactor_first_order.__name__: batch_reactor_first_order,
    cstr_first_order.__name__: cstr_first_order,
    pfr_first_order.__name__: pfr_first_order,
    residence_time.__name__: residence_time,
}

