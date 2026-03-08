"""Application information page."""

from __future__ import annotations

import streamlit as st


def render_info_page() -> None:
    """Render static application information."""

    st.title("アプリ情報")
    st.markdown(
        """
        - 日本語UIで化工計算を行うローカル向け Streamlit アプリです。
        - 初期版は便覧レベルの簡易式・代表物性値を採用しています。
        - 計算は標準単位へ正規化して実行し、結果には換算後の値も表示します。
        - 物性DBや式定義は JSON、案件保存は SQLite に分離しています。
        - 今後は熱力学モデル、VLE、相関式拡充へ拡張しやすい構造にしています。
        """
    )

