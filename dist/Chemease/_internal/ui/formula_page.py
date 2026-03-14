# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Formula management page for user-defined formulas."""

from __future__ import annotations

import streamlit as st

from formula_registry.custom_formula_service import CustomFormulaService
from formula_registry.models import FormulaDefinition, FormulaVariable
from formula_registry.registry import FormulaRegistry
from ui.layout import render_empty_state, render_note, render_page_header, render_section_header


def _split_lines(raw_text: str) -> list[str]:
    return [item.strip() for item in raw_text.replace(",", "\n").splitlines() if item.strip()]


def _variable_from_form(prefix: str, index: int, current: FormulaVariable | None = None, *, is_output: bool = False) -> FormulaVariable:
    label_prefix = "出力変数" if is_output else f"入力変数{index + 1}"
    col1, col2 = st.columns(2)
    with col1:
        key = st.text_input(
            f"{label_prefix} キー",
            value=current.key if current else "",
            key=f"{prefix}_key_{index}",
            help="式の中で使う英数字キーです。半角英数字とアンダースコアで統一すると管理しやすくなります。",
        )
        label = st.text_input(
            f"{label_prefix} 表示名",
            value=current.label_ja if current else "",
            key=f"{prefix}_label_{index}",
            help="計算画面に表示される名称です。現場で通じる日本語にしてください。",
        )
        description = st.text_input(
            f"{label_prefix} 説明",
            value=current.description if current else "",
            key=f"{prefix}_description_{index}",
            help="何を表す変数か、判断に迷わない説明を短く書いてください。",
        )
    with col2:
        standard_unit = st.text_input(
            f"{label_prefix} 標準単位",
            value=current.standard_unit if current else "",
            key=f"{prefix}_unit_{index}",
            help="内部計算の基準単位です。式の整合性確認に使います。",
        )
        allowed_units_text = st.text_input(
            f"{label_prefix} 許容単位（カンマ区切り）",
            value=", ".join(current.allowed_units) if current else "",
            key=f"{prefix}_allowed_{index}",
            help="画面で選択可能にする単位一覧です。標準単位も必ず含めてください。",
        )
        default_value = st.text_input(
            f"{label_prefix} 初期値",
            value="" if current is None or current.default_value is None else str(current.default_value),
            key=f"{prefix}_default_{index}",
            help="よく使う目安値があれば設定します。空欄でも構いません。",
        )
    col3, col4, col5 = st.columns(3)
    with col3:
        positive_only = st.checkbox(f"{label_prefix} は正値中心", value=current.positive_only if current else False, key=f"{prefix}_positive_{index}")
    with col4:
        nonzero = st.checkbox(f"{label_prefix} は0不可", value=current.nonzero if current else False, key=f"{prefix}_nonzero_{index}")
    with col5:
        pressure_basis_supported = st.checkbox(
            f"{label_prefix} は圧力基準対応",
            value=current.pressure_basis_supported if current else False,
            key=f"{prefix}_pressure_{index}",
        )
    is_temperature_difference = st.checkbox(
        f"{label_prefix} は温度差として扱う",
        value=current.is_temperature_difference if current else False,
        key=f"{prefix}_tempdiff_{index}",
        help="温度差は絶対温度とは換算ルールが異なるため、必要な場合にチェックします。",
    )

    payload = {
        "key": key.strip(),
        "label_ja": label.strip() or key.strip(),
        "description": description.strip() or label.strip() or key.strip(),
        "standard_unit": standard_unit.strip(),
        "allowed_units": _split_lines(allowed_units_text),
        "default_value": float(default_value) if default_value.strip() else None,
        "positive_only": positive_only,
        "nonzero": nonzero,
        "pressure_basis_supported": pressure_basis_supported,
        "is_temperature_difference": is_temperature_difference,
        "required": not is_output,
    }
    return FormulaVariable.model_validate(payload)


def _build_definition_from_form(current: FormulaDefinition | None, category_options: list[str], variable_count: int) -> FormulaDefinition:
    mode_token = current.formula_id if current else "new"
    render_section_header("式の基本情報", "まずは式名、カテゴリ、概要を整理し、次に入出力と計算 expression を設定します。")
    formula_id = st.text_input(
        "formula_id",
        value=current.formula_id if current else "",
        help="一意な管理IDです。保存後も識別子として使われます。例: custom_heat_duty_balance",
    )
    name_ja = st.text_input(
        "式名",
        value=current.name_ja if current else "",
        help="利用者が計算画面で探しやすい日本語名にしてください。",
    )
    distinct_categories = list(dict.fromkeys(category_options + ["ユーザー定義", "その他"]))
    category = st.selectbox(
        "カテゴリ",
        options=distinct_categories,
        index=distinct_categories.index(current.category) if current and current.category in distinct_categories else 0,
        key=f"formula_category_{mode_token}",
        help="近い既存カテゴリへ入れると、計算画面から探しやすくなります。",
    )
    summary = st.text_input(
        "概要",
        value=current.summary if current else "",
        help="一覧画面で見える短い説明です。用途が一目で伝わる表現にしてください。",
    )
    description = st.text_area(
        "詳細説明",
        value=current.description if current else "",
        help="どんな状況で使う式か、結果をどう読むべきかを丁寧に書いておくと計算画面で迷いにくくなります。",
    )
    equation_latex = st.text_input(
        "LaTeX 式",
        value=current.equation_latex if current else "",
        help="例: Re = rho v D / mu",
    )
    expression = st.text_input(
        "計算式 expression",
        value=current.expression or "" if current else "",
        help="Python風の数式で出力変数を計算します。例: density * velocity * diameter / viscosity",
    )

    render_section_header("出力変数", "出力は 1 変数として登録します。表示名と説明は、結果画面でそのまま使われます。")
    output_variable = _variable_from_form("formula_output", 0, current.outputs[0] if current else None, is_output=True)

    render_section_header("入力変数", "必要な入力数だけ定義し、単位と制約を合わせて設定してください。")
    inputs: list[FormulaVariable] = []
    for index in range(variable_count):
        existing = current.inputs[index] if current and index < len(current.inputs) else None
        with st.expander(f"入力変数 {index + 1}", expanded=True):
            inputs.append(_variable_from_form("formula_input", index, existing))

    render_section_header("利用時の説明", "ここで書いた内容は計算画面の補足説明になります。入力時の迷いを減らすため、できるだけ丁寧に書くことをおすすめします。")
    applicability = st.text_area("適用条件（改行またはカンマ区切り）", value="\n".join(current.applicability) if current else "")
    assumptions = st.text_area("前提（改行またはカンマ区切り）", value="\n".join(current.assumptions) if current else "")
    cautions = st.text_area("注意事項（改行またはカンマ区切り）", value="\n".join(current.cautions) if current else "")
    references = st.text_area("参考情報（改行またはカンマ区切り）", value="\n".join(current.references) if current else "")
    keywords = st.text_input(
        "検索キーワード（カンマ区切り）",
        value=", ".join(current.keywords) if current else "",
        help="計算画面の検索ヒットを増やしたい語を入れてください。",
    )
    interpretation = st.text_area(
        "結果解釈ヒント",
        value=current.interpretation_hint if current else "",
        help="結果欄に表示する補足です。参考値としてどう読むかを書いておくと親切です。",
    )

    variable_definitions = {item.key: item.label_ja for item in [*inputs, output_variable]}
    return FormulaDefinition.model_validate(
        {
            "formula_id": formula_id.strip(),
            "name_ja": name_ja.strip(),
            "category": category,
            "summary": summary.strip(),
            "description": description.strip() or summary.strip(),
            "equation_latex": equation_latex.strip(),
            "inputs": [item.model_dump() for item in inputs],
            "outputs": [output_variable.model_dump()],
            "variable_definitions": variable_definitions,
            "applicability": _split_lines(applicability),
            "assumptions": _split_lines(assumptions),
            "cautions": _split_lines(cautions),
            "references": _split_lines(references),
            "function_name": f"custom:{formula_id.strip()}",
            "expression": expression.strip(),
            "keywords": _split_lines(keywords),
            "interpretation_hint": interpretation.strip(),
            "is_user_defined": True,
        }
    )


def render_formula_page(custom_formula_service: CustomFormulaService, registry: FormulaRegistry) -> None:
    """Render the user-defined formula management page."""

    render_page_header(
        "式管理",
        "Chemease にない式を追加したい場合は、この画面でユーザー定義式を登録します。登録時に説明文や注意事項を丁寧に書いておくと、あとから使う人が計算意図を理解しやすくなります。",
        eyebrow="Formula Library",
        steps=[
            ("基本情報を決める", "式名、概要、カテゴリを整えて検索しやすくします。"),
            ("入出力を定義する", "変数名、単位、制約を明確にします。"),
            ("説明を残す", "適用条件や注意事項を残して使い回しやすくします。"),
        ],
    )
    custom_formulas = custom_formula_service.list_custom_formulas()
    tab_manage, tab_list = st.tabs(["登録・編集", "登録済みユーザー式"])

    with tab_manage:
        render_note(
            "登録前の確認ポイント",
            "expression 登録は単一出力の簡易式向けです。多変量の分岐ロジックや複雑な相関式は、コード側へ追加したほうが保守しやすい場合があります。",
            bullets=[
                "formula_id は後から参照しやすい短い英数字IDにします。",
                "概要、適用条件、注意事項は利用者向け文章として書くと実務で役立ちます。",
            ],
        )
        mode = st.radio("編集モード", ["新規登録", "既存編集"], horizontal=True)
        current: FormulaDefinition | None = None
        if mode == "既存編集" and custom_formulas:
            current_id = st.selectbox(
                "編集対象",
                options=[item.formula_id for item in custom_formulas],
                format_func=lambda value: next(item.name_ja for item in custom_formulas if item.formula_id == value),
                help="既存のユーザー式を選ぶと、内容を読み込んで編集できます。",
            )
            current = next(item for item in custom_formulas if item.formula_id == current_id)
        elif mode == "既存編集":
            render_empty_state("まだユーザー登録式がありません。", "まずは新規登録モードで式を追加してください。")

        variable_count = st.number_input(
            "入力変数数",
            min_value=1,
            max_value=10,
            value=len(current.inputs) if current else 2,
            step=1,
            key=f"formula_var_count_{current.formula_id if current else 'new'}",
            help="必要な入力数に合わせて調整します。",
        )

        with st.form("custom_formula_editor"):
            definition = _build_definition_from_form(current, registry.list_categories(), int(variable_count))
            submitted = st.form_submit_button("式を保存する", use_container_width=True)

        if submitted:
            if not definition.formula_id or not definition.name_ja:
                st.error("formula_id と式名は必須です。")
            else:
                try:
                    custom_formula_service.save_formula(definition)
                except Exception as exc:
                    st.error(str(exc))
                else:
                    st.success("ユーザー定義式を保存しました。計算画面にすぐ反映されます。")
                    st.rerun()

        if current is not None and st.button("選択中のユーザー式を削除する", type="secondary", use_container_width=True):
            custom_formula_service.delete_formula(current.formula_id)
            st.success("ユーザー定義式を削除しました。")
            st.rerun()

    with tab_list:
        render_section_header("登録済みの式", "一覧から内容を確認し、必要なら計算画面でそのまま使えます。")
        if not custom_formulas:
            render_empty_state("ユーザー定義式はまだありません。", "上の登録・編集タブから最初の式を追加してください。")
            return

        for item in custom_formulas:
            with st.expander(f"{item.name_ja} / {item.formula_id}"):
                st.caption(f"カテゴリ: {item.category}")
                st.write(item.summary)
                st.latex(item.equation_latex)
                if item.expression:
                    st.code(item.expression, language="python")
                st.write("入力変数:", ", ".join(f"{variable.label_ja} ({variable.key})" for variable in item.inputs))
                st.write("出力変数:", ", ".join(f"{variable.label_ja} ({variable.key})" for variable in item.outputs))
                col_edit, col_calc = st.columns(2)
                with col_edit:
                    st.caption("編集したい場合は、上の登録・編集タブでこの式を選択してください。")
                with col_calc:
                    if st.button("計算画面で使う", key=f"open_custom_formula_{item.formula_id}", use_container_width=True):
                        st.session_state["calculator_formula_id"] = item.formula_id
                        st.session_state["page"] = "計算"
