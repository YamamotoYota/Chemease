# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Property reference page."""

from __future__ import annotations

import streamlit as st

from property_database.property_service import PropertyService
from ui.components import PROPERTY_KEYS, property_record_to_dataframe


def render_property_page(property_service: PropertyService) -> None:
    """Render the property database page."""

    st.title("物性参照")
    search_keyword = st.text_input("物質名検索", placeholder="例: 水, air, ethanol")
    records = property_service.search(search_keyword)
    if not records:
        st.info("該当物質が見つかりません。")
        return

    selected_id = st.selectbox("物質選択", options=[record.substance_id for record in records], format_func=lambda value: property_service.get(value).name_ja)
    record = property_service.get(selected_id)

    override_store = st.session_state.setdefault("property_overrides", {})
    overrides = override_store.get(selected_id, {})

    st.caption(f"適用温度範囲: {record.temperature_range}")
    st.dataframe(property_record_to_dataframe(record, overrides), use_container_width=True, hide_index=True)
    st.caption(f"出典: {record.source}")
    st.caption(record.notes)

    with st.expander("物性値手入力上書き", expanded=False):
        edited_values: dict[str, dict[str, object]] = {}
        for property_key in PROPERTY_KEYS:
            base = getattr(record, property_key, None)
            if base is None:
                continue
            effective = overrides.get(property_key, {"value": base.value, "unit": base.unit})
            col1, col2 = st.columns([2, 2])
            with col1:
                value = st.number_input(f"{property_key}_value", value=float(effective["value"]), key=f"override_{selected_id}_{property_key}_value")
            with col2:
                unit = st.text_input(f"{property_key}_unit", value=str(effective["unit"]), key=f"override_{selected_id}_{property_key}_unit")
            edited_values[property_key] = {"value": value, "unit": unit}

        col_save, col_clear = st.columns(2)
        with col_save:
            if st.button("上書き保存", key=f"save_override_{selected_id}"):
                override_store[selected_id] = edited_values
                st.success("このセッション内の上書き値を保存しました。")
        with col_clear:
            if st.button("上書きをクリア", key=f"clear_override_{selected_id}"):
                override_store.pop(selected_id, None)
                st.success("上書き値をクリアしました。")

