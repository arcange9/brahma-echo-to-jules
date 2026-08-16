# -*- mode: python ; coding: utf-8 -*-
# Brahma Echo — PyInstaller Specification File
# Builds a Windows x64 onedir distribution with all dependencies bundled

import os
import sys
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules, collect_dynamic_libs

block_cipher = None

# === Data files and binaries ===
datas = []
binaries = []
hiddenimports = []

# --- PyQt6 ---
tmp_d, tmp_b, tmp_h = collect_all('PyQt6')
datas += tmp_d; binaries += tmp_b; hiddenimports += tmp_h

# --- OpenCV ---
tmp_d, tmp_b, tmp_h = collect_all('cv2')
datas += tmp_d; binaries += tmp_b; hiddenimports += tmp_h

# --- MediaPipe ---
tmp_d, tmp_b, tmp_h = collect_all('mediapipe')
datas += tmp_d; binaries += tmp_b; hiddenimports += tmp_h

# --- Google GenAI ---
tmp_d, tmp_b, tmp_h = collect_all('google.genai')
datas += tmp_d; binaries += tmp_b; hiddenimports += tmp_h
tmp_d, tmp_b, tmp_h = collect_all('google.generativeai')
datas += tmp_d; binaries += tmp_b; hiddenimports += tmp_h

# --- Other heavy packages that need collect_all ---
for pkg in ['numpy', 'PIL', 'matplotlib', 'reportlab', 'openpyxl',
            'pptx', 'docx', 'cryptography', 'fastapi', 'uvicorn',
            'edge_tts', 'qrcode', 'pydantic', 'starlette',
            'google.api_core', 'google.auth', 'google.protobuf',
            'grpc', 'discord', 'aiohttp']:
    try:
        tmp_d, tmp_b, tmp_h = collect_all(pkg)
        datas += tmp_d; binaries += tmp_b; hiddenimports += tmp_h
    except Exception:
        pass

# --- Packages needing hidden imports only ---
for pkg in ['sounddevice', 'pyaudio', 'comtypes', 'pycaw.pycaw', 'psutil',
            'send2trash', 'pyperclip', 'pygetwindow', 'pywinauto',
            'pyautogui', 'pytweening', 'pyscreeze', 'pymsgbox', 'pyrect',
            'mss', 'mss.tools', 'beautifulsoup4', 'bs4',
            'duckduckgo_search', 'youtube_transcript_api',
            'win10toast', 'python_kasa', 'kasa',
            'anyio', 'h11', 'httpcore', 'httpx', 'sniffio',
            'watchfiles', 'websockets', 'pyee',
            'typing_inspection', 'tabulate', 'tqdm',
            'charset_normalizer', 'certifi', 'idna', 'urllib3',
            'requests', 'flatbuffers', 'absl',
            'contourpy', 'fonttools', 'cycler', 'kiwisolver',
            'lxml', 'et_xmlfile', 'defusedxml', 'lxml.etree',
            'click', 'colorama', 'distro', 'greenlet',
            'pyasn1', 'pyasn1_modules', ' mashumaro',
            'proto_plus', 'tenacity', 'multidict', 'yarl',
            'propcache', 'aiohappyeyeballs', 'aiosignal',
            'frozenlist', 'attrs', 'python_multipart',
            'pydantic_core', 'annotated_types']:
    try:
        hiddenimports += collect_submodules(pkg)
    except Exception:
        pass
    hiddenimports.append(pkg)

# --- Windows-specific ---
hiddenimports += [
    'winreg', 'ctypes.wintypes', 'ctypes.macholib',
    'comtypes', 'comtypes.client', 'comtypes.gen',
    'pycaw.pycaw', 'pycaw',
    'pywinauto', 'pywinauto.application', 'pywinauto.findwindows',
    'pywinauto.controls', 'pywinauto.findwindows',
]

# --- Stdlib modules missed by PyInstaller analysis ---
hiddenimports += [
    'unittest', 'unittest.mock', 'unittest.case',
    'unittest.loader', 'unittest.runner', 'unittest.suite',
    'unittest.result', 'unittest.signals', 'unittest.util',
    'unittest.async_case',
    'html', 'html.parser', 'html.entities',
    'http', 'http.client', 'http.server',
    'email', 'email.mime', 'email.parser', 'email.utils',
]
# --- Audio/MediaPipe model data ---
datas += [
    ('config/models', 'config/models'),
    ('config/templates', 'config/templates'),
    ('config/brahma_connect.json', 'config'),
    ('config/brahma_connect', 'config/brahma_connect'),
    ('config/create_desktop_shortcut.ps1', 'config'),
]

# --- Assets ---
datas += [
    ('assets', 'assets'),
]

# --- Core (prompt.txt etc) ---
datas += [
    ('core', 'core'),
]

# --- Memory module ---
datas += [
    ('memory', 'memory'),
]

# --- Smart home module ---
datas += [
    ('smart_home', 'smart_home'),
]

# --- Brahma connect ---
datas += [
    ('brahma_connect', 'brahma_connect'),
]

# --- Dashboard ---
datas += [
    ('dashboard', 'dashboard'),
]

# --- Plugin system ---
datas += [
    ('plugins', 'plugins'),
]

# --- Actions (all submodules) ---
datas += [
    ('actions', 'actions'),
]

# --- Agent modules ---
datas += [
    ('agent', 'agent'),
]

# --- Config package ---
datas += [
    ('config/__init__.py', 'config'),
]

# --- Auth package ---
datas += [
    ('auth', 'auth'),
]

# Exclude unnecessary modules to reduce size
excludes = [
    'tkinter', 'test', 'unittest', 'pydoc', 'doctest',
    'distutils', 'lib2to3', 'turtle', 'turtledemo',
    'http.server', 'pdb', 'profile', 'pstats',
    'numpy.f2py.tests', 'numpy.tests', 'numpy.distutils',
    'matplotlib.tests', 'matplotlib.testing',
    'pytest', '_pytest',
    'google.genai.tests',
]

a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath('.')],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=1,
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
    upx_exclude=[],
    runtime_tmpdir=None,
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
