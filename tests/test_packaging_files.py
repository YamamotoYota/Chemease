# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Regression checks for packaging helper files."""

from __future__ import annotations

from pathlib import Path


def test_spec_file_is_root_relative() -> None:
    text = Path("Chemease.spec").read_text(encoding="utf-8")
    assert "Path(SPECPATH).resolve()" in text
    assert "Path.cwd()" not in text
    assert "iter_first_party_packages" in text
    assert "discover_first_party_modules" in text
    assert "filter_hiddenimports" in text
    assert "datas.append((str(project_root / package_name), package_name))" in text
    assert '(str(project_root / "projects"), "projects")' not in text


def test_build_script_uses_script_directory_and_python_module_entrypoints() -> None:
    text = Path("build_exe.ps1").read_text(encoding="utf-8")
    assert "$MyInvocation.MyCommand.Path" in text
    assert "-m', 'PyInstaller'" in text
    assert "-r', 'requirements.txt'" in text


def test_launcher_disables_streamlit_development_mode() -> None:
    text = Path("launcher.py").read_text(encoding="utf-8")
    assert "--global.developmentMode=false" in text
    assert "find_available_port" in text
