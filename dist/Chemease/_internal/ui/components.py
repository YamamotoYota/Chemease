# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Reusable Streamlit UI components."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from formula_registry.models import FormulaDefinition, ValidationMessage
from property_database.property_models import PROPERTY_FIELD_DEFINITIONS, PropertyRecord
from ui.layout import render_empty_state, render_section_header


PROPERTY_KEYS = [
    "molecular_weight",
    "density",
    "specific_heat",
    "viscosity",
    "thermal_conductivity",
    "latent_heat",
]
PROPERTY_LABELS = {key: label for key, label, _ in PROPERTY_FIELD_DEFINITIONS}


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
    for key, _, _ in PROPERTY_FIELD_DEFINITIONS:
        entry = get_effective_property_entry(record, key, overrides)
        if entry is None:
            continue
        value, unit, note = entry
        rows.append({"物性": PROPERTY_LABELS[key], "値": value, "単位": unit, "備考": note})
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

    render_section_header(
        definition.name_ja,
        f"{definition.summary} カテゴリは「{definition.category}」です。",
    )
    st.write(definition.description)
    st.latex(definition.equation_latex)
    if definition.is_user_defined and definition.expression:
        st.caption("この式はユーザー登録の expression から計算されます。")
        st.code(definition.expression, language="python")

    with st.expander("式の説明と前提", expanded=True):
        for title, items, empty_text in [
            ("適用条件", definition.applicability, "適用条件はまだ登録されていません。入力条件の妥当性を個別に確認してください。"),
            ("前提", definition.assumptions, "前提条件はまだ登録されていません。式の想定範囲を便覧や元資料で確認してください。"),
            ("注意事項・よくある誤用", definition.cautions, "特記事項はまだありません。単位と圧力基準の取り違えに注意してください。"),
            ("参考情報", definition.references, "参考情報はまだ登録されていません。"),
        ]:
            st.markdown(f"**{title}**")
            if items:
                for item in items:
                    st.markdown(f"- {item}")
            else:
                render_empty_state(title, empty_text)

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
        st.caption("まず説明欄で変数の意味を確認し、そのあと単位を選んで値を入力すると取り違えを防ぎやすくなります。")


def render_messages(messages: list[ValidationMessage]) -> None:
    """Render validation and warning messages."""

    for message in messages:
        if message.level == "error":
            st.error(message.message)
        else:
            st.warning(message.message)

