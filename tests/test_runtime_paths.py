# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Runtime path tests."""

from __future__ import annotations

from pathlib import Path

import runtime_paths


def test_user_data_dir_can_be_overridden(monkeypatch, tmp_path: Path) -> None:
    override_root = tmp_path / "portable-data"
    monkeypatch.setenv(runtime_paths.ENV_DATA_DIR, str(override_root))
    monkeypatch.delenv(runtime_paths.ENV_USER_DATA_DIR, raising=False)
    runtime_paths.get_user_data_root.cache_clear()

    try:
        root = runtime_paths.get_user_data_root()

        assert root == override_root
        assert runtime_paths.get_project_db_path() == root / "chemease.db"
        assert runtime_paths.get_custom_formula_data_path() == root / "custom_formulas.json"
        assert runtime_paths.get_custom_property_data_path() == root / "custom_properties.json"
    finally:
        runtime_paths.get_user_data_root.cache_clear()


def test_relative_override_is_resolved_from_app_root(monkeypatch, tmp_path: Path) -> None:
    app_root = tmp_path / "Chemease"
    monkeypatch.setenv(runtime_paths.ENV_DATA_DIR, "shared-data")
    monkeypatch.setattr(runtime_paths, "get_app_root", lambda: app_root)
    runtime_paths.get_user_data_root.cache_clear()

    try:
        root = runtime_paths.get_user_data_root()

        assert root == app_root / "shared-data"
    finally:
        runtime_paths.get_user_data_root.cache_clear()


def test_default_workspace_root_is_used_without_override(monkeypatch, tmp_path: Path) -> None:
    app_root = tmp_path / "Chemease"
    monkeypatch.delenv(runtime_paths.ENV_DATA_DIR, raising=False)
    monkeypatch.delenv(runtime_paths.ENV_USER_DATA_DIR, raising=False)
    monkeypatch.setattr(runtime_paths, "get_app_root", lambda: app_root)
    runtime_paths.get_user_data_root.cache_clear()

    try:
        root = runtime_paths.get_user_data_root()

        assert root == app_root / "workspace"
    finally:
        runtime_paths.get_user_data_root.cache_clear()


def test_legacy_repo_local_data_is_migrated(monkeypatch, tmp_path: Path) -> None:
    app_root = tmp_path / "Chemease"
    legacy_root = app_root / "projects"
    legacy_root.mkdir(parents=True, exist_ok=True)
    (legacy_root / "custom_formulas.json").write_text("[]", encoding="utf-8")
    (legacy_root / "custom_properties.json").write_text("[]", encoding="utf-8")
    (legacy_root / "chemease.db").write_text("sqlite", encoding="utf-8")

    target_root = tmp_path / "portable-data"
    monkeypatch.setenv(runtime_paths.ENV_DATA_DIR, str(target_root))
    monkeypatch.setattr(runtime_paths, "get_app_root", lambda: app_root)
    monkeypatch.setattr(runtime_paths, "_legacy_per_user_data_root", lambda: tmp_path / "unused-user-data")
    runtime_paths.get_user_data_root.cache_clear()

    try:
        root = runtime_paths.get_user_data_root()

        assert root == target_root
        assert (target_root / "custom_formulas.json").exists()
        assert (target_root / "custom_properties.json").exists()
        assert (target_root / "chemease.db").exists()
    finally:
        runtime_paths.get_user_data_root.cache_clear()
