# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Chemease application entry point."""

from __future__ import annotations

import streamlit as st

from calculator_engine.engine import CalculationEngine
from formula_registry.registry import get_registry
from project_storage.project_service import get_project_service
from property_database.property_service import get_property_service
from ui.calculator_page import render_calculator_page
from ui.home import render_home_page
from ui.info_page import render_info_page
from ui.project_page import render_project_page
from ui.property_page import render_property_page


def main() -> None:
    """Run the Streamlit application."""

    st.set_page_config(page_title="Chemease", page_icon="⚗️", layout="wide")

    registry = get_registry()
    property_service = get_property_service()
    project_service = get_project_service()
    engine = CalculationEngine(registry=registry)

    if "page" not in st.session_state:
        st.session_state["page"] = "ホーム"

    with st.sidebar:
        st.title("Chemease")
        page = st.radio("メニュー", ["ホーム", "計算", "案件管理", "物性参照", "アプリ情報"], key="page")
        st.caption(f"搭載式数: {len(registry.definitions)}")

    if page == "ホーム":
        render_home_page(registry)
    elif page == "計算":
        render_calculator_page(registry, engine, property_service, project_service)
    elif page == "案件管理":
        render_project_page(project_service)
    elif page == "物性参照":
        render_property_page(property_service)
    else:
        render_info_page()


if __name__ == "__main__":
    main()

