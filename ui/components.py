# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Reusable Streamlit UI components."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from formula_registry.models import FormulaDefinition, ValidationMessage
from property_database.property_models import PROPERTY_FIELD_DEFINITIONS, PropertyRecord


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
    labels = {key: label for key, label, _ in PROPERTY_FIELD_DEFINITIONS}
    for key, _, _ in PROPERTY_FIELD_DEFINITIONS:
        entry = get_effective_property_entry(record, key, overrides)
        if entry is None:
            continue
        value, unit, note = entry
        rows.append({"物性": labels[key], "値": value, "単位": unit, "備考": note})
    rows.extend(
        [
            {"物性": "相・代表状態", "値": record.phase_reference, "単位": "", "備考": ""},
            {"物性": "適用温度範囲", "値": record.temperature_range, "単位": "", "備考": ""},
            {"物性": "データ出所", "値": record.data_origin, "単位": "", "備考": ""},
        ]
    )
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

