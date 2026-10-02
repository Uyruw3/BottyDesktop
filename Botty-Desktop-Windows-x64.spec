from PyInstaller.utils.hooks import collect_all

edge_datas, edge_binaries, edge_hiddenimports = collect_all("edge_tts")

a = Analysis(
    ['botty/__main__.py'],
    pathex=[],
    binaries=edge_binaries,
    datas=edge_datas,
    hiddenimports=edge_hiddenimports,
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
    name='Botty-Desktop-Windows-x64',
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
