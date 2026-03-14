# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Runtime path tests."""

from __future__ import annotations

from pathlib import Path

import runtime_paths


def test_user_data_dir_can_be_overridden(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv(runtime_paths.ENV_USER_DATA_DIR, str(tmp_path / "portable-data"))
    runtime_paths.get_user_data_root.cache_clear()

    try:
        root = runtime_paths.get_user_data_root()

        assert root == (tmp_path / "portable-data")
        assert runtime_paths.get_project_db_path() == root / "chemease.db"
        assert runtime_paths.get_custom_formula_data_path() == root / "custom_formulas.json"
        assert runtime_paths.get_custom_property_data_path() == root / "custom_properties.json"
    finally:
        runtime_paths.get_user_data_root.cache_clear()


def test_legacy_user_data_is_migrated(monkeypatch, tmp_path: Path) -> None:
    legacy_root = tmp_path / "legacy-bundle"
    (legacy_root / "projects").mkdir(parents=True, exist_ok=True)
    (legacy_root / "projects" / "custom_formulas.json").write_text("[]", encoding="utf-8")
    (legacy_root / "projects" / "custom_properties.json").write_text("[]", encoding="utf-8")
    (legacy_root / "projects" / "chemease.db").write_text("sqlite", encoding="utf-8")

    target_root = tmp_path / "portable-data"
    monkeypatch.setenv(runtime_paths.ENV_USER_DATA_DIR, str(target_root))
    monkeypatch.setattr(runtime_paths, "get_bundle_root", lambda: legacy_root)
    runtime_paths.get_user_data_root.cache_clear()

    try:
        root = runtime_paths.get_user_data_root()

        assert root == target_root
        assert (target_root / "custom_formulas.json").exists()
        assert (target_root / "custom_properties.json").exists()
        assert (target_root / "chemease.db").exists()
    finally:
        runtime_paths.get_user_data_root.cache_clear()
