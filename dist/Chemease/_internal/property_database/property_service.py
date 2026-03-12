# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Search, lookup, and editing service for representative properties."""

from __future__ import annotations

from property_database.property_repository import PropertyRepository
from property_database.property_models import PropertyRecord


class PropertyService:
    """Provide search and field lookup for property records."""

    def __init__(self, repository: PropertyRepository | list[PropertyRecord] | None = None) -> None:
        if isinstance(repository, list):
            self.repository = None
            self.records = repository
            self.by_id = {record.substance_id: record for record in repository}
            return

        self.repository = repository or PropertyRepository()
        self.records: list[PropertyRecord] = []
        self.by_id: dict[str, PropertyRecord] = {}
        self.reload()

    def reload(self) -> None:
        """Reload records from base and custom stores."""

        if self.repository is None:
            self.by_id = {record.substance_id: record for record in self.records}
            return
        self.records = self.repository.load_all_records()
        self.by_id = {record.substance_id: record for record in self.records}

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

    def save_record(self, record: PropertyRecord) -> PropertyRecord:
        """Persist a user-defined or overridden record."""

        if self.repository is None:
            raise RuntimeError("読み込み専用の PropertyService では保存できません。")
        saved = self.repository.save_custom_record(record)
        self.reload()
        return saved

    def delete_custom_record(self, substance_id: str) -> bool:
        """Delete a custom record or override entry."""

        if self.repository is None:
            raise RuntimeError("読み込み専用の PropertyService では削除できません。")
        removed = self.repository.delete_custom_record(substance_id)
        self.reload()
        return removed

    def list_records(self) -> list[PropertyRecord]:
        """Return all merged property records."""

        return list(self.records)


def get_property_service() -> PropertyService:
    """Return a property service instance."""

    return PropertyService()

