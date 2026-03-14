# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Calculator page."""

from __future__ import annotations

from typing import Any

import streamlit as st

from calculator_engine.engine import CalculationEngine
from formula_registry.models import CalculationResult, FormulaDefinition, FormulaVariable
from formula_registry.registry import FormulaRegistry
from project_storage.project_service import ProjectService
from property_database.property_service import PropertyService
from reporting.exporters import result_to_csv_bytes, result_to_json_bytes
from reporting.formatters import build_input_table, build_output_table
from ui.components import get_effective_property_entry, property_record_to_dataframe, render_formula_information, render_messages
from ui.layout import render_empty_state, render_note, render_page_header, render_section_header
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
    variable: FormulaVariable,
    record,
    overrides,
    engine: CalculationEngine,
) -> None:
    st.markdown(f"**{variable.label_ja}**")
    st.caption(variable.description)
    if variable.default_value is not None:
        st.caption(f"初期値の目安: {variable.default_value:g} {variable.standard_unit}")

    col_value, col_unit, col_basis = st.columns([2, 2, 1])
    default_value = float(st.session_state.get(f"input_{formula_id}_{variable.key}", variable.default_value or 0.0))
    with col_value:
        st.number_input(
            "入力値",
            value=default_value,
            key=f"input_{formula_id}_{variable.key}",
            format="%.6f",
            help="説明欄の意味を確認したうえで、実測値や設計条件を入力してください。",
        )
    with col_unit:
        default_unit = st.session_state.get(f"unit_{formula_id}_{variable.key}", variable.allowed_units[0] if variable.allowed_units else variable.standard_unit)
        unit_index = variable.allowed_units.index(default_unit) if default_unit in variable.allowed_units else 0
        st.selectbox(
            "入力単位",
            options=variable.allowed_units,
            index=unit_index,
            key=f"unit_{formula_id}_{variable.key}",
            help="内部では標準単位へ換算して計算するため、手元の単位のまま入力できます。",
        )
    with col_basis:
        if variable.pressure_basis_supported:
            st.selectbox(
                "圧力基準",
                options=["absolute", "gauge"],
                format_func=lambda value: "絶対圧" if value == "absolute" else "ゲージ圧",
                key=f"basis_{formula_id}_{variable.key}",
                help="圧力に関する値だけ表示されます。絶対圧かゲージ圧かを明示してください。",
            )

    if record is not None and variable.suggested_property_key:
        candidate = get_effective_property_entry(record, variable.suggested_property_key, overrides)
        if candidate is not None:
            candidate_value, candidate_unit, note = candidate
            st.caption(f"候補値: {record.name_ja} / {candidate_value:g} {candidate_unit}（{note}）")
            if st.button(f"{variable.label_ja} に候補値を反映する", key=f"apply_property_{formula_id}_{variable.key}", use_container_width=True):
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


def _render_formula_selector(registry: FormulaRegistry) -> FormulaDefinition | None:
    render_section_header(
        "1. 式を選ぶ",
        "カテゴリで大きく絞り、必要に応じてキーワードでさらに探してください。式を選ぶと、その下に前提条件と入力欄が表示されます。",
    )
    col_category, col_keyword = st.columns([1, 2])
    category_options = ["すべて", *registry.list_categories()]
    with col_category:
        selected_category = st.selectbox(
            "カテゴリ",
            category_options,
            help="計算の分野が分かっている場合は、先にカテゴリで絞ると候補を見つけやすくなります。",
        )
    with col_keyword:
        keyword = st.text_input(
            "キーワード検索",
            placeholder="例: 圧力損失, LMTD, Reynolds, 蒸発",
            help="日本語名、英語名、略語、概要文から絞り込めます。",
        )

    filtered = registry.search(keyword=keyword, category=None if selected_category == "すべて" else selected_category)
    if not filtered:
        render_empty_state("条件に合う式がありません。", "キーワードを短くするか、カテゴリを広げて再度探してください。")
        return None

    filtered_ids = [item.formula_id for item in filtered]
    default_formula_id = st.session_state.get("calculator_formula_id", filtered_ids[0])
    if default_formula_id not in filtered_ids:
        default_formula_id = filtered_ids[0]

    selected_formula_id = st.selectbox(
        "使う式",
        options=filtered_ids,
        index=filtered_ids.index(default_formula_id),
        format_func=lambda value: f"{registry.get(value).name_ja} / {registry.get(value).category}",
        key="calculator_formula_id",
        help="式名の横にカテゴリも表示しています。似た式がある場合は、まずカテゴリ違いを確認してください。",
    )
    return registry.get(selected_formula_id)


def _render_calculation_mode(definition: FormulaDefinition) -> tuple[str, str, FormulaVariable | None]:
    render_section_header(
        "2. 計算方法を決める",
        "通常計算は入力から出力を求めます。逆算は、欲しい出力値を先に決めて必要な入力値を推定するモードです。",
    )
    single_output = len(definition.outputs) == 1
    output_variable = definition.outputs[0] if single_output else None
    mode_options = ["通常計算"] + (["任意変数を逆算"] if single_output else [])
    calculation_mode = st.radio("計算モード", mode_options, horizontal=True, key=f"mode_{definition.formula_id}")

    if not single_output:
        render_note("この式で使えるモード", "この式は出力が複数あるため、通常計算のみ利用できます。")
        return calculation_mode, "", output_variable

    target_key = output_variable.key
    if calculation_mode == "任意変数を逆算" and output_variable is not None:
        render_note(
            "逆算モードの考え方",
            "まず欲しい出力値を指定し、その結果に合う入力値を一つ選んで求めます。初期推定値は、だいたいの想定値を入れると収束しやすくなります。",
            bullets=[
                "入力変数を選ぶと逆算になります。",
                "出力変数を選ぶと通常計算と同じ挙動です。",
            ],
        )
        variable_map = {item.key: item.label_ja for item in [*definition.inputs, output_variable]}
        candidate_keys = [item.key for item in definition.inputs] + [output_variable.key]
        default_target_key = st.session_state.get(f"target_{definition.formula_id}", output_variable.key)
        target_key = st.selectbox(
            "何を求めたいか",
            options=candidate_keys,
            index=candidate_keys.index(default_target_key) if default_target_key in candidate_keys else len(candidate_keys) - 1,
            format_func=lambda value: variable_map[value],
            key=f"target_{definition.formula_id}",
            help="通常は入力変数を選びます。出力変数を選ぶと、通常計算と同じ扱いになります。",
        )

    return calculation_mode, target_key, output_variable


def _render_property_selector(definition_id: str, property_service: PropertyService):
    render_section_header(
        "3. 物性候補を確認する",
        "物性値が必要な変数には、ここで選んだ物質の代表値を下書きとして反映できます。使わない場合は未選択のままで問題ありません。",
    )
    property_keyword = st.text_input(
        "物質名で候補を絞る",
        key=f"property_search_{definition_id}",
        placeholder="例: 水, air, ethanol, toluene",
        help="物質名、ID、別名から絞り込めます。",
    )
    matched_records = property_service.search(property_keyword)
    current_substance = st.session_state.get(f"substance_{definition_id}", "")
    substance_options = [""] + [record.substance_id for record in matched_records]
    if current_substance and current_substance not in substance_options:
        substance_options.append(current_substance)

    if property_keyword and not matched_records:
        render_empty_state("候補になる物質が見つかりません。", "表記を変えて再検索するか、物性参照画面で独自レコードを登録してください。")

    selected_substance = st.selectbox(
        "候補に使う物質",
        options=substance_options,
        format_func=lambda value: "選択しない" if not value else property_service.get(value).name_ja,
        key=f"substance_{definition_id}",
        help="選択すると、その物質の代表値を確認でき、入力欄へ個別反映できます。",
    )
    record = property_service.get(selected_substance) if selected_substance else None
    override_store: dict[str, dict[str, dict[str, Any]]] = st.session_state.setdefault("property_overrides", {})
    overrides = override_store.get(selected_substance, {}) if selected_substance else {}

    if record is not None:
        with st.expander("代表物性候補を確認する", expanded=False):
            st.caption(f"適用温度範囲: {record.temperature_range or '未設定'} / 出典: {record.source or '未設定'}")
            if record.notes:
                st.caption(record.notes)
            st.dataframe(property_record_to_dataframe(record, overrides), use_container_width=True, hide_index=True)

    return selected_substance, record, overrides


def _render_input_section(
    definition: FormulaDefinition,
    calculation_mode: str,
    target_key: str,
    output_variable: FormulaVariable | None,
    record,
    overrides,
    engine: CalculationEngine,
) -> list[FormulaVariable]:
    render_section_header(
        "4. 条件を入力する",
        "各入力欄の説明を確認してから値と単位を入力してください。物性候補を使う場合も、そのまま確定せず設計条件に合うかを確認する運用をおすすめします。",
    )
    active_inputs = definition.inputs
    if calculation_mode == "任意変数を逆算" and output_variable is not None and target_key != output_variable.key:
        active_inputs = [item for item in definition.inputs if item.key != target_key]
        target_label = next(item.label_ja for item in definition.inputs if item.key == target_key)
        render_note("逆算の対象", f"「{target_label}」はこのあと逆算で求めるため、ここでは入力不要です。")

    for variable in active_inputs:
        with st.container(border=True):
            _render_variable_input(definition.formula_id, variable, record, overrides, engine)

    return active_inputs


def _render_forward_output_units(definition: FormulaDefinition) -> None:
    render_section_header(
        "5. 出力の表示単位を決める",
        "計算自体は標準単位で行い、ここで指定した単位で結果を表示します。報告書に近い単位へ合わせておくと確認しやすくなります。",
    )
    for variable in definition.outputs:
        default_output_unit = variable.output_preferred_unit or variable.standard_unit
        state_key = f"output_unit_{definition.formula_id}_{variable.key}"
        if state_key not in st.session_state:
            st.session_state[state_key] = default_output_unit
        st.selectbox(
            f"{variable.label_ja} の表示単位",
            options=variable.allowed_units,
            index=variable.allowed_units.index(st.session_state[state_key]) if st.session_state[state_key] in variable.allowed_units else 0,
            key=state_key,
            help="表示上の単位だけを切り替えます。計算ロジックの内部単位は固定です。",
        )


def _render_solve_configuration(
    definition: FormulaDefinition,
    target_key: str,
    output_variable: FormulaVariable,
) -> None:
    render_section_header(
        "5. 逆算条件を指定する",
        "ここでは、欲しい出力値と、逆算対象の表示単位・初期推定値を設定します。初期推定値は、あり得る範囲の値を入れると逆算が安定しやすくなります。",
    )
    col_value, col_unit = st.columns([2, 2])
    default_specified_unit = st.session_state.get(
        f"specified_output_unit_{definition.formula_id}_{output_variable.key}",
        output_variable.output_preferred_unit or output_variable.standard_unit,
    )
    with col_value:
        st.number_input(
            f"{output_variable.label_ja} の指定値",
            value=float(st.session_state.get(f"specified_output_{definition.formula_id}_{output_variable.key}", 0.0)),
            key=f"specified_output_{definition.formula_id}_{output_variable.key}",
            format="%.6f",
            help="最終的に得たい出力値を入力します。",
        )
    with col_unit:
        st.selectbox(
            f"{output_variable.label_ja} の指定単位",
            options=output_variable.allowed_units,
            index=output_variable.allowed_units.index(default_specified_unit) if default_specified_unit in output_variable.allowed_units else 0,
            key=f"specified_output_unit_{definition.formula_id}_{output_variable.key}",
            help="指定値の単位です。表示単位ではなく、逆算条件そのものになります。",
        )

    if target_key == output_variable.key:
        render_note("現在の設定", "出力変数が選ばれているため、この実行は通常計算と同じ扱いになります。")
        _render_forward_output_units(definition)
        return

    target_variable = next(item for item in definition.inputs if item.key == target_key)
    col_display_unit, col_guess, col_guess_unit, col_basis = st.columns([2, 2, 2, 1])
    default_target_unit = st.session_state.get(
        f"solve_unit_{definition.formula_id}_{target_key}",
        target_variable.allowed_units[0] if target_variable.allowed_units else target_variable.standard_unit,
    )
    default_guess_value = float(
        st.session_state.get(
            f"solve_guess_{definition.formula_id}_{target_key}",
            st.session_state.get(f"input_{definition.formula_id}_{target_key}", target_variable.default_value or 1.0),
        )
    )
    default_guess_unit = st.session_state.get(f"solve_guess_unit_{definition.formula_id}_{target_key}", default_target_unit)

    with col_display_unit:
        st.selectbox(
            f"{target_variable.label_ja} の表示単位",
            options=target_variable.allowed_units,
            index=target_variable.allowed_units.index(default_target_unit) if default_target_unit in target_variable.allowed_units else 0,
            key=f"solve_unit_{definition.formula_id}_{target_key}",
            help="逆算して得られた値をどの単位で表示するかを指定します。",
        )
    with col_guess:
        st.number_input(
            f"{target_variable.label_ja} の初期推定値",
            value=default_guess_value,
            key=f"solve_guess_{definition.formula_id}_{target_key}",
            format="%.6f",
            help="逆算の開始点です。現実的な値に近いほど収束しやすくなります。",
        )
    with col_guess_unit:
        st.selectbox(
            f"{target_variable.label_ja} の初期推定単位",
            options=target_variable.allowed_units,
            index=target_variable.allowed_units.index(default_guess_unit) if default_guess_unit in target_variable.allowed_units else 0,
            key=f"solve_guess_unit_{definition.formula_id}_{target_key}",
            help="初期推定値に対する単位です。",
        )
    with col_basis:
        if target_variable.pressure_basis_supported:
            st.selectbox(
                f"{target_variable.label_ja} の圧力基準",
                options=["absolute", "gauge"],
                format_func=lambda value: "絶対圧" if value == "absolute" else "ゲージ圧",
                key=f"basis_{definition.formula_id}_{target_key}",
                help="圧力変数を逆算する場合のみ指定が必要です。",
            )


def _collect_input_payload(definition: FormulaDefinition, active_inputs: list[FormulaVariable]) -> tuple[dict[str, float], dict[str, str], dict[str, str]]:
    formula_id = definition.formula_id
    input_values = {variable.key: float(st.session_state[f"input_{formula_id}_{variable.key}"]) for variable in active_inputs}
    input_units = {variable.key: str(st.session_state[f"unit_{formula_id}_{variable.key}"]) for variable in active_inputs}
    pressure_bases = {
        variable.key: str(st.session_state.get(f"basis_{formula_id}_{variable.key}", "absolute"))
        for variable in definition.inputs
        if variable.pressure_basis_supported and f"basis_{formula_id}_{variable.key}" in st.session_state
    }
    return input_values, input_units, pressure_bases


def _build_forward_result(
    definition: FormulaDefinition,
    engine: CalculationEngine,
    active_inputs: list[FormulaVariable],
    selected_substance: str,
    overrides,
) -> CalculationResult | None:
    input_values, input_units, pressure_bases = _collect_input_payload(definition, active_inputs)
    output_units = {variable.key: str(st.session_state[f"output_unit_{definition.formula_id}_{variable.key}"]) for variable in definition.outputs}
    validation_messages = validate_inputs(definition, input_values, input_units)
    if any(message.level == "error" for message in validation_messages):
        render_messages(validation_messages)
        return None

    try:
        return engine.calculate(
            definition.formula_id,
            input_values,
            input_units,
            pressure_bases,
            output_units,
            selected_properties={"selected_substance": selected_substance} if selected_substance else {},
            overridden_properties=overrides if selected_substance else {},
        )
    except ValueError as exc:
        st.error(str(exc))
        return None


def _build_solve_result(
    definition: FormulaDefinition,
    engine: CalculationEngine,
    active_inputs: list[FormulaVariable],
    target_key: str,
    output_variable: FormulaVariable,
    selected_substance: str,
    overrides,
) -> CalculationResult | None:
    input_values, input_units, pressure_bases = _collect_input_payload(definition, active_inputs)
    try:
        return engine.solve_for_variable(
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
            overridden_properties=overrides if selected_substance else {},
        )
    except ValueError as exc:
        st.error(str(exc))
        return None


def _append_recent_formula(formula_id: str) -> None:
    recent = st.session_state.setdefault("recent_formulas", [])
    recent.append(formula_id)
    st.session_state["recent_formulas"] = recent[-20:]


def _render_result_section(result: CalculationResult, definition: FormulaDefinition, project_service: ProjectService) -> None:
    render_section_header(
        "7. 結果を確認する",
        "出力値だけでなく、内部換算後の入力値や警告もあわせて確認してください。案件へ保存すると、あとで同じ条件を再読込できます。",
    )
    render_messages(result.messages)
    if result.calculation_mode == "solve":
        st.caption(
            f"逆算対象: {result.solve_metadata.get('target_label', result.solve_metadata.get('target_key', ''))}"
            f" / 指定出力: {result.solve_metadata.get('specified_output_label', '')}"
        )

    col_inputs, col_outputs = st.columns(2)
    with col_inputs:
        st.markdown("**入力条件の整理**")
        st.dataframe(build_input_table(result, definition), use_container_width=True, hide_index=True)
    with col_outputs:
        st.markdown("**計算結果**")
        st.dataframe(build_output_table(result, definition), use_container_width=True, hide_index=True)

    render_note(
        "結果の読み方",
        result.interpretation or "結果は便覧レベルの簡易式に基づく参考値です。前提条件から外れる場合は、より詳細な設計計算で再確認してください。",
        tone="info",
    )

    col_json, col_csv = st.columns(2)
    with col_json:
        st.download_button(
            "結果を JSON で出力",
            data=result_to_json_bytes(result),
            file_name=f"{definition.formula_id}_result.json",
            mime="application/json",
            use_container_width=True,
        )
    with col_csv:
        st.download_button(
            "結果を CSV で出力",
            data=result_to_csv_bytes(result, definition),
            file_name=f"{definition.formula_id}_result.csv",
            mime="text/csv",
            use_container_width=True,
        )

    render_section_header("案件へ保存する", "案件を先に作成しておくと、ここから結果をケースとして保存できます。")
    projects = project_service.list_projects()
    if not projects:
        render_empty_state("保存先案件がありません。", "先に案件管理画面で案件を作成すると、この結果を保存できるようになります。")
        return

    project_id = st.selectbox(
        "保存先案件",
        options=[project.project_id for project in projects],
        format_func=lambda value: project_service.get_project(value).name,
        key=f"save_project_{definition.formula_id}",
        help="案件ごとにケースを蓄積できます。あとから案件管理画面で再読込や複製が可能です。",
    )
    if st.button("この結果を案件へ保存する", key=f"save_case_{definition.formula_id}", use_container_width=True):
        project_service.save_result(project_id, result)
        st.success("案件へ保存しました。")


def render_calculator_page(
    registry: FormulaRegistry,
    engine: CalculationEngine,
    property_service: PropertyService,
    project_service: ProjectService,
) -> None:
    """Render the calculation page."""

    render_page_header(
        "計算",
        "この画面では、式の前提を確認しながら条件入力、物性候補の反映、結果の保存までを順に進められます。迷った場合は、上から順に見ていく使い方をおすすめします。",
        eyebrow="Calculator",
        steps=[
            ("式を確認する", "まず式の説明と適用条件を読みます。"),
            ("条件を入力する", "値、単位、物性候補、圧力基準を整えます。"),
            ("結果を整理する", "出力を確認し、必要なら案件へ保存します。"),
        ],
    )

    definition = _render_formula_selector(registry)
    if definition is None:
        return

    _apply_loaded_case_to_state(definition.formula_id)
    render_formula_information(definition)

    calculation_mode, target_key, output_variable = _render_calculation_mode(definition)
    selected_substance, record, overrides = _render_property_selector(definition.formula_id, property_service)
    active_inputs = _render_input_section(definition, calculation_mode, target_key, output_variable, record, overrides, engine)

    single_output = len(definition.outputs) == 1
    if not single_output or calculation_mode == "通常計算" or (output_variable is not None and target_key == output_variable.key):
        _render_forward_output_units(definition)
    elif output_variable is not None:
        _render_solve_configuration(definition, target_key, output_variable)

    render_section_header(
        "6. 計算を実行する",
        "入力内容を見直したら実行してください。エラーや警告がある場合は、その場で理由を表示します。",
    )
    if st.button("計算を実行する", type="primary", use_container_width=True):
        result: CalculationResult | None = None
        if not single_output or calculation_mode == "通常計算" or (output_variable is not None and target_key == output_variable.key):
            result = _build_forward_result(definition, engine, active_inputs, selected_substance, overrides)
        elif output_variable is not None:
            result = _build_solve_result(definition, engine, active_inputs, target_key, output_variable, selected_substance, overrides)

        if result is not None:
            st.session_state["last_result"] = result
            _append_recent_formula(definition.formula_id)

    result = st.session_state.get("last_result")
    if result and result.formula_id == definition.formula_id:
        _render_result_section(result, definition, project_service)
