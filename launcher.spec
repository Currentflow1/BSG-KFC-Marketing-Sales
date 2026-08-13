# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = []

for pkg in [
    'waitress',
    'whitenoise',
    'tailwind',
    'statsforecast',
    'coreforecast',
    'utilsforecast',
    'fugue',
    'triad',
    'adagio',
    'numba',
    'llvmlite',
    'pyarrow',
    'statsmodels',
    'scipy',
]:
    tmp_ret = collect_all(pkg)
    datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# --- project data files ---
datas += [
    ('templates', 'templates'),
    ('theme/templates', 'theme/templates'),
    ('theme/static', 'theme/static'),
    ('orders/static', 'orders/static'),
]

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='django-backend-x86_64-pc-windows-msvc',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)