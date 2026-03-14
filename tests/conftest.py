# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Pytest fixtures shared across the test suite."""

from __future__ import annotations

import os

import pytest

import runtime_paths


@pytest.fixture(autouse=True, scope="session")
def isolate_user_data_dir(tmp_path_factory: pytest.TempPathFactory) -> None:
    """Keep tests independent from the developer's local user-data directory."""

    original = os.environ.get(runtime_paths.ENV_USER_DATA_DIR)
    isolated_root = tmp_path_factory.mktemp("chemease-user-data")
    os.environ[runtime_paths.ENV_USER_DATA_DIR] = str(isolated_root)
    runtime_paths.get_user_data_root.cache_clear()

    (isolated_root / "custom_formulas.json").write_text("[]", encoding="utf-8")
    (isolated_root / "custom_properties.json").write_text("[]", encoding="utf-8")
    (isolated_root / "chemease.db").touch()

    try:
        yield
    finally:
        runtime_paths.get_user_data_root.cache_clear()
        if original is None:
            os.environ.pop(runtime_paths.ENV_USER_DATA_DIR, None)
        else:
            os.environ[runtime_paths.ENV_USER_DATA_DIR] = original
