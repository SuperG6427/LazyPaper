# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['lazypaper.py'],
    pathex=[],
    binaries=[],
    datas=[('assets/images', 'assets/images'), ('icons', 'icons')],
    hiddenimports=['PIL._tkinter_finder', 'numpy.core._multiarray_umath', 'packaging.specifiers', 'packaging.requirements', 'pkg_resources', 'email', 'email.mime', 'email.mime.text', 'email.mime.multipart', 'email.mime.base', 'email.mime.image', 'email.mime.application', 'email.utils', 'email.encoders', 'email.header', 'email.charset', 'email.policy', 'email.generator', 'email.iterators', 'email.parser', 'email.feedparser'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'pandas', 'tensorflow', 'keras', 'sklearn', 'test', 'unittest'],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [('O', None, 'OPTION'), ('O', None, 'OPTION')],
    name='Lazypaper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icons\\icon.ico'],
)
