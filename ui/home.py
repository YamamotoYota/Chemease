"""Home page."""

from __future__ import annotations

import streamlit as st

from formula_registry.registry import FormulaRegistry


def render_home_page(registry: FormulaRegistry) -> None:
    """Render the home dashboard."""

    st.title("Chemease")
    st.subheader("化学工学エンジニア向け 化工計算アプリ")
    st.write(
        "化学工学便覧レベルの基礎式・経験式を日本語UIで扱える、"
        "ローカル実行前提の化工計算アプリです。式の意味、適用条件、物性候補、単位換算を見ながら使えます。"
    )

    categories = registry.list_categories()
    count_columns = st.columns(min(4, max(1, len(categories))))
    for index, category in enumerate(categories):
        with count_columns[index % len(count_columns)]:
            count = len(registry.search(category=category))
            st.metric(category, f"{count} 式")

    st.markdown("### 計算カテゴリ一覧")
    for category in categories:
        st.markdown(f"- {category}")

    search_keyword = st.text_input("式を検索", placeholder="例: Reynolds, 顕熱, 理想気体")
    if search_keyword:
        matches = registry.search(search_keyword)
        st.markdown("### 検索結果")
        for definition in matches[:10]:
            if st.button(f"{definition.name_ja} を開く", key=f"home_open_{definition.formula_id}"):
                st.session_state["calculator_formula_id"] = definition.formula_id
                st.session_state["page"] = "計算"
            st.caption(f"{definition.category} / {definition.summary}")

    st.markdown("### よく使う計算")
    popular_ids = [
        "fluid_reynolds_number",
        "fluid_darcy_weisbach_pressure_drop",
        "heat_sensible_heat",
        "heat_lmtd",
        "basic_ideal_gas_moles",
    ]
    for formula_id in popular_ids:
        definition = registry.get(formula_id)
        st.markdown(f"- {definition.name_ja}（{definition.category}）")

    st.markdown("### 最近使った計算")
    recent_ids: list[str] = st.session_state.get("recent_formulas", [])[-5:][::-1]
    if recent_ids:
        for formula_id in recent_ids:
            definition = registry.get(formula_id)
            st.markdown(f"- {definition.name_ja}")
    else:
        st.caption("まだ実行履歴がありません。")

    if st.button("案件管理へ移動"):
        st.session_state["page"] = "案件管理"

