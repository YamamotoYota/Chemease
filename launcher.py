# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Executable launcher for the Streamlit application."""

from __future__ import annotations

import sys
import threading
import time
import webbrowser
from pathlib import Path

from streamlit.web import cli as stcli


def resolve_resource_path(relative_path: str) -> str:
    """Resolve a path both in source mode and PyInstaller mode."""

    if getattr(sys, "_MEIPASS", None):
        return str(Path(sys._MEIPASS) / relative_path)
    return str(Path(__file__).resolve().parent / relative_path)


def open_browser_later(url: str, delay_seconds: float = 1.5) -> None:
    """Open the local Streamlit URL shortly after startup."""

    def _runner() -> None:
        time.sleep(delay_seconds)
        webbrowser.open(url)

    threading.Thread(target=_runner, daemon=True).start()


def main() -> int:
    """Launch the bundled Streamlit application."""

    port = 8501
    app_path = resolve_resource_path("app.py")
    open_browser_later(f"http://127.0.0.1:{port}")
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--server.headless=true",
        f"--server.port={port}",
        "--browser.gatherUsageStats=false",
    ]
    return stcli.main()


if __name__ == "__main__":
    raise SystemExit(main())
