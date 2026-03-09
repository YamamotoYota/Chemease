# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Property reference page."""

from __future__ import annotations

import streamlit as st

from property_database.property_models import PROPERTY_FIELD_DEFINITIONS, PropertyRecord, PropertyValue
from property_database.property_service import PropertyService
from ui.components import PROPERTY_KEYS, property_record_to_dataframe


def _build_record_from_form(
    *,
    substance_id: str,
    name_ja: str,
    aliases_text: str,
    phase_reference: str,
    gas_constant_basis: str,
    temperature_range: str,
    notes: str,
    source: str,
    property_inputs: dict[str, dict[str, str | float]],
    data_origin: str = "custom",
) -> PropertyRecord:
    payload: dict[str, object] = {
        "substance_id": substance_id.strip(),
        "name_ja": name_ja.strip(),
        "aliases": [item.strip() for item in aliases_text.split(",") if item.strip()],
        "phase_reference": phase_reference.strip(),
        "gas_constant_basis": gas_constant_basis.strip(),
        "temperature_range": temperature_range.strip(),
        "notes": notes.strip(),
        "source": source.strip(),
        "data_origin": data_origin,
        "is_user_defined": True,
    }
    for key, values in property_inputs.items():
        value_text = str(values["value"]).strip()
        unit_text = str(values["unit"]).strip()
        note_text = str(values["note"]).strip() or "GUI登録値"
        if value_text and unit_text:
            payload[key] = PropertyValue(value=float(value_text), unit=unit_text, note=note_text)
    return PropertyRecord.model_validate(payload)


def render_property_page(property_service: PropertyService) -> None:
    """Render the property database page."""

    st.title("物性参照")
    tab_view, tab_edit = st.tabs(["参照", "DB登録・編集"])

    with tab_view:
        search_keyword = st.text_input("物質名検索", placeholder="例: 水, air, ethanol")
        records = property_service.search(search_keyword)
        if not records:
            st.info("該当物質が見つかりません。新規登録タブから追加できます。")
        else:
            selected_id = st.selectbox("物質選択", options=[record.substance_id for record in records], format_func=lambda value: property_service.get(value).name_ja)
            record = property_service.get(selected_id)

            override_store = st.session_state.setdefault("property_overrides", {})
            overrides = override_store.get(selected_id, {})

            st.caption(f"適用温度範囲: {record.temperature_range}")
            st.dataframe(property_record_to_dataframe(record, overrides), use_container_width=True, hide_index=True)
            st.caption(f"相・代表状態: {record.phase_reference or '未設定'}")
            st.caption(f"出典: {record.source}")
            st.caption(record.notes)
            st.caption(f"保存元: {'ユーザー編集DB' if record.data_origin == 'custom' else '同梱DB'}")

            with st.expander("案件内の一時上書き", expanded=False):
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
                    if st.button("一時上書きを保存", key=f"save_override_{selected_id}"):
                        override_store[selected_id] = edited_values
                        st.success("このセッション内の上書き値を保存しました。")
                with col_clear:
                    if st.button("一時上書きをクリア", key=f"clear_override_{selected_id}"):
                        override_store.pop(selected_id, None)
                        st.success("上書き値をクリアしました。")

    with tab_edit:
        st.markdown("### 物性DBへの登録・編集")
        mode = st.radio("編集モード", ["新規登録", "既存編集"], horizontal=True)
        current_record: PropertyRecord | None = None
        target_token = "new"
        if mode == "既存編集":
            current_id = st.selectbox("編集対象物質", options=[record.substance_id for record in property_service.list_records()], format_func=lambda value: property_service.get(value).name_ja, key="property_editor_target")
            current_record = property_service.get(current_id)
            target_token = current_record.substance_id

        with st.form("property_editor_form"):
            substance_id = st.text_input("substance_id", value=current_record.substance_id if current_record else "")
            name_ja = st.text_input("物質名", value=current_record.name_ja if current_record else "")
            aliases_text = st.text_input("別名（カンマ区切り）", value=", ".join(current_record.aliases) if current_record else "")
            phase_reference = st.text_input("相・代表状態", value=current_record.phase_reference if current_record else "")
            gas_constant_basis = st.text_input("ガス定数・基準メモ", value=(current_record.gas_constant_basis or "") if current_record else "")
            temperature_range = st.text_input("適用温度範囲", value=current_record.temperature_range if current_record else "")
            source = st.text_input("出典", value=current_record.source if current_record else "")
            notes = st.text_area("備考", value=current_record.notes if current_record else "")

            property_inputs: dict[str, dict[str, str | float]] = {}
            for key, label, default_unit in PROPERTY_FIELD_DEFINITIONS:
                base = getattr(current_record, key, None) if current_record else None
                col1, col2, col3 = st.columns([2, 2, 3])
                with col1:
                    raw_value = st.text_input(f"{label} 値", value="" if base is None else f"{base.value}", key=f"edit_{mode}_{target_token}_{key}_value")
                with col2:
                    raw_unit = st.text_input(f"{label} 単位", value=default_unit if base is None else base.unit, key=f"edit_{mode}_{target_token}_{key}_unit")
                with col3:
                    raw_note = st.text_input(f"{label} 備考", value="" if base is None else base.note, key=f"edit_{mode}_{target_token}_{key}_note")
                property_inputs[key] = {"value": raw_value, "unit": raw_unit, "note": raw_note}

            submitted = st.form_submit_button("DBへ保存")

        if submitted:
            if not substance_id.strip() or not name_ja.strip():
                st.error("substance_id と物質名は必須です。")
            else:
                record_to_save = _build_record_from_form(
                    substance_id=substance_id,
                    name_ja=name_ja,
                    aliases_text=aliases_text,
                    phase_reference=phase_reference,
                    gas_constant_basis=gas_constant_basis,
                    temperature_range=temperature_range,
                    notes=notes,
                    source=source,
                    property_inputs=property_inputs,
                )
                property_service.save_record(record_to_save)
                st.success("物性DBへ保存しました。")
                st.rerun()

        if mode == "既存編集" and current_record is not None and current_record.data_origin == "custom":
            if st.button("ユーザー編集DBから削除", type="secondary"):
                property_service.delete_custom_record(current_record.substance_id)
                st.success("カスタム物性レコードを削除しました。")
                st.rerun()

