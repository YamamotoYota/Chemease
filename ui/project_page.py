"""Project management page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from project_storage.project_service import ProjectService


def render_project_page(project_service: ProjectService) -> None:
    """Render project and case management UI."""

    st.title("案件管理")

    with st.form("new_project_form"):
        st.markdown("### 案件新規作成")
        project_name = st.text_input("案件名")
        project_description = st.text_area("説明")
        submitted = st.form_submit_button("案件を作成")
    if submitted:
        if project_name.strip():
            project_service.create_project(project_name.strip(), project_description.strip())
            st.success("案件を作成しました。")
        else:
            st.error("案件名を入力してください。")

    projects = project_service.list_projects()
    if not projects:
        st.info("案件がまだありません。上から新規作成してください。")
        return

    selected_project_id = st.selectbox("案件一覧", options=[project.project_id for project in projects], format_func=lambda value: project_service.get_project(value).name)
    project = project_service.get_project(selected_project_id)
    st.caption(project.description or "説明なし")

    cases = project_service.list_cases(selected_project_id)
    st.markdown("### 保存済みケース一覧")
    if not cases:
        st.caption("この案件にはまだケースがありません。計算画面から保存してください。")
        return

    comparison_rows: list[dict[str, object]] = []
    for case in cases:
        with st.expander(f"{case.formula_name} / {case.updated_at.strftime('%Y-%m-%d %H:%M')}"):
            st.json(
                {
                    "formula_id": case.formula_id,
                    "input_values": case.input_values,
                    "input_units": case.input_units,
                    "normalized_inputs": case.normalized_inputs,
                    "output_values": case.output_values,
                    "warnings": case.warnings,
                },
                expanded=False,
            )
            col1, col2 = st.columns(2)
            with col1:
                if st.button("ケース再読込", key=f"load_case_{case.case_id}"):
                    st.session_state["loaded_case"] = case.model_dump(mode="json")
                    st.session_state["calculator_formula_id"] = case.formula_id
                    st.session_state["page"] = "計算"
            with col2:
                if st.button("ケース複製", key=f"copy_case_{case.case_id}"):
                    project_service.duplicate_case(case.case_id)
                    st.success("ケースを複製しました。")
            comparison_rows.append(
                {
                    "case_id": case.case_id,
                    "ケース": case.formula_name,
                    **{f"出力:{key}": value for key, value in case.output_values.items()},
                }
            )

    st.markdown("### ケース比較（基礎表示）")
    selected_case_ids = st.multiselect("比較対象ケース", options=[case.case_id for case in cases], format_func=lambda value: next(case.formula_name for case in cases if case.case_id == value))
    if selected_case_ids:
        frame = pd.DataFrame([row for row in comparison_rows if row["case_id"] in selected_case_ids])
        st.dataframe(frame, use_container_width=True, hide_index=True)

