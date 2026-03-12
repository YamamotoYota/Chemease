# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""In-memory registry of formula definitions."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from formula_registry.loader import load_formula_definitions
from formula_registry.models import FormulaDefinition


@dataclass(slots=True)
class FormulaRegistry:
    """Searchable registry for formula definitions."""

    definitions: dict[str, FormulaDefinition]

    def get(self, formula_id: str) -> FormulaDefinition:
        """Return a formula definition by identifier."""

        return self.definitions[formula_id]

    def list_categories(self) -> list[str]:
        """Return unique categories sorted in Japanese order by text."""

        return sorted({definition.category for definition in self.definitions.values()})

    def search(self, keyword: str = "", category: str | None = None) -> list[FormulaDefinition]:
        """Search formulas by free-text keyword and category."""

        keyword_text = keyword.strip().lower()
        matched: list[FormulaDefinition] = []

        for definition in self.definitions.values():
            if category and definition.category != category:
                continue

            if not keyword_text:
                matched.append(definition)
                continue

            haystacks = [
                definition.formula_id,
                definition.name_ja,
                definition.summary,
                definition.description,
                *definition.keywords,
            ]
            if any(keyword_text in text.lower() for text in haystacks):
                matched.append(definition)

        return sorted(matched, key=lambda item: (item.category, item.name_ja))


@lru_cache(maxsize=1)
def get_registry() -> FormulaRegistry:
    """Return a cached registry instance."""

    definitions = {definition.formula_id: definition for definition in load_formula_definitions()}
    return FormulaRegistry(definitions=definitions)

