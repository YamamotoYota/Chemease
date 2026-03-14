# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Project management page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from project_storage.project_service import ProjectService
from ui.layout import render_empty_state, render_metric_cards, render_note, render_page_header, render_section_header


def render_project_page(project_service: ProjectService) -> None:
    """Render project and case management UI."""

    projects = project_service.list_projects()
    all_cases = [case for project in projects for case in project_service.list_cases(project.project_id)]

    render_page_header(
        "案件管理",
        "計算結果を案件ごとに整理し、あとで読み返せる形にまとめる画面です。案件は保存箱、ケースは各計算のスナップショットという考え方で使うと整理しやすくなります。",
        eyebrow="Projects",
        steps=[
            ("案件を作る", "装置、テーマ、検討単位ごとに保存先を用意します。"),
            ("結果を保存する", "計算画面から案件へケースを追加します。"),
            ("比較して再利用する", "読み戻しや複製で検討条件を展開します。"),
        ],
    )
    render_metric_cards(
        [
            ("案件数", str(len(projects)), "案件は保存先の単位です。"),
            ("保存ケース数", str(len(all_cases)), "案件に紐づく計算結果の累計です。"),
            ("再利用方法", "再読込・複製対応", "過去条件を起点に再計算できます。"),
        ]
    )

    render_note(
        "運用の目安",
        "案件名は、あとから見たときに用途が分かる名前にしてください。案件説明には装置名、検討目的、対象流体などを書いておくと検索しやすくなります。",
        bullets=[
            "日次試算よりも、テーマ単位や装置単位で案件を分けると見返しやすくなります。",
            "ケース比較は、同じ案件内に近い条件をまとめておくと効果的です。",
        ],
    )

    render_section_header("案件を新規作成する", "まず保存先となる案件を作成します。計算結果の保存は計算画面から行います。")
    with st.form("new_project_form"):
        project_name = st.text_input("案件名", help="例: 吸収塔圧損検討、熱交換器概算、反応槽スケールアップ")
        project_description = st.text_area("説明", help="背景、対象装置、対象物質、検討の狙いなどを書いておくと再利用しやすくなります。")
        submitted = st.form_submit_button("案件を作成する", use_container_width=True)
    if submitted:
        if project_name.strip():
            project_service.create_project(project_name.strip(), project_description.strip())
            st.success("案件を作成しました。")
            st.rerun()
        else:
            st.error("案件名を入力してください。")

    if not projects:
        render_empty_state("案件がまだありません。", "上のフォームから案件を作成すると、計算画面で保存先として選べるようになります。")
        return

    render_section_header("案件を選んで内容を確認する", "案件ごとに保存済みケースを確認できます。")
    selected_project_id = st.selectbox(
        "案件一覧",
        options=[project.project_id for project in projects],
        format_func=lambda value: project_service.get_project(value).name,
        help="案件を選ぶと、その下に保存済みケースが表示されます。",
    )
    project = project_service.get_project(selected_project_id)
    st.caption(project.description or "この案件には説明がまだありません。")

    cases = project_service.list_cases(selected_project_id)
    render_metric_cards(
        [
            ("選択中の案件", project.name, "現在表示している案件です。"),
            ("ケース数", str(len(cases)), "この案件に保存されている計算結果です。"),
            ("最終更新", project.updated_at.strftime("%Y-%m-%d %H:%M"), "案件情報の最終更新日時です。"),
        ]
    )

    render_section_header("保存済みケース", "ケースの中身を確認し、必要に応じて計算画面へ再読込したり、複製して比較用の起点にできます。")
    if not cases:
        render_empty_state("この案件にはまだケースがありません。", "計算画面で結果を出したあと、「案件へ保存する」からこの案件を選択してください。")
        return

    comparison_rows: list[dict[str, object]] = []
    for case in cases:
        mode_label = "逆算" if case.calculation_mode == "solve" else "通常"
        with st.expander(f"{case.formula_name} / {mode_label} / {case.updated_at.strftime('%Y-%m-%d %H:%M')}"):
            st.caption("計算条件と出力値のスナップショットです。再読込すると計算画面へ条件を戻せます。")
            st.json(
                {
                    "formula_id": case.formula_id,
                    "calculation_mode": case.calculation_mode,
                    "input_values": case.input_values,
                    "input_units": case.input_units,
                    "normalized_inputs": case.normalized_inputs,
                    "output_values": case.output_values,
                    "solve_metadata": case.solve_metadata,
                    "warnings": case.warnings,
                },
                expanded=False,
            )
            col1, col2 = st.columns(2)
            with col1:
                if st.button("計算画面へ再読込する", key=f"load_case_{case.case_id}", use_container_width=True):
                    st.session_state["loaded_case"] = case.model_dump(mode="json")
                    st.session_state["calculator_formula_id"] = case.formula_id
                    st.session_state["page"] = "計算"
            with col2:
                if st.button("このケースを複製する", key=f"copy_case_{case.case_id}", use_container_width=True):
                    project_service.duplicate_case(case.case_id)
                    st.success("ケースを複製しました。")
                    st.rerun()
            comparison_rows.append(
                {
                    "case_id": case.case_id,
                    "ケース": case.formula_name,
                    "モード": mode_label,
                    "更新日時": case.updated_at.strftime("%Y-%m-%d %H:%M"),
                    **{f"出力:{key}": value for key, value in case.output_values.items()},
                }
            )

    render_section_header("ケース比較", "複数ケースを並べて、出力値の違いをざっと確認できます。")
    selected_case_ids = st.multiselect(
        "比較対象ケース",
        options=[case.case_id for case in cases],
        format_func=lambda value: next(case.formula_name for case in cases if case.case_id == value),
        help="同じ案件内で比較したいケースを複数選択してください。",
    )
    if selected_case_ids:
        frame = pd.DataFrame([row for row in comparison_rows if row["case_id"] in selected_case_ids])
        st.dataframe(frame, use_container_width=True, hide_index=True)
    else:
        render_empty_state("まだ比較対象が選ばれていません。", "2 件以上のケースを選ぶと、出力を表形式で比較できます。")
