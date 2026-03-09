# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

python -m pip install -r requirements-build.txt
pyinstaller --noconfirm --clean Chemease.spec
