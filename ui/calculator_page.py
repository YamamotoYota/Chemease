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
        st.session_state[f"solve_guess_{definition_id}_{key}"] = float(value)
    for key, value in loaded_case.get("input_units", {}).items():
        st.session_state[f"unit_{definition_id}_{key}"] = value
        st.session_state[f"solve_guess_unit_{definition_id}_{key}"] = value
    for key, value in loaded_case.get("pressure_bases", {}).items():
        st.session_state[f"basis_{definition_id}_{key}"] = value

    calculation_mode = loaded_case.get("calculation_mode", "forward")
    st.session_state[f"mode_{definition_id}"] = "任意変数を逆算" if calculation_mode == "solve" else "通常計算"
    solve_metadata = loaded_case.get("solve_metadata", {})
    if calculation_mode == "solve" and solve_metadata:
        target_key = str(solve_metadata.get("target_key", ""))
        specified_output_key = str(solve_metadata.get("specified_output_key", ""))
        st.session_state[f"target_{definition_id}"] = target_key
        if target_key:
            st.session_state[f"solve_unit_{definition_id}_{target_key}"] = str(solve_metadata.get("target_display_unit", ""))
        if specified_output_key:
            st.session_state[f"specified_output_{definition_id}_{specified_output_key}"] = float(solve_metadata.get("specified_output_value", 0.0))
            st.session_state[f"specified_output_unit_{definition_id}_{specified_output_key}"] = str(solve_metadata.get("specified_output_unit", ""))

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


def _render_variable_input(
    formula_id: str,
    variable,
    record,
    overrides,
    engine: CalculationEngine,
) -> None:
    st.markdown(f"**{variable.label_ja}**")
    st.caption(variable.description)
    col_value, col_unit, col_basis = st.columns([2, 2, 1])
    default_value = float(st.session_state.get(f"input_{formula_id}_{variable.key}", variable.default_value or 0.0))
    with col_value:
        st.number_input(
            f"{variable.label_ja} の値",
            value=default_value,
            key=f"input_{formula_id}_{variable.key}",
            format="%.6f",
        )
    with col_unit:
        default_unit = st.session_state.get(f"unit_{formula_id}_{variable.key}", variable.allowed_units[0] if variable.allowed_units else variable.standard_unit)
        unit_index = variable.allowed_units.index(default_unit) if default_unit in variable.allowed_units else 0
        st.selectbox(
            f"{variable.label_ja} の単位",
            options=variable.allowed_units,
            index=unit_index,
            key=f"unit_{formula_id}_{variable.key}",
        )
    with col_basis:
        if variable.pressure_basis_supported:
            st.selectbox(
                f"{variable.label_ja} の圧力基準",
                options=["absolute", "gauge"],
                format_func=lambda value: "絶対圧" if value == "absolute" else "ゲージ圧",
                key=f"basis_{formula_id}_{variable.key}",
            )

    if record is not None and variable.suggested_property_key:
        candidate = get_effective_property_entry(record, variable.suggested_property_key, overrides)
        if candidate is not None:
            candidate_value, candidate_unit, note = candidate
            st.caption(f"候補: {record.name_ja} / {candidate_value:g} {candidate_unit}（{note}）")
            if st.button(f"{variable.label_ja} に物性値を反映", key=f"apply_property_{formula_id}_{variable.key}"):
                _apply_property_to_input(
                    formula_id,
                    variable.key,
                    candidate_value,
                    candidate_unit,
                    variable.allowed_units,
                    variable.standard_unit,
                    engine.unit_service,
                )
                st.success(f"{variable.label_ja} に候補値を反映しました。")


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

    single_output = len(definition.outputs) == 1
    output_variable = definition.outputs[0] if single_output else None
    mode_options = ["通常計算"] + (["任意変数を逆算"] if single_output else [])
    calculation_mode = st.radio("計算モード", mode_options, horizontal=True, key=f"mode_{definition.formula_id}")

    target_key = output_variable.key if output_variable is not None else ""
    if calculation_mode == "任意変数を逆算" and output_variable is not None:
        variable_map = {item.key: item.label_ja for item in [*definition.inputs, output_variable]}
        candidate_keys = [item.key for item in definition.inputs] + [output_variable.key]
        target_key = st.selectbox(
            "求める変数",
            options=candidate_keys,
            index=candidate_keys.index(st.session_state.get(f"target_{definition.formula_id}", output_variable.key)) if st.session_state.get(f"target_{definition.formula_id}", output_variable.key) in candidate_keys else len(candidate_keys) - 1,
            format_func=lambda value: variable_map[value],
            key=f"target_{definition.formula_id}",
        )

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
    active_inputs = definition.inputs
    if calculation_mode == "任意変数を逆算" and output_variable is not None and target_key != output_variable.key:
        active_inputs = [item for item in definition.inputs if item.key != target_key]
        st.info(f"逆算対象: {next(item.label_ja for item in definition.inputs if item.key == target_key)}")

    for variable in active_inputs:
        _render_variable_input(definition.formula_id, variable, record, overrides, engine)

    if not single_output or calculation_mode == "通常計算" or (output_variable is not None and target_key == output_variable.key):
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
    elif output_variable is not None:
        st.markdown("### 指定する出力値")
        col_value, col_unit = st.columns([2, 2])
        default_specified_unit = st.session_state.get(f"specified_output_unit_{definition.formula_id}_{output_variable.key}", output_variable.output_preferred_unit or output_variable.standard_unit)
        with col_value:
            st.number_input(
                f"{output_variable.label_ja} の指定値",
                value=float(st.session_state.get(f"specified_output_{definition.formula_id}_{output_variable.key}", 0.0)),
                key=f"specified_output_{definition.formula_id}_{output_variable.key}",
                format="%.6f",
            )
        with col_unit:
            st.selectbox(
                f"{output_variable.label_ja} の指定単位",
                options=output_variable.allowed_units,
                index=output_variable.allowed_units.index(default_specified_unit) if default_specified_unit in output_variable.allowed_units else 0,
                key=f"specified_output_unit_{definition.formula_id}_{output_variable.key}",
            )

        target_variable = next(item for item in definition.inputs if item.key == target_key)
        st.markdown("### 逆算対象の表示・初期推定")
        col_display_unit, col_guess, col_guess_unit, col_basis = st.columns([2, 2, 2, 1])
        default_target_unit = st.session_state.get(f"solve_unit_{definition.formula_id}_{target_key}", target_variable.allowed_units[0] if target_variable.allowed_units else target_variable.standard_unit)
        default_guess_value = float(st.session_state.get(f"solve_guess_{definition.formula_id}_{target_key}", st.session_state.get(f"input_{definition.formula_id}_{target_key}", target_variable.default_value or 1.0)))
        default_guess_unit = st.session_state.get(f"solve_guess_unit_{definition.formula_id}_{target_key}", default_target_unit)
        with col_display_unit:
            st.selectbox(
                f"{target_variable.label_ja} の表示単位",
                options=target_variable.allowed_units,
                index=target_variable.allowed_units.index(default_target_unit) if default_target_unit in target_variable.allowed_units else 0,
                key=f"solve_unit_{definition.formula_id}_{target_key}",
            )
        with col_guess:
            st.number_input(
                f"{target_variable.label_ja} の初期推定値",
                value=default_guess_value,
                key=f"solve_guess_{definition.formula_id}_{target_key}",
                format="%.6f",
            )
        with col_guess_unit:
            st.selectbox(
                f"{target_variable.label_ja} の初期推定単位",
                options=target_variable.allowed_units,
                index=target_variable.allowed_units.index(default_guess_unit) if default_guess_unit in target_variable.allowed_units else 0,
                key=f"solve_guess_unit_{definition.formula_id}_{target_key}",
            )
        with col_basis:
            if target_variable.pressure_basis_supported:
                st.selectbox(
                    f"{target_variable.label_ja} の圧力基準",
                    options=["absolute", "gauge"],
                    format_func=lambda value: "絶対圧" if value == "absolute" else "ゲージ圧",
                    key=f"basis_{definition.formula_id}_{target_key}",
                )

    if st.button("計算実行", type="primary"):
        input_values = {variable.key: float(st.session_state[f"input_{definition.formula_id}_{variable.key}"]) for variable in active_inputs}
        input_units = {variable.key: str(st.session_state[f"unit_{definition.formula_id}_{variable.key}"]) for variable in active_inputs}
        pressure_bases = {variable.key: str(st.session_state.get(f"basis_{definition.formula_id}_{variable.key}", "absolute")) for variable in definition.inputs if variable.pressure_basis_supported and f"basis_{definition.formula_id}_{variable.key}" in st.session_state}

        if not single_output or calculation_mode == "通常計算" or (output_variable is not None and target_key == output_variable.key):
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
        else:
            target_variable = next(item for item in definition.inputs if item.key == target_key)
            try:
                result = engine.solve_for_variable(
                    definition.formula_id,
                    target_key,
                    input_values,
                    input_units,
                    float(st.session_state[f"specified_output_{definition.formula_id}_{output_variable.key}"]),
                    str(st.session_state[f"specified_output_unit_{definition.formula_id}_{output_variable.key}"]),
                    target_display_unit=str(st.session_state[f"solve_unit_{definition.formula_id}_{target_key}"]),
                    initial_guess_value=float(st.session_state[f"solve_guess_{definition.formula_id}_{target_key}"]),
                    initial_guess_unit=str(st.session_state[f"solve_guess_unit_{definition.formula_id}_{target_key}"]),
                    pressure_bases=pressure_bases,
                    selected_properties={"selected_substance": selected_substance} if selected_substance else {},
                    overridden_properties=overrides if record is not None else {},
                )
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.session_state["last_result"] = result

        recent = st.session_state.setdefault("recent_formulas", [])
        recent.append(definition.formula_id)
        st.session_state["recent_formulas"] = recent[-20:]

    result = st.session_state.get("last_result")
    if result and result.formula_id == definition.formula_id:
        st.markdown("### 計算結果")
        render_messages(result.messages)
        if result.calculation_mode == "solve":
            st.caption(
                f"逆算対象: {result.solve_metadata.get('target_label', result.solve_metadata.get('target_key', ''))}"
                f" / 指定出力: {result.solve_metadata.get('specified_output_label', '')}"
            )
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
