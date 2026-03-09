# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Repository for bundled and user-managed property data."""

from __future__ import annotations

import json
from pathlib import Path

from property_database.property_models import PropertyRecord


BASE_PROPERTY_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "properties" / "substances.json"
CUSTOM_PROPERTY_DATA_PATH = Path(__file__).resolve().parent.parent / "projects" / "custom_properties.json"


class PropertyRepository:
    """Load, merge, and persist property records."""

    def __init__(
        self,
        base_path: Path | None = None,
        custom_path: Path | None = None,
    ) -> None:
        self.base_path = base_path or BASE_PROPERTY_DATA_PATH
        self.custom_path = custom_path or CUSTOM_PROPERTY_DATA_PATH
        self.custom_path.parent.mkdir(parents=True, exist_ok=True)

    def load_base_records(self) -> list[PropertyRecord]:
        """Load bundled base records."""

        raw_items = json.loads(self.base_path.read_text(encoding="utf-8"))
        return [PropertyRecord.model_validate({**item, "data_origin": "base", "is_user_defined": False}) for item in raw_items]

    def load_custom_records(self) -> list[PropertyRecord]:
        """Load user-managed records."""

        if not self.custom_path.exists():
            return []
        raw_items = json.loads(self.custom_path.read_text(encoding="utf-8"))
        return [PropertyRecord.model_validate({**item, "data_origin": "custom", "is_user_defined": True}) for item in raw_items]

    def load_all_records(self) -> list[PropertyRecord]:
        """Merge base records with user overrides."""

        merged = {record.substance_id: record for record in self.load_base_records()}
        for record in self.load_custom_records():
            merged[record.substance_id] = record
        return sorted(merged.values(), key=lambda item: item.name_ja)

    def save_custom_record(self, record: PropertyRecord) -> PropertyRecord:
        """Insert or update a user-managed property record."""

        records = {item.substance_id: item for item in self.load_custom_records()}
        stored = PropertyRecord.model_validate({**record.model_dump(), "data_origin": "custom", "is_user_defined": True})
        records[stored.substance_id] = stored
        payload = [self._to_storage_dict(item) for item in sorted(records.values(), key=lambda value: value.name_ja)]
        self.custom_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return stored

    def delete_custom_record(self, substance_id: str) -> bool:
        """Delete a user-managed record or override."""

        records = {item.substance_id: item for item in self.load_custom_records()}
        removed = records.pop(substance_id, None)
        payload = [self._to_storage_dict(item) for item in sorted(records.values(), key=lambda value: value.name_ja)]
        self.custom_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return removed is not None

    def _to_storage_dict(self, record: PropertyRecord) -> dict[str, object]:
        data = record.model_dump()
        data.pop("data_origin", None)
        data.pop("is_user_defined", None)
        return data
