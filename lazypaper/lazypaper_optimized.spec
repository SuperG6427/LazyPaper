# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Excluir módulos innecesarios para reducir tamaño
excluded_imports = [
    'matplotlib', 'scipy', 'pandas', 'tensorflow', 'keras',
    'sklearn', 'sqlite3', 'test', 'unittest', 'email',
    'html', 'http', 'xml', 'multiprocessing', 'pydoc',
    'pdb', 'curses', 'lib2to3', 'tkinter.test'
]

a = Analysis(
    ['lazypaper.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/images/icon.png', 'assets/images'),
        ('icons/icon.ico', 'icons'),
        ('icons/icon.png', 'icons'),
    ],
    hiddenimports=[
        'PIL._tkinter_finder',
        'numpy.core._multiarray_umath',
        'numpy.core._multiarray_tests',
        'packaging.specifiers',
        'packaging.requirements',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL.ImageDraw',
        'PIL.ImageFilter',
        'PIL.ImageOps',
        'tkinter',
        'tkinter.font',
        'queue',
        'concurrent.futures',
        'threading',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excluded_imports,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=2,  # Optimización máxima
)

# Excluir módulos pesados de numpy que no necesitamos
for mod in list(a.pure):
    if mod.name and any(x in mod.name for x in ['numpy.tests', 'numpy.f2py', 'numpy.distutils']):
        a.pure.remove(mod)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Lazypaper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Comprimir con UPX
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sin consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icons/icon.ico',
)