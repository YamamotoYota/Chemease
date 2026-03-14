# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Home page."""

from __future__ import annotations

import streamlit as st

from formula_registry.registry import FormulaRegistry
from ui.layout import render_empty_state, render_metric_cards, render_note, render_page_header, render_section_header


def render_home_page(registry: FormulaRegistry) -> None:
    """Render the home dashboard."""

    render_page_header(
        "Chemease",
        "Chemease は、式の意味と前提を確認しながら条件を整理し、計算結果を案件へ残せる化学工学向けアプリです。初めて使う場合でも、下の流れに沿って進めれば必要な画面に迷わずたどり着けます。",
        eyebrow="Home",
        steps=[
            ("1. 式を探す", "検索やカテゴリから目的の計算式を見つけます。"),
            ("2. 条件を整える", "単位、物性値、圧力基準を確認して計算条件を入力します。"),
            ("3. 結果を残す", "必要な結果だけ案件へ保存し、あとで読み返せる形に整理します。"),
        ],
    )

    categories = registry.list_categories()
    render_metric_cards(
        [
            ("搭載カテゴリ", f"{len(categories)} 区分", "流体、伝熱、反応など主要領域を横断して探せます。"),
            ("搭載式", f"{len(registry.definitions)} 式", "概要と前提を確認しながら使えるよう整理しています。"),
            ("検索方法", "日本語・英語対応", "式名、略語、キーワードのどれからでも絞り込み可能です。"),
        ]
    )

    render_note(
        "最初に確認すると迷いにくい点",
        "Chemease の計算は、式の適用条件と単位の確認を前提にしています。まずは式の説明を読み、入力欄の下に出る補足を確認してから実行する使い方をおすすめします。",
        bullets=[
            "カテゴリが分かる場合はカテゴリから絞ると、近い式の比較がしやすくなります。",
            "必要な物性がある場合は計算画面の物性候補を使うと入力の手間を減らせます。",
        ],
    )

    render_section_header("式を検索して計算へ進む", "式名が曖昧でも、用途や現象名から探せるようにしています。")
    search_keyword = st.text_input(
        "式を検索",
        placeholder="例: Reynolds, 顕熱, 理想気体, 圧力損失",
        help="日本語名、英語名、略語、要約文のキーワードから検索できます。",
    )
    if search_keyword:
        matches = registry.search(search_keyword)
        if matches:
            for definition in matches[:10]:
                with st.container(border=True):
                    col_text, col_action = st.columns([4, 1])
                    with col_text:
                        st.markdown(f"**{definition.name_ja}**")
                        st.caption(f"{definition.category} | {definition.summary}")
                    with col_action:
                        if st.button("この式を使う", key=f"home_open_{definition.formula_id}", use_container_width=True):
                            st.session_state["calculator_formula_id"] = definition.formula_id
                            st.session_state["page"] = "計算"
        else:
            render_empty_state("該当する式が見つかりませんでした。", "別のキーワードに変えるか、カテゴリ一覧から近い分野の式を探してください。")

    render_section_header("カテゴリから選ぶ", "計算の種類が決まっている場合は、ここから全体像をつかめます。")
    count_columns = st.columns(min(4, max(1, len(categories))))
    for index, category in enumerate(categories):
        with count_columns[index % len(count_columns)]:
            count = len(registry.search(category=category))
            st.metric(category, f"{count} 式")

    render_section_header("よく使う計算", "代表的な計算から始めたい場合はこちらが近道です。")
    popular_ids = [
        "fluid_reynolds_number",
        "fluid_darcy_weisbach_pressure_drop",
        "heat_sensible_heat",
        "heat_lmtd",
        "basic_ideal_gas_moles",
    ]
    popular_columns = st.columns(len(popular_ids))
    for column, formula_id in zip(popular_columns, popular_ids):
        definition = registry.get(formula_id)
        with column:
            st.markdown(f"**{definition.name_ja}**")
            st.caption(f"{definition.category} | {definition.summary}")
            if st.button("開く", key=f"popular_{formula_id}", use_container_width=True):
                st.session_state["calculator_formula_id"] = definition.formula_id
                st.session_state["page"] = "計算"

    render_section_header("最近使った計算", "直前に扱った式へすぐ戻れます。")
    recent_ids: list[str] = st.session_state.get("recent_formulas", [])[-5:][::-1]
    if recent_ids:
        for formula_id in recent_ids:
            definition = registry.get(formula_id)
            with st.container(border=True):
                col_text, col_action = st.columns([4, 1])
                with col_text:
                    st.markdown(f"**{definition.name_ja}**")
                    st.caption(definition.summary)
                with col_action:
                    if st.button("再度開く", key=f"recent_{formula_id}", use_container_width=True):
                        st.session_state["calculator_formula_id"] = definition.formula_id
                        st.session_state["page"] = "計算"
    else:
        render_empty_state("まだ計算履歴がありません。", "ホームから式を選ぶか、計算画面で式を選んで一度実行すると履歴がここに表示されます。")

    render_section_header("次に進む", "計算を始めるか、先に案件箱を作るかをここで選べます。")
    col_calc, col_project = st.columns(2)
    with col_calc:
        if st.button("計算画面へ進む", type="primary", use_container_width=True):
            st.session_state["page"] = "計算"
    with col_project:
        if st.button("案件管理を開く", use_container_width=True):
            st.session_state["page"] = "案件管理"

