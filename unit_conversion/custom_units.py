# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Custom unit definitions for process-engineering work."""

from __future__ import annotations

from pint import UnitRegistry


def register_custom_units(ureg: UnitRegistry) -> None:
    """Register custom engineering units that are not built into Pint."""

    definitions = [
        "mPas = 0.001 * pascal * second = mPa*s",
        "cP = 0.001 * pascal * second = centipoise",
        "kgf = 9.80665 * newton",
        "kgf_per_cm2 = 98066.5 * pascal = kgf/cm^2",
        "tonne_per_hour = tonne / hour = t/h",
        "normal_cubic_meter = meter ** 3 = Nm^3",
    ]

    for definition in definitions:
        try:
            ureg.define(definition)
        except Exception:
            continue

