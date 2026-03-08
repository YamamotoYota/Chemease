# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Search and lookup service for representative properties."""

from __future__ import annotations

from functools import lru_cache

from property_database.property_loader import load_property_records
from property_database.property_models import PropertyRecord


class PropertyService:
    """Provide search and field lookup for property records."""

    def __init__(self, records: list[PropertyRecord]) -> None:
        self.records = records
        self.by_id = {record.substance_id: record for record in records}

    def search(self, keyword: str = "") -> list[PropertyRecord]:
        """Search substances by name or alias."""

        keyword_text = keyword.strip().lower()
        if not keyword_text:
            return sorted(self.records, key=lambda item: item.name_ja)

        matched: list[PropertyRecord] = []
        for record in self.records:
            haystacks = [record.substance_id, record.name_ja, *record.aliases]
            if any(keyword_text in text.lower() for text in haystacks):
                matched.append(record)
        return sorted(matched, key=lambda item: item.name_ja)

    def get(self, substance_id: str) -> PropertyRecord:
        """Return a property record by identifier."""

        return self.by_id[substance_id]

    def get_property_value(self, substance_id: str, property_key: str) -> tuple[float, str] | None:
        """Return a property value and its unit when available."""

        record = self.get(substance_id)
        item = getattr(record, property_key, None)
        if item is None:
            return None
        return item.value, item.unit


@lru_cache(maxsize=1)
def get_property_service() -> PropertyService:
    """Return a cached property service."""

    return PropertyService(load_property_records())

