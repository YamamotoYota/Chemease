# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Runtime path helpers for bundled resources and writable user data."""

from __future__ import annotations

import os
import shutil
import sys
from functools import lru_cache
from pathlib import Path


APP_NAME = "Chemease"
ENV_USER_DATA_DIR = "CHEMEASE_USER_DATA_DIR"
LEGACY_USER_DATA_FILENAMES = ("custom_formulas.json", "custom_properties.json", "chemease.db")


def get_bundle_root() -> Path:
    """Return the directory that contains bundled read-only resources."""

    if getattr(sys, "_MEIPASS", None):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def _default_user_data_root() -> Path:
    """Return the per-user writable data directory for the current platform."""

    if sys.platform == "win32":
        base_dir = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA")
        if base_dir:
            return Path(base_dir) / APP_NAME
        return Path.home() / "AppData" / "Local" / APP_NAME

    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_NAME

    xdg_data_home = os.getenv("XDG_DATA_HOME")
    if xdg_data_home:
        return Path(xdg_data_home) / APP_NAME
    return Path.home() / ".local" / "share" / APP_NAME


@lru_cache(maxsize=1)
def get_user_data_root() -> Path:
    """Return and create the writable user-data directory."""

    override = os.getenv(ENV_USER_DATA_DIR)
    root = Path(override).expanduser() if override else _default_user_data_root()
    root.mkdir(parents=True, exist_ok=True)
    _migrate_legacy_user_data(root)
    return root


def _migrate_legacy_user_data(target_root: Path) -> None:
    """Copy legacy repo-local user data into the writable per-user directory once."""

    legacy_root = get_bundle_root() / "projects"
    if legacy_root == target_root or not legacy_root.exists():
        return

    for filename in LEGACY_USER_DATA_FILENAMES:
        source_path = legacy_root / filename
        target_path = target_root / filename
        if source_path.exists() and not target_path.exists():
            shutil.copy2(source_path, target_path)


def get_formula_data_dir() -> Path:
    """Return the bundled directory containing base formula JSON files."""

    return get_bundle_root() / "data" / "formulas"


def get_property_data_path() -> Path:
    """Return the bundled path containing base property data."""

    return get_bundle_root() / "data" / "properties" / "substances.json"


def get_custom_formula_data_path() -> Path:
    """Return the writable path for user-defined formulas."""

    return get_user_data_root() / "custom_formulas.json"


def get_custom_property_data_path() -> Path:
    """Return the writable path for user-defined properties."""

    return get_user_data_root() / "custom_properties.json"


def get_project_db_path() -> Path:
    """Return the writable SQLite path for saved projects and cases."""

    return get_user_data_root() / "chemease.db"


def describe_user_data_root() -> str:
    """Return a human-readable path used in the UI."""

    return str(get_user_data_root())
