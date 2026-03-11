# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Safe expression evaluation for user-defined formulas."""

from __future__ import annotations

import ast
import math
from functools import lru_cache


ALLOWED_FUNCTIONS = {
    "abs": abs,
    "acos": math.acos,
    "asin": math.asin,
    "atan": math.atan,
    "cos": math.cos,
    "cosh": math.cosh,
    "exp": math.exp,
    "log": math.log,
    "log10": math.log10,
    "max": max,
    "min": min,
    "sin": math.sin,
    "sinh": math.sinh,
    "sqrt": math.sqrt,
    "tan": math.tan,
    "tanh": math.tanh,
}
ALLOWED_CONSTANTS = {"e": math.e, "pi": math.pi}
ALLOWED_BINOPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod)
ALLOWED_UNARYOPS = (ast.UAdd, ast.USub)
ALLOWED_NODES = (
    ast.Expression,
    ast.BinOp,
    ast.Call,
    ast.Constant,
    ast.Load,
    ast.Name,
    ast.operator,
    ast.UnaryOp,
    ast.unaryop,
)


class ExpressionValidationError(ValueError):
    """Raised when a user expression is unsafe or malformed."""


class SafeExpression:
    """Compiled and validated expression."""

    def __init__(self, expression: str) -> None:
        self.expression = expression
        try:
            parsed = ast.parse(expression, mode="eval")
        except SyntaxError as exc:
            raise ExpressionValidationError("expression の構文が不正です。") from exc
        self._validate(parsed)
        self.variable_names = sorted(
            {
                child.id
                for child in ast.walk(parsed)
                if isinstance(child, ast.Name) and child.id not in ALLOWED_FUNCTIONS and child.id not in ALLOWED_CONSTANTS
            }
        )
        self._compiled = compile(parsed, "<custom_formula>", "eval")

    def evaluate(self, variables: dict[str, float]) -> float:
        """Evaluate the expression with a restricted environment."""

        names = {**ALLOWED_FUNCTIONS, **ALLOWED_CONSTANTS, **variables}
        try:
            value = eval(self._compiled, {"__builtins__": {}}, names)
        except ZeroDivisionError as exc:
            raise ValueError("式の評価中に 0 除算が発生しました。") from exc
        except NameError as exc:
            raise ValueError("式内に未定義の変数があります。") from exc
        except Exception as exc:
            raise ValueError("式の評価に失敗しました。") from exc
        if not isinstance(value, (int, float)):
            raise ValueError("式の評価結果が数値ではありません。")
        return float(value)

    def _validate(self, node: ast.AST) -> None:
        for child in ast.walk(node):
            if not isinstance(child, ALLOWED_NODES):
                raise ExpressionValidationError("expression に未対応の構文が含まれています。")
            if isinstance(child, ast.BinOp) and not isinstance(child.op, ALLOWED_BINOPS):
                raise ExpressionValidationError("expression に未対応の演算子が含まれています。")
            if isinstance(child, ast.UnaryOp) and not isinstance(child.op, ALLOWED_UNARYOPS):
                raise ExpressionValidationError("expression に未対応の単項演算子が含まれています。")
            if isinstance(child, ast.Call):
                if not isinstance(child.func, ast.Name) or child.func.id not in ALLOWED_FUNCTIONS:
                    raise ExpressionValidationError("expression で使える関数は math 系の限定セットのみです。")


@lru_cache(maxsize=512)
def get_safe_expression(expression: str) -> SafeExpression:
    """Return a cached validated expression."""

    return SafeExpression(expression)
