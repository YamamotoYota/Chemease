# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Executable launcher for the Streamlit application."""

from __future__ import annotations

import sys
import threading
import time
import webbrowser
import socket

from streamlit.web import cli as stcli
from runtime_paths import get_bundle_root


def resolve_resource_path(relative_path: str) -> str:
    """Resolve a path both in source mode and PyInstaller mode."""

    return str(get_bundle_root() / relative_path)


def find_available_port(preferred_port: int = 8501) -> int:
    """Return an available localhost port, preferring the usual Streamlit port."""

    for port in [preferred_port, 8502, 8503, 8504, 8505]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if probe.connect_ex(("127.0.0.1", port)) != 0:
                return port

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def open_browser_later(url: str, delay_seconds: float = 1.5) -> None:
    """Open the local Streamlit URL shortly after startup."""

    def _runner() -> None:
        time.sleep(delay_seconds)
        webbrowser.open(url)

    threading.Thread(target=_runner, daemon=True).start()


def main() -> int:
    """Launch the bundled Streamlit application."""

    port = find_available_port()
    app_path = resolve_resource_path("app.py")
    open_browser_later(f"http://127.0.0.1:{port}")
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false",
        "--server.headless=true",
        f"--server.port={port}",
        "--browser.gatherUsageStats=false",
    ]
    return stcli.main()


if __name__ == "__main__":
    raise SystemExit(main())
