# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

from __future__ import annotations

from pathlib import Path

from PyInstaller.utils.hooks import collect_all


project_root = Path.cwd()

datas: list[tuple[str, str]] = [
    (str(project_root / "app.py"), "."),
    (str(project_root / "data"), "data"),
    (str(project_root / "projects"), "projects"),
    (str(project_root / "LICENSE"), "."),
    (str(project_root / "README.md"), "."),
]
binaries: list[tuple[str, str]] = []
hiddenimports: list[str] = []

for package_name in ["streamlit", "altair", "pydeck", "pandas", "pydantic", "pint"]:
    collected_datas, collected_binaries, collected_hiddenimports = collect_all(package_name)
    datas += collected_datas
    binaries += collected_binaries
    hiddenimports += collected_hiddenimports

a = Analysis(
    ["launcher.py"],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Chemease",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="Chemease",
)
