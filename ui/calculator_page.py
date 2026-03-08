# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Calculator page."""

from __future__ import annotations

from typing import Any

import streamlit as st

from calculator_engine.engine import CalculationEngine
from formula_registry.registry import FormulaRegistry
from project_storage.project_service import ProjectService
from property_database.property_service import PropertyService
from reporting.exporters import result_to_csv_bytes, result_to_json_bytes
from reporting.formatters import build_input_table, build_output_table
from ui.components import get_effective_property_entry, property_record_to_dataframe, render_formula_information, render_messages
from validation.validators import validate_inputs


def _apply_loaded_case_to_state(definition_id: str) -> None:
    loaded_case = st.session_state.get("loaded_case")
    if not loaded_case or loaded_case.get("formula_id") != definition_id:
        return

    token = f"{loaded_case.get('case_id', 'ad-hoc')}:{definition_id}"
    if st.session_state.get("_loaded_case_token") == token:
        return

    for key, value in loaded_case.get("input_values", {}).items():
        st.session_state[f"input_{definition_id}_{key}"] = float(value)
    for key, value in loaded_case.get("input_units", {}).items():
        st.session_state[f"unit_{definition_id}_{key}"] = value
    for key, value in loaded_case.get("pressure_bases", {}).items():
        st.session_state[f"basis_{definition_id}_{key}"] = value
    st.session_state["_loaded_case_token"] = token


def _apply_property_to_input(
    formula_id: str,
    variable_key: str,
    candidate_value: float,
    candidate_unit: str,
    allowed_units: list[str],
    standard_unit: str,
    unit_service,
) -> None:
    target_unit = candidate_unit if candidate_unit in allowed_units else standard_unit
    input_value = candidate_value if target_unit == candidate_unit else unit_service.convert_value(candidate_value, candidate_unit, target_unit)
    st.session_state[f"input_{formula_id}_{variable_key}"] = float(input_value)
    st.session_state[f"unit_{formula_id}_{variable_key}"] = target_unit


def render_calculator_page(
    registry: FormulaRegistry,
    engine: CalculationEngine,
    property_service: PropertyService,
    project_service: ProjectService,
) -> None:
    """Render the calculation page."""

    st.title("計算")
    category_options = ["すべて", *registry.list_categories()]
    selected_category = st.selectbox("カテゴリ", category_options)
    keyword = st.text_input("式検索", placeholder="例: 圧力損失, LMTD")

    filtered = registry.search(keyword=keyword, category=None if selected_category == "すべて" else selected_category)
    if not filtered:
        st.info("条件に合う式がありません。")
        return

    filtered_ids = [item.formula_id for item in filtered]
    default_formula_id = st.session_state.get("calculator_formula_id", filtered_ids[0])
    if default_formula_id not in filtered_ids:
        default_formula_id = filtered_ids[0]
    selected_formula_id = st.selectbox(
        "計算式",
        options=filtered_ids,
        index=filtered_ids.index(default_formula_id),
        format_func=lambda value: f"{registry.get(value).name_ja} / {registry.get(value).category}",
        key="calculator_formula_id",
    )
    definition = registry.get(selected_formula_id)
    _apply_loaded_case_to_state(definition.formula_id)

    render_formula_information(definition)

    override_store: dict[str, dict[str, dict[str, Any]]] = st.session_state.setdefault("property_overrides", {})
    selected_substance = st.selectbox(
        "物性DBから候補を読み込む物質",
        options=[""] + [record.substance_id for record in property_service.search()],
        format_func=lambda value: "選択しない" if not value else property_service.get(value).name_ja,
        key=f"substance_{definition.formula_id}",
    )
    record = property_service.get(selected_substance) if selected_substance else None
    overrides = override_store.get(selected_substance, {}) if selected_substance else {}
    if record is not None:
        with st.expander("代表物性候補", expanded=False):
            st.dataframe(property_record_to_dataframe(record, overrides), use_container_width=True, hide_index=True)

    st.markdown("### 入力")
    for variable in definition.inputs:
        st.markdown(f"**{variable.label_ja}**")
        st.caption(variable.description)
        col_value, col_unit, col_basis = st.columns([2, 2, 1])
        default_value = float(st.session_state.get(f"input_{definition.formula_id}_{variable.key}", variable.default_value or 0.0))
        with col_value:
            st.number_input(
                f"{variable.label_ja} の値",
                value=default_value,
                key=f"input_{definition.formula_id}_{variable.key}",
                format="%.6f",
            )
        with col_unit:
            default_unit = st.session_state.get(f"unit_{definition.formula_id}_{variable.key}", variable.allowed_units[0] if variable.allowed_units else variable.standard_unit)
            unit_index = variable.allowed_units.index(default_unit) if default_unit in variable.allowed_units else 0
            st.selectbox(
                f"{variable.label_ja} の単位",
                options=variable.allowed_units,
                index=unit_index,
                key=f"unit_{definition.formula_id}_{variable.key}",
            )
        with col_basis:
            if variable.pressure_basis_supported:
                st.selectbox(
                    f"{variable.label_ja} の圧力基準",
                    options=["absolute", "gauge"],
                    format_func=lambda value: "絶対圧" if value == "absolute" else "ゲージ圧",
                    key=f"basis_{definition.formula_id}_{variable.key}",
                )

        if record is not None and variable.suggested_property_key:
            candidate = get_effective_property_entry(record, variable.suggested_property_key, overrides)
            if candidate is not None:
                candidate_value, candidate_unit, note = candidate
                st.caption(f"候補: {record.name_ja} / {candidate_value:g} {candidate_unit}（{note}）")
                if st.button(f"{variable.label_ja} に物性値を反映", key=f"apply_property_{definition.formula_id}_{variable.key}"):
                    _apply_property_to_input(
                        definition.formula_id,
                        variable.key,
                        candidate_value,
                        candidate_unit,
                        variable.allowed_units,
                        variable.standard_unit,
                        engine.unit_service,
                    )
                    st.success(f"{variable.label_ja} に候補値を反映しました。")

    st.markdown("### 出力単位")
    for variable in definition.outputs:
        default_output_unit = variable.output_preferred_unit or variable.standard_unit
        if f"output_unit_{definition.formula_id}_{variable.key}" not in st.session_state:
            st.session_state[f"output_unit_{definition.formula_id}_{variable.key}"] = default_output_unit
        st.selectbox(
            f"{variable.label_ja} の表示単位",
            options=variable.allowed_units,
            index=variable.allowed_units.index(st.session_state[f"output_unit_{definition.formula_id}_{variable.key}"]) if st.session_state[f"output_unit_{definition.formula_id}_{variable.key}"] in variable.allowed_units else 0,
            key=f"output_unit_{definition.formula_id}_{variable.key}",
        )

    if st.button("計算実行", type="primary"):
        input_values = {variable.key: float(st.session_state[f"input_{definition.formula_id}_{variable.key}"]) for variable in definition.inputs}
        input_units = {variable.key: str(st.session_state[f"unit_{definition.formula_id}_{variable.key}"]) for variable in definition.inputs}
        pressure_bases = {variable.key: str(st.session_state.get(f"basis_{definition.formula_id}_{variable.key}", "absolute")) for variable in definition.inputs if variable.pressure_basis_supported}
        output_units = {variable.key: str(st.session_state[f"output_unit_{definition.formula_id}_{variable.key}"]) for variable in definition.outputs}

        validation_messages = validate_inputs(definition, input_values, input_units)
        if any(message.level == "error" for message in validation_messages):
            render_messages(validation_messages)
        else:
            result = engine.calculate(
                definition.formula_id,
                input_values,
                input_units,
                pressure_bases,
                output_units,
                selected_properties={"selected_substance": selected_substance} if selected_substance else {},
                overridden_properties=overrides if record is not None else {},
            )
            st.session_state["last_result"] = result
            recent = st.session_state.setdefault("recent_formulas", [])
            recent.append(definition.formula_id)
            st.session_state["recent_formulas"] = recent[-20:]

    result = st.session_state.get("last_result")
    if result and result.formula_id == definition.formula_id:
        st.markdown("### 計算結果")
        render_messages(result.messages)
        st.dataframe(build_input_table(result, definition), use_container_width=True, hide_index=True)
        st.dataframe(build_output_table(result, definition), use_container_width=True, hide_index=True)
        st.info(result.interpretation or "結果は便覧レベルの簡易式に基づく参考値です。")

        col_json, col_csv = st.columns(2)
        with col_json:
            st.download_button("結果をJSON出力", data=result_to_json_bytes(result), file_name=f"{definition.formula_id}_result.json", mime="application/json")
        with col_csv:
            st.download_button("結果をCSV出力", data=result_to_csv_bytes(result, definition), file_name=f"{definition.formula_id}_result.csv", mime="text/csv")

        projects = project_service.list_projects()
        if projects:
            project_id = st.selectbox("案件へ保存", options=[project.project_id for project in projects], format_func=lambda value: project_service.get_project(value).name, key=f"save_project_{definition.formula_id}")
            if st.button("案件へ保存する", key=f"save_case_{definition.formula_id}"):
                project_service.save_result(project_id, result)
                st.success("案件へ保存しました。")
        else:
            st.caption("保存先案件がまだありません。案件管理画面で案件を作成してください。")

