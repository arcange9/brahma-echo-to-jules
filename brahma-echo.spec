# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Brahma Echo
# Builds a single-folder distribution with all dependencies

import os
import sys
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules

block_cipher = None

# Collect all data and binaries for heavy packages
datas = []
binaries = []
hiddenimports = []

# PyQt6
tmp_d, tmp_b, tmp_h = collect_all('PyQt6')
datas += tmp_d; binaries += tmp_b; hiddenimports += tmp_h

# opencv
tmp_d, tmp_b, tmp_h = collect_all('cv2')
datas += tmp_d; binaries += tmp_b; hiddenimports += tmp_h

# mediapipe
tmp_d, tmp_b, tmp_h = collect_all('mediapipe')
datas += tmp_d; binaries += tmp_b; hiddenimports += tmp_h

# google-genai / google-generativeai
tmp_d, tmp_b, tmp_h = collect_all('google.genai')
datas += tmp_d; binaries += tmp_b; hiddenimports += tmp_h
tmp_d, tmp_b, tmp_h = collect_all('google.generativeai')
datas += tmp_d; binaries += tmp_b; hiddenimports += tmp_h

# Other packages that need special handling
for pkg in ['sounddevice', 'pyaudio', 'comtypes', 'pycaw', 'psutil', 
            'send2trash', 'openpyxl', 'pptx', 'docx', 'reportlab',
            'edge_tts', 'qrcode', 'beautifulsoup4', 'bs4', 'duckduckgo_search',
            'youtube_transcript_api', 'pyperclip', 'pygetwindow', 'pywinauto',
            'pyautogui', 'cryptography', 'fastapi', 'uvicorn',
            'python_kasa', 'win10toast', 'mss', 'numpy', 'PIL']:
    try:
        tmp_d, tmp_b, tmp_h = collect_all(pkg)
        datas += tmp_d; binaries += tmp_b; hiddenimports += tmp_h
    except Exception:
        try:
            hiddenimports += collect_submodules(pkg)
        except Exception:
            pass

# Add our own data files
datas += [
    ('assets', 'assets'),
    ('config', 'config'),
    ('core', 'core'),
    ('memory', 'memory'),
    ('smart_home', 'smart_home'),
    ('plugins', 'plugins'),
    ('brahma_connect', 'brahma_connect'),
]

# Hidden imports for dynamic imports in the code
hiddenimports += [
    'discord',
    'httpx',
    'httpcore',
    'anyio',
    'h11',
    'sniffio',
    'certifi',
    'charset_normalizer',
    'idna',
    'requests',
    'urllib3',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'test', 'unittest', 'pydoc'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BrahmaEcho',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/Brahma_Lite_Logo.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BrahmaEcho',
)
