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
    assert len(registry.definitions) >= 54


def test_registry_search_finds_reynolds() -> None:
    registry = get_registry()
    matches = registry.search("Reynolds")
    assert any(item.formula_id == "fluid_reynolds_number" for item in matches)

