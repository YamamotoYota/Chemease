# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Application information page."""

from __future__ import annotations

import streamlit as st

from runtime_paths import describe_user_data_root
from ui.layout import render_note, render_page_header, render_section_header


def render_info_page() -> None:
    """Render static application information."""

    render_page_header(
        "アプリ情報",
        "Chemease の考え方、できること、使うときの前提をまとめたページです。初めて使う方への案内としても、運用ルールの確認用としても使えるよう整理しています。",
        eyebrow="About",
        steps=[
            ("何ができるかを見る", "搭載機能と対象範囲を把握します。"),
            ("おすすめの使い方を知る", "迷いにくい基本フローを確認します。"),
            ("注意点を確認する", "便覧式を使う前提と限界を把握します。"),
        ],
    )

    render_section_header("Chemease でできること", "化学工学の基礎計算を、式の説明付きで扱えるようにしています。")
    st.markdown(
        """
        - 日本語 UI で化工計算を行うローカル向け Streamlit アプリです。
        - 便覧レベルの簡易式と代表物性値を採用し、標準単位へ正規化して計算します。
        - ユーザー定義式を GUI から追加・編集・削除でき、保存後すぐ計算に使えます。
        - 単一出力の式では、出力指定から入力変数を逆算する使い方にも対応します。
        - 物性 DB や式定義は JSON、案件保存は SQLite に分離し、段階的に拡張しやすい構造にしています。
        """
    )

    render_section_header("おすすめの使い方", "慣れるまでは、次の順序で使うと操作意図が分かりやすくなります。")
    render_note(
        "基本フロー",
        "ホームで式を探し、計算画面で条件と単位を整え、納得した結果だけ案件へ保存する流れが基本です。物性値が必要な場合は、計算画面の物性候補か、物性参照画面で出典を確認してから採用してください。",
        bullets=[
            "式の説明と前提条件を先に読むと、入力ミスや誤用を減らせます。",
            "案件へ保存しておくと、計算条件をあとで再読込して再検討できます。",
            "汎用式が足りない場合は、式管理で独自の簡易式を追加できます。",
        ],
    )

    render_section_header("使うときの前提と注意点", "設計判断の最終値というより、検討のたたき台を素早く作るためのアプリとして位置付けています。")
    st.markdown(
        """
        - 結果は便覧レベルの簡易式に基づく参考値です。厳密設計や保証値の代替にはなりません。
        - 適用範囲外の条件では妥当な値にならない場合があります。温度範囲、圧力基準、物性値の出典を必ず確認してください。
        - 逆算は初期推定値に影響を受けるため、現実的な目安値を入れると安定しやすくなります。
        - カスタム式やカスタム物性は利便性が高い反面、レビューなしで使い回すと誤用の原因になります。説明文と出典を残す運用を推奨します。
        """
    )
    st.caption(f"ユーザー定義式、カスタム物性、案件DB は次の書き込み可能フォルダへ保存されます: {describe_user_data_root()}")
