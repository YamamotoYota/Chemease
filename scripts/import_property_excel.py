# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Import and merge workbook-based property data into the bundled JSON DB."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

import pandas as pd


DEFAULT_OUTPUT_PATH = Path("data/properties/substances.json")
WORKBOOK_SOURCE = "改訂七版 化学工学便覧 付録 物性定数表 Property.xlsx"
ROOM_TEMPERATURE_K = 298.15

MANUAL_NAME_ID_MAP = {
    "水": "water",
    "窒素": "nitrogen",
    "酸素": "oxygen",
    "二酸化炭素": "co2",
    "メタノール": "methanol",
    "トルエン": "toluene",
    "ベンゼン": "benzene",
    "アルゴン": "argon",
    "アンモニア": "ammonia",
    "メタン": "methane",
    "プロパン": "propane",
    "アセトン": "acetone",
    "酢酸": "acetic_acid",
    "n-ヘキサン": "hexane",
    "n-ヘプタン": "heptane",
    "水素(正常）": "hydrogen",
    "ヘリウム－４": "helium",
}

MANUAL_FORMULA_ID_MAP = {
    "AR": "argon",
    "N2": "nitrogen",
    "O2": "oxygen",
    "CO2": "co2",
    "CH4O": "methanol",
    "C7H8": "toluene",
    "C6H6": "benzene",
    "H3N": "ammonia",
    "CH4": "methane",
    "C3H8": "propane",
    "C3H6O": "acetone",
    "C2H4O2": "acetic_acid",
    "C6H14": "hexane",
    "C7H16": "heptane",
    "H2": "hydrogen",
    "HE(4)": "helium",
    "H2O": "water",
}


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--excel", required=True, type=Path, help="入力する Excel ファイル")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_PATH, type=Path, help="更新対象の JSON ファイル")
    return parser.parse_args()


def is_number(value: Any) -> bool:
    """Return whether the incoming value is a usable number."""

    if value is None:
        return False
    if isinstance(value, (int, float)):
        return not (isinstance(value, float) and math.isnan(value))
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return False
        try:
            float(text)
        except ValueError:
            return False
        return True
    return False


def normalize_text(value: Any) -> str:
    """Normalize workbook cell values into trimmed strings."""

    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return str(value).strip()


def to_property_value(value: float, unit: str, note: str) -> dict[str, Any]:
    """Create the app's property-value JSON shape."""

    return {"value": float(value), "unit": unit, "note": note}


def slugify_formula(formula: str) -> str:
    """Create a conservative ASCII slug from a chemical formula."""

    slug = re.sub(r"[^0-9A-Za-z]+", "_", formula).strip("_").lower()
    return slug or "item"


def is_liquid_at_room_temperature(melting_point: float | None, boiling_point: float | None) -> bool:
    """Return whether the material is likely liquid at 25 degC."""

    if melting_point is None or boiling_point is None:
        return False
    return melting_point < ROOM_TEMPERATURE_K < boiling_point


def build_phase_reference(existing_phase: str, melting_point: float | None, boiling_point: float | None) -> str:
    """Select a simple representative phase description."""

    if existing_phase:
        return existing_phase
    if melting_point is None or boiling_point is None:
        return "便覧表の代表値"
    if melting_point < ROOM_TEMPERATURE_K < boiling_point:
        return "液体, 25 degC 付近"
    if boiling_point <= ROOM_TEMPERATURE_K:
        return "気体, 25 degC 付近"
    if melting_point >= ROOM_TEMPERATURE_K:
        return "常温で固体"
    return "便覧表の代表値"


def merge_source(existing_source: str) -> str:
    """Merge workbook source text with an existing source string."""

    if not existing_source:
        return WORKBOOK_SOURCE
    if WORKBOOK_SOURCE in existing_source:
        return existing_source
    return f"{WORKBOOK_SOURCE} / {existing_source}"


def merge_notes(existing_notes: str, density_temperature: str, applied_density: bool) -> str:
    """Compose a compact notes field describing imported workbook data."""

    notes = ["便覧付録の参考値を取り込みました。"]
    if applied_density and density_temperature:
        notes.append(f"密度は液密度欄の {density_temperature} K 基準値です。")
    if existing_notes:
        notes.append(existing_notes)
    return " ".join(notes)


def normalize_temperature_range(value: str) -> str:
    """Normalize the workbook temperature range column."""

    if not value:
        return ""
    return f"便覧の相関適用温度範囲: {value} K"


def load_existing_records(path: Path) -> list[dict[str, Any]]:
    """Load the current JSON records."""

    return json.loads(path.read_text(encoding="utf-8"))


def build_existing_indexes(records: list[dict[str, Any]]) -> tuple[dict[str, str], dict[str, str]]:
    """Build name and formula indexes for current records."""

    by_name = {normalize_text(record.get("name_ja")): str(record["substance_id"]) for record in records}
    by_formula: dict[str, str] = {}
    for record in records:
        substance_id = str(record["substance_id"])
        for alias in record.get("aliases", []):
            alias_text = normalize_text(alias).upper()
            if re.fullmatch(r"[0-9A-Z()\-+]+", alias_text):
                by_formula[alias_text] = substance_id
    return by_name, by_formula


def choose_substance_id(
    row_no: int,
    name_ja: str,
    formula: str,
    existing_by_name: dict[str, str],
    existing_by_formula: dict[str, str],
    formula_counts: dict[str, int],
    used_ids: set[str],
) -> str:
    """Choose a stable substance identifier for a workbook row."""

    for candidate in (MANUAL_NAME_ID_MAP.get(name_ja), existing_by_name.get(name_ja)):
        if candidate:
            used_ids.add(candidate)
            return candidate

    if formula and formula_counts.get(formula, 0) == 1:
        for candidate in (MANUAL_FORMULA_ID_MAP.get(formula), existing_by_formula.get(formula)):
            if candidate:
                used_ids.add(candidate)
                return candidate

    base = f"book_{int(row_no):03d}_{slugify_formula(formula)}"
    candidate = base
    counter = 2
    while candidate in used_ids:
        candidate = f"{base}_{counter}"
        counter += 1
    used_ids.add(candidate)
    return candidate


def build_record_from_row(
    row: pd.Series,
    existing_record: dict[str, Any] | None,
    substance_id: str,
) -> dict[str, Any]:
    """Convert one workbook row into the JSON record shape."""

    name_ja = normalize_text(row["名称"])
    formula = normalize_text(row["化学式"])
    molecular_weight = float(row["分子量"]) if is_number(row["分子量"]) else None
    melting_point = float(row["融点"]) if is_number(row["融点"]) else None
    boiling_point = float(row["Tb"]) if is_number(row["Tb"]) else None
    critical_temperature = float(row["Tc"]) if is_number(row["Tc"]) else None
    critical_pressure = float(row["ｐｃ"]) if is_number(row["ｐｃ"]) and float(row["ｐｃ"]) > 0 else None
    liquid_density = float(row["液密度"]) if is_number(row["液密度"]) and float(row["液密度"]) > 0 else None
    density_temperature = normalize_text(row["at T"])
    viscosity_25c = float(row["粘度(25℃)"]) if is_number(row["粘度(25℃)"]) and float(row["粘度(25℃)"]) > 0 else None
    latent_heat_kj_per_mol = float(row["蒸発潜熱"]) if is_number(row["蒸発潜熱"]) and float(row["蒸発潜熱"]) > 0 else None
    temperature_range = normalize_text(row["温度範囲"])

    record: dict[str, Any] = dict(existing_record or {})
    record["substance_id"] = substance_id
    record["name_ja"] = normalize_text(record.get("name_ja")) or name_ja

    alias_candidates = [*record.get("aliases", []), name_ja]
    if formula:
        alias_candidates.append(formula)
    aliases = list(dict.fromkeys([alias for alias in alias_candidates if normalize_text(alias)]))
    record["aliases"] = aliases

    if molecular_weight is not None:
        record["molecular_weight"] = to_property_value(molecular_weight / 1000.0, "kg/mol", "Property.xlsx")
    if melting_point is not None:
        record["melting_point"] = to_property_value(melting_point, "K", "Property.xlsx")
    if boiling_point is not None:
        record["boiling_point"] = to_property_value(boiling_point, "K", "Property.xlsx")
    if critical_temperature is not None:
        record["critical_temperature"] = to_property_value(critical_temperature, "K", "Property.xlsx")
    if critical_pressure is not None:
        record["critical_pressure"] = to_property_value(critical_pressure * 1_000_000.0, "Pa", "Property.xlsx")
    if viscosity_25c is not None:
        record["viscosity"] = to_property_value(viscosity_25c * 1.0e-3, "Pas", "Property.xlsx, 25 degC")

    applied_density = False
    if liquid_density is not None and is_liquid_at_room_temperature(melting_point, boiling_point):
        density_note = "Property.xlsx"
        if density_temperature:
            density_note = f"Property.xlsx, {density_temperature} K"
        record["density"] = to_property_value(liquid_density * 1000.0, "kg/m^3", density_note)
        applied_density = True

    if latent_heat_kj_per_mol is not None and molecular_weight is not None and molecular_weight > 0:
        latent_heat_j_per_kg = latent_heat_kj_per_mol * 1_000_000.0 / molecular_weight
        record["latent_heat"] = to_property_value(latent_heat_j_per_kg, "J/kg", "Property.xlsx")

    record["phase_reference"] = build_phase_reference(
        normalize_text(record.get("phase_reference")),
        melting_point,
        boiling_point,
    )

    workbook_temperature_range = normalize_temperature_range(temperature_range)
    if workbook_temperature_range:
        record["temperature_range"] = workbook_temperature_range
    else:
        record["temperature_range"] = normalize_text(record.get("temperature_range"))

    record["source"] = merge_source(normalize_text(record.get("source")))
    record["notes"] = merge_notes(normalize_text(record.get("notes")), density_temperature, applied_density)
    return record


def import_workbook(excel_path: Path, output_path: Path) -> list[dict[str, Any]]:
    """Merge workbook rows into the bundled property JSON DB."""

    existing_records = load_existing_records(output_path)
    by_id = {str(record["substance_id"]): record for record in existing_records}
    existing_by_name, existing_by_formula = build_existing_indexes(existing_records)
    used_ids = set(by_id)

    df = pd.read_excel(excel_path)
    df = df[df["No."].apply(is_number) & df["名称"].notna()].copy()
    formula_counts = df["化学式"].map(normalize_text).str.upper().value_counts().to_dict()

    for _, row in df.iterrows():
        row_no = int(float(row["No."]))
        name_ja = normalize_text(row["名称"])
        formula = normalize_text(row["化学式"]).upper()
        substance_id = choose_substance_id(row_no, name_ja, formula, existing_by_name, existing_by_formula, formula_counts, used_ids)
        existing_record = by_id.get(substance_id)
        by_id[substance_id] = build_record_from_row(row, existing_record, substance_id)

    merged_records = sorted(by_id.values(), key=lambda item: normalize_text(item.get("name_ja")))
    output_path.write_text(json.dumps(merged_records, ensure_ascii=False, indent=2), encoding="utf-8")
    return merged_records


def main() -> int:
    """CLI entry point."""

    args = parse_args()
    import_workbook(args.excel, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
