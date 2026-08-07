# launcher.spec
# Build with: pyinstaller launcher.spec
#
# Naming convention Tauri requires for sidecars:
# <name>-<target-triple>.exe  e.g. django-backend-x86_64-pc-windows-msvc.exe
# Run `rustc -Vv` to find your triple, then rename the dist output accordingly
# (or set the name below directly, see notes at bottom).

import sys
from PyInstaller.utils.hooks import collect_submodules

hidden_imports = (
    collect_submodules("django")
    + collect_submodules("statsforecast")
    + collect_submodules("pandas")
    + collect_submodules("whitenoise")
    + [
        "waitress",
        "ms.settings",
        "ms.wsgi",
    ]
)

a = Analysis(
    ["launcher.py"],
    pathex=["."],
    binaries=[],
    datas=[
        ("templates", "templates"),
        ("theme/templates", "theme/templates"),
        ("theme/static", "theme/static"),
        (".venv/Lib/site-packages/tailwind/templates", "tailwind/templates"),
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="django-backend-x86_64-pc-windows-msvc",
    console=True,
    debug=False,
    upx=False,
)