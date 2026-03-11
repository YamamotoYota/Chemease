# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Formula registry tests."""

from __future__ import annotations

from formula_registry.registry import get_registry


def test_registry_loads_all_categories() -> None:
    registry = get_registry()
    categories = registry.list_categories()
    assert "流体" in categories
    assert "伝熱" in categories
    assert "反応工学" in categories
    assert len(registry.definitions) >= 210


def test_registry_has_20_plus_new_formulas_per_category() -> None:
    registry = get_registry()
    expected_minimums = {
        "流体": 32,
        "伝熱": 32,
        "物質移動": 29,
        "蒸留・分離": 28,
        "反応工学": 31,
        "粉体・機械操作": 27,
        "物性・基礎化工計算": 31,
    }
    for category, minimum in expected_minimums.items():
        assert len(registry.search(category=category)) >= minimum


def test_registry_search_finds_reynolds() -> None:
    registry = get_registry()
    matches = registry.search("Reynolds")
    assert any(item.formula_id == "fluid_reynolds_number" for item in matches)

