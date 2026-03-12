# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

from __future__ import annotations

from pathlib import Path

from PyInstaller.utils.hooks import collect_all


project_root = Path(SPECPATH).resolve()
excluded_top_level_dirs = {
    "__pycache__",
    ".git",
    ".pytest_cache",
    "build",
    "dist",
    "data",
    "projects",
    "scripts",
    "tests",
}


def iter_first_party_packages(root: Path) -> list[str]:
    """Return top-level local packages that must be bundled with the app."""

    packages: list[str] = []
    for child in root.iterdir():
        if not child.is_dir():
            continue
        if child.name in excluded_top_level_dirs:
            continue
        if (child / "__init__.py").exists():
            packages.append(child.name)
    return sorted(packages)


def discover_first_party_modules(root: Path, package_names: list[str]) -> list[str]:
    """Return importable module names for local packages."""

    module_names: list[str] = []
    for package_name in package_names:
        package_root = root / package_name
        for path in package_root.rglob("*.py"):
            relative = path.relative_to(root).with_suffix("")
            parts = list(relative.parts)
            if parts[-1] == "__init__":
                parts = parts[:-1]
            module_names.append(".".join(parts))
    return sorted(set(module_names))


first_party_packages = iter_first_party_packages(project_root)
first_party_hiddenimports = discover_first_party_modules(project_root, first_party_packages)

datas: list[tuple[str, str]] = [
    (str(project_root / "app.py"), "."),
    (str(project_root / "data"), "data"),
    (str(project_root / "projects"), "projects"),
    (str(project_root / "LICENSE"), "."),
    (str(project_root / "README.md"), "."),
]
binaries: list[tuple[str, str]] = []
hiddenimports: list[str] = list(first_party_hiddenimports)

for package_name in first_party_packages:
    datas.append((str(project_root / package_name), package_name))

for package_name in ["streamlit", "altair", "pydeck", "pandas", "pydantic", "pint"]:
    collected_datas, collected_binaries, collected_hiddenimports = collect_all(package_name)
    datas += collected_datas
    binaries += collected_binaries
    hiddenimports += collected_hiddenimports

hiddenimports = sorted(set(hiddenimports))

a = Analysis(
    [str(project_root / "launcher.py")],
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
