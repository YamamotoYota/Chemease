# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Load representative physical-property records from JSON."""

from __future__ import annotations

import json
from pathlib import Path

from property_database.property_models import PropertyRecord


PROPERTY_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "properties" / "substances.json"


def load_property_records(path: Path | None = None) -> list[PropertyRecord]:
    """Load all property records from the JSON data file."""

    target_path = path or PROPERTY_DATA_PATH
    raw_items = json.loads(target_path.read_text(encoding="utf-8"))
    return [PropertyRecord.model_validate(item) for item in raw_items]

