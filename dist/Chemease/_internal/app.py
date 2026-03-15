# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Chemease application entry point."""

from __future__ import annotations

import streamlit as st

from app_runtime import stop_application
from calculator_engine.engine import CalculationEngine
from formula_registry.custom_formula_service import get_custom_formula_service
from formula_registry.registry import get_registry
from project_storage.project_service import get_project_service
from property_database.property_service import get_property_service
from runtime_paths import describe_user_data_root
from ui.calculator_page import render_calculator_page
from ui.formula_page import render_formula_page
from ui.home import render_home_page
from ui.info_page import render_info_page
from ui.layout import inject_global_styles, render_note
from ui.project_page import render_project_page
from ui.property_page import render_property_page


def main() -> None:
    """Run the Streamlit application."""

    st.set_page_config(page_title="Chemease", page_icon="⚗️", layout="wide")
    inject_global_styles()

    registry = get_registry()
    custom_formula_service = get_custom_formula_service()
    property_service = get_property_service()
    project_service = get_project_service()
    engine = CalculationEngine(registry=registry)
    projects = project_service.list_projects()
    custom_formulas = custom_formula_service.list_custom_formulas()
    page_descriptions = {
        "ホーム": "全体像を確認し、どこから始めるかを決める画面です。",
        "計算": "式の前提を確認しながら、条件入力から結果保存まで進めます。",
        "式管理": "ユーザー定義の計算式を追加・編集して、ライブラリを育てる画面です。",
        "案件管理": "計算結果を案件ごとに整理し、ケースを読み戻して比較します。",
        "物性参照": "代表物性の確認、一時上書き、独自データの登録を行います。",
        "アプリ情報": "Chemease の使い方、前提、注意点をまとめて確認できます。",
    }

    if "page" not in st.session_state:
        st.session_state["page"] = "ホーム"

    with st.sidebar:
        st.title("Chemease")
        st.caption("化学工学の条件整理から計算、保存、再利用までを一つの流れで進めるためのワークスペースです。")
        page = st.radio("メニュー", ["ホーム", "計算", "式管理", "案件管理", "物性参照", "アプリ情報"], key="page")
        st.caption(page_descriptions[page])
        col1, col2 = st.columns(2)
        with col1:
            st.metric("搭載式", f"{len(registry.definitions)}")
        with col2:
            st.metric("案件", f"{len(projects)}")
        st.metric("ユーザー式", f"{len(custom_formulas)}")
        render_note(
            "基本の進め方",
            "迷ったときは、まずホームで式を探し、計算で条件を整えてから、必要な結果だけ案件へ保存してください。",
            bullets=[
                "物性値が必要なときは、計算画面か物性参照画面で候補を確認します。",
                "独自の計算式は式管理で追加すると、すぐ計算画面に反映されます。",
            ],
        )
        st.caption(f"共有データ保存先: {describe_user_data_root()}")
        render_note(
            "アプリの停止",
            "ローカルで起動している Chemease を終了したい場合は、下のボタンを押してください。ブラウザタブだけでなく、Streamlit サーバー自体を停止します。",
            tone="warn",
        )
        if st.button("アプリを停止する", use_container_width=True):
            stop_application()
            st.stop()

    if page == "ホーム":
        render_home_page(registry)
    elif page == "計算":
        render_calculator_page(registry, engine, property_service, project_service)
    elif page == "式管理":
        render_formula_page(custom_formula_service, registry)
    elif page == "案件管理":
        render_project_page(project_service)
    elif page == "物性参照":
        render_property_page(property_service)
    else:
        render_info_page()


if __name__ == "__main__":
    main()

