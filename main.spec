# -*- mode: python ; coding: utf-8 -*-
import os


# Specific Analysis.datas files to exclude in dist
blocklist = {
    'material-design-icons-4.0.0.tar.gz',
    'map_data_old.geojson',
    'HUC8_WGS84.json',
}

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('Resources/WebMap', 'Resources/WebMap'),
        ('Resources/Icons', 'Resources/Icons'),
        ('Resources/templates', 'Resources/templates'),
        ('pyproject.toml', '.')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
    optimize=0,
)
a.datas = [item for item in a.datas if os.path.basename(item[0]) not in blocklist]

pyz = PYZ(a.pure)

splash = Splash(
    'Resources/Icons/Splash.png',
    binaries=a.binaries,
    datas=a.datas,
    text_pos=(115, 70),
    text_size=18,
    text_color='white',
    text_default='Loading PyForecast...',
    max_img_size=(480, 480),
)

exe = EXE(
    pyz,
    splash,
    a.scripts,
    a.datas,
    [],
    exclude_binaries=True,
    name='PyForecast',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['Resources/Icons/AppIcon.ico'],
)

coll = COLLECT(
    exe,
    splash.binaries,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
