"""Representative property database tests."""

from __future__ import annotations

from property_database.property_loader import load_property_records
from property_database.property_service import PropertyService


def test_property_database_loads_water() -> None:
    records = load_property_records()
    service = PropertyService(records)
    water = service.get("water")
    assert water.name_ja == "水"
    assert water.density is not None
    assert water.density.value > 900.0

