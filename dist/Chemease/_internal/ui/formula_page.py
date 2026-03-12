# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Formula management page for user-defined formulas."""

from __future__ import annotations

import streamlit as st

from formula_registry.custom_formula_service import CustomFormulaService
from formula_registry.models import FormulaDefinition, FormulaVariable
from formula_registry.registry import FormulaRegistry


def _split_lines(raw_text: str) -> list[str]:
    return [item.strip() for item in raw_text.replace(",", "\n").splitlines() if item.strip()]


def _variable_from_form(prefix: str, index: int, current: FormulaVariable | None = None, *, is_output: bool = False) -> FormulaVariable:
    label_prefix = "出力変数" if is_output else f"入力変数{index + 1}"
    col1, col2 = st.columns(2)
    with col1:
        key = st.text_input(f"{label_prefix} キー", value=current.key if current else "", key=f"{prefix}_key_{index}")
        label = st.text_input(f"{label_prefix} 表示名", value=current.label_ja if current else "", key=f"{prefix}_label_{index}")
        description = st.text_input(f"{label_prefix} 説明", value=current.description if current else "", key=f"{prefix}_description_{index}")
    with col2:
        standard_unit = st.text_input(f"{label_prefix} 標準単位", value=current.standard_unit if current else "", key=f"{prefix}_unit_{index}")
        allowed_units_text = st.text_input(
            f"{label_prefix} 許容単位（カンマ区切り）",
            value=", ".join(current.allowed_units) if current else "",
            key=f"{prefix}_allowed_{index}",
        )
        default_value = st.text_input(
            f"{label_prefix} 初期値",
            value="" if current is None or current.default_value is None else str(current.default_value),
            key=f"{prefix}_default_{index}",
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
    st.markdown("### ユーザー定義式の登録・編集")
    formula_id = st.text_input("formula_id", value=current.formula_id if current else "")
    name_ja = st.text_input("式名", value=current.name_ja if current else "")
    distinct_categories = list(dict.fromkeys(category_options + ["ユーザー定義", "その他"]))
    category = st.selectbox(
        "カテゴリ",
        options=distinct_categories,
        index=distinct_categories.index(current.category) if current and current.category in distinct_categories else 0,
        key=f"formula_category_{mode_token}",
    )
    summary = st.text_input("概要", value=current.summary if current else "")
    description = st.text_area("詳細説明", value=current.description if current else "")
    equation_latex = st.text_input("LaTeX式", value=current.equation_latex if current else "", help="例: Re = rho v D / mu")
    expression = st.text_input(
        "計算式 expression",
        value=current.expression or "" if current else "",
        help="Python風の数式で出力変数を計算します。例: density * velocity * diameter / viscosity",
    )
    output_variable = _variable_from_form("formula_output", 0, current.outputs[0] if current else None, is_output=True)

    inputs: list[FormulaVariable] = []
    for index in range(variable_count):
        existing = current.inputs[index] if current and index < len(current.inputs) else None
        with st.expander(f"入力変数 {index + 1}", expanded=True):
            inputs.append(_variable_from_form("formula_input", index, existing))

    applicability = st.text_area("適用条件（改行またはカンマ区切り）", value="\n".join(current.applicability) if current else "")
    assumptions = st.text_area("前提（改行またはカンマ区切り）", value="\n".join(current.assumptions) if current else "")
    cautions = st.text_area("注意事項（改行またはカンマ区切り）", value="\n".join(current.cautions) if current else "")
    references = st.text_area("参考情報（改行またはカンマ区切り）", value="\n".join(current.references) if current else "")
    keywords = st.text_input("検索キーワード（カンマ区切り）", value=", ".join(current.keywords) if current else "")
    interpretation = st.text_area("結果解釈ヒント", value=current.interpretation_hint if current else "")

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

    st.title("式管理")
    custom_formulas = custom_formula_service.list_custom_formulas()
    tab_manage, tab_list = st.tabs(["登録・編集", "登録済みユーザー式"])

    with tab_manage:
        mode = st.radio("編集モード", ["新規登録", "既存編集"], horizontal=True)
        current: FormulaDefinition | None = None
        if mode == "既存編集" and custom_formulas:
            current_id = st.selectbox(
                "編集対象",
                options=[item.formula_id for item in custom_formulas],
                format_func=lambda value: next(item.name_ja for item in custom_formulas if item.formula_id == value),
            )
            current = next(item for item in custom_formulas if item.formula_id == current_id)
        elif mode == "既存編集":
            st.info("まだユーザー登録式がありません。")

        variable_count = st.number_input(
            "入力変数数",
            min_value=1,
            max_value=10,
            value=len(current.inputs) if current else 2,
            step=1,
            key=f"formula_var_count_{current.formula_id if current else 'new'}",
        )

        with st.form("custom_formula_editor"):
            definition = _build_definition_from_form(current, registry.list_categories(), int(variable_count))
            submitted = st.form_submit_button("式を保存")

        if submitted:
            if not definition.formula_id or not definition.name_ja:
                st.error("formula_id と式名は必須です。")
            else:
                try:
                    custom_formula_service.save_formula(definition)
                except Exception as exc:
                    st.error(str(exc))
                else:
                    st.success("ユーザー定義式を保存しました。計算画面ですぐ利用できます。")
                    st.rerun()

        if current is not None and st.button("選択中のユーザー式を削除", type="secondary"):
            custom_formula_service.delete_formula(current.formula_id)
            st.success("ユーザー定義式を削除しました。")
            st.rerun()

    with tab_list:
        if not custom_formulas:
            st.caption("ユーザー定義式はまだありません。")
            return

        for item in custom_formulas:
            with st.expander(f"{item.name_ja} / {item.formula_id}"):
                st.caption(f"カテゴリ: {item.category}")
                st.write(item.summary)
                st.latex(item.equation_latex)
                if item.expression:
                    st.code(item.expression, language="python")
                st.write("入力変数:", ", ".join(f"{variable.label_ja}({variable.key})" for variable in item.inputs))
                st.write("出力変数:", ", ".join(f"{variable.label_ja}({variable.key})" for variable in item.outputs))
