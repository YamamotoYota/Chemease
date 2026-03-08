# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Reusable Streamlit UI components."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from formula_registry.models import FormulaDefinition, ValidationMessage
from property_database.property_models import PropertyRecord


PROPERTY_KEYS = [
    "molecular_weight",
    "density",
    "specific_heat",
    "viscosity",
    "thermal_conductivity",
    "latent_heat",
]


def get_effective_property_entry(
    record: PropertyRecord,
    property_key: str,
    overrides: dict[str, dict[str, Any]] | None = None,
) -> tuple[float, str, str] | None:
    """Return a property entry, preferring a temporary override when present."""

    if overrides and property_key in overrides:
        entry = overrides[property_key]
        return float(entry["value"]), str(entry["unit"]), "上書き値"

    value = getattr(record, property_key, None)
    if value is None:
        return None
    return value.value, value.unit, value.note


def property_record_to_dataframe(
    record: PropertyRecord,
    overrides: dict[str, dict[str, Any]] | None = None,
) -> pd.DataFrame:
    """Convert a property record into a display table."""

    rows: list[dict[str, Any]] = []
    labels = {
        "molecular_weight": "分子量",
        "density": "密度",
        "specific_heat": "比熱",
        "viscosity": "粘度",
        "thermal_conductivity": "熱伝導率",
        "latent_heat": "潜熱",
    }
    for key in PROPERTY_KEYS:
        entry = get_effective_property_entry(record, key, overrides)
        if entry is None:
            continue
        value, unit, note = entry
        rows.append({"物性": labels[key], "値": value, "単位": unit, "備考": note})
    return pd.DataFrame(rows)


def render_formula_information(definition: FormulaDefinition) -> None:
    """Render rich explanatory content for a formula."""

    st.subheader(definition.name_ja)
    st.caption(f"カテゴリ: {definition.category}")
    st.write(definition.summary)
    st.write(definition.description)
    st.latex(definition.equation_latex)

    with st.expander("式の説明と前提", expanded=True):
        st.markdown("**適用条件**")
        for item in definition.applicability:
            st.markdown(f"- {item}")
        st.markdown("**前提**")
        for item in definition.assumptions:
            st.markdown(f"- {item}")
        st.markdown("**注意事項・よくある誤用**")
        for item in definition.cautions:
            st.markdown(f"- {item}")
        st.markdown("**参考情報**")
        for item in definition.references:
            st.markdown(f"- {item}")

    with st.expander("変数の意味", expanded=False):
        rows = []
        for variable in [*definition.inputs, *definition.outputs]:
            rows.append(
                {
                    "変数": variable.label_ja,
                    "キー": variable.key,
                    "説明": variable.description,
                    "標準単位": variable.standard_unit,
                    "許容単位": ", ".join(variable.allowed_units),
                }
            )
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def render_messages(messages: list[ValidationMessage]) -> None:
    """Render validation and warning messages."""

    for message in messages:
        if message.level == "error":
            st.error(message.message)
        else:
            st.warning(message.message)

