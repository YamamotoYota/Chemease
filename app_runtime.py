# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Helpers for controlling the running Streamlit application."""

from __future__ import annotations

import streamlit.runtime


def stop_application() -> bool:
    """Stop the active Streamlit runtime when available."""

    try:
        runtime = streamlit.runtime.get_instance()
    except RuntimeError:
        return False

    runtime.stop()
    return True
