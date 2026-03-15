# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Tests for runtime control helpers."""

from __future__ import annotations

from types import SimpleNamespace

import app_runtime


def test_stop_application_returns_false_when_runtime_is_missing(monkeypatch) -> None:
    def raise_runtime_error() -> None:
        raise RuntimeError("runtime unavailable")

    monkeypatch.setattr(app_runtime.streamlit.runtime, "get_instance", raise_runtime_error)

    assert app_runtime.stop_application() is False


def test_stop_application_stops_the_runtime(monkeypatch) -> None:
    state = {"stopped": False}

    def stop() -> None:
        state["stopped"] = True

    runtime = SimpleNamespace(stop=stop)
    monkeypatch.setattr(app_runtime.streamlit.runtime, "get_instance", lambda: runtime)

    assert app_runtime.stop_application() is True
    assert state["stopped"] is True
