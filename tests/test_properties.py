# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Representative property database tests."""

from __future__ import annotations

from pathlib import Path

from property_database.property_loader import load_property_records
from property_database.property_models import PropertyRecord, PropertyValue
from property_database.property_repository import PropertyRepository
from property_database.property_service import PropertyService


def test_property_database_loads_water() -> None:
    records = load_property_records()
    service = PropertyService(records)
    water = service.get("water")
    assert water.name_ja == "水"
    assert water.density is not None
    assert water.density.value > 900.0


def test_custom_property_record_persistence(tmp_path: Path) -> None:
    base_path = Path("data/properties/substances.json")
    custom_path = tmp_path / "custom_properties.json"
    repository = PropertyRepository(base_path=base_path, custom_path=custom_path)
    service = PropertyService(repository)

    record = PropertyRecord(
        substance_id="custom_solvent",
        name_ja="カスタム溶媒",
        aliases=["Custom"],
        density=PropertyValue(value=950.0, unit="kg/m^3", note="GUI登録値"),
        phase_reference="液体, 25 degC",
        source="pytest",
        notes="test record",
        data_origin="custom",
        is_user_defined=True,
    )
    service.save_record(record)

    reloaded = PropertyService(repository)
    saved = reloaded.get("custom_solvent")
    assert saved.name_ja == "カスタム溶媒"
    assert saved.density is not None
    assert saved.density.value == 950.0

