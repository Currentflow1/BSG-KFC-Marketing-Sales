# launcher.spec
#
# Build with:
#
#     pyinstaller launcher.spec
#
# Tauri sidecar:
#
#     django-backend-x86_64-pc-windows-msvc.exe

import os

from PyInstaller.utils.hooks import (
    collect_submodules,
    collect_data_files,
    collect_dynamic_libs,
)


# ---------------------------------------------------------------------------
# Local Django apps (not picked up by collect_submodules, since they're
# your own top-level packages, not third-party ones)
# ---------------------------------------------------------------------------

LOCAL_APPS = [
    "ms",
    "theme",
    "login",
    "dashboard",
    "products",
    "employees",
    "area_prices",
    "customers",
    "orders",
    "records",
    "forecasting",
    "transaction_logs",
]


# ---------------------------------------------------------------------------
# Hidden imports
# ---------------------------------------------------------------------------

hidden_imports = (
    collect_submodules("django")
    + collect_submodules("statsforecast")
    + collect_submodules("pandas")
    + collect_submodules("whitenoise")
    + collect_submodules("tailwind")
    + [module for app in LOCAL_APPS for module in collect_submodules(app)]
    + [
        "waitress",
        "ms.settings",
        "ms.wsgi",
    ]
)


# ---------------------------------------------------------------------------
# Binaries (numba/llvmlite JIT libs used by statsforecast won't always be
# picked up by static import analysis)
# ---------------------------------------------------------------------------

binaries = (
    collect_dynamic_libs("numba")
    + collect_dynamic_libs("llvmlite")
)


# ---------------------------------------------------------------------------
# Data files
# ---------------------------------------------------------------------------

datas = [
    # Project templates
    ("templates", "templates"),

    # Theme templates
    ("theme/templates", "theme/templates"),

    # Theme static files
    ("theme/static", "theme/static"),

    # Orders static files (HTMX / form-navigation JS)
    ("orders/static", "orders/static"),

    # Tailwind templates
    (
        ".venv/Lib/site-packages/tailwind/templates",
        "tailwind/templates",
    ),
]

# django.contrib.admin / django.contrib.auth ship their own templates and
# static files as package data -- collect_submodules() does NOT grab these.
datas += collect_data_files("django.contrib.admin")
datas += collect_data_files("django.contrib.auth")

# Bundle each local app's own templates/ and static/ dirs, since APP_DIRS
# looks these up on disk at runtime and PyInstaller won't auto-include
# non-.py files from your own packages.
for app in LOCAL_APPS:
    for subdir in ("templates", "static"):
        src = os.path.join(app, subdir)
        if os.path.isdir(src):
            datas.append((src, f"{app}/{subdir}"))


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

a = Analysis(
    ["launcher.py"],

    pathex=[
        ".",
    ],

    binaries=binaries,

    datas=datas,

    hiddenimports=hidden_imports,

    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)


# ---------------------------------------------------------------------------
# Python archive
# ---------------------------------------------------------------------------

pyz = PYZ(
    a.pure,
)


# ---------------------------------------------------------------------------
# Executable
# ---------------------------------------------------------------------------

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