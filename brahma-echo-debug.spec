# -*- mode: python ; coding: utf-8 -*-
# Brahma Echo — PyInstaller Debug Specification File
# Same as brahma-echo.spec but with console=True for debugging.
# Produces: dist/BrahmaEchoDebug/BrahmaEchoDebug.exe
#
# This build shows a console window with logging output.
# Use it when diagnosing crashes or startup failures.

import os
import sys
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules, collect_dynamic_libs

block_cipher = None

datas = []
binaries = []
hiddenimports = []

# --- PyQt6 ---
tmp_d, tmp_b, tmp_h = collect_all('PyQt6')
datas += tmp_d; binaries += tmp_b; hiddenimports += tmp_h

try:
    from PyInstaller.utils.hooks import qt6
    datas += qt6.get_qt_data_files()
except Exception:
    pass

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

for pkg in ['numpy', 'PIL', 'Pillow', 'matplotlib', 'reportlab', 'openpyxl',
            'pptx', 'python-docx', 'docx', 'cryptography', 'fastapi', 'uvicorn',
            'edge_tts', 'qrcode', 'pydantic', 'pydantic_core', 'starlette',
            'google.api_core', 'google.auth', 'google.protobuf',
            'grpc', 'discord', 'aiohttp', 'httpx', 'httpcore',
            'anyio', 'h11', 'sniffio', 'watchfiles', 'websockets',
            'python_multipart', 'multidict', 'yarl', 'aiosignal',
            'frozenlist', 'attrs', 'certifi', 'charset_normalizer']:
    try:
        tmp_d, tmp_b, tmp_h = collect_all(pkg)
        datas += tmp_d; binaries += tmp_b; hiddenimports += tmp_h
    except Exception:
        pass

try:
    tmp_d, tmp_b, tmp_h = collect_all('playwright')
    datas += tmp_d; binaries += tmp_b; hiddenimports += tmp_h
except Exception:
    pass
hiddenimports += collect_submodules('playwright')

for pkg in ['sounddevice', 'pyaudio', 'comtypes', 'comtypes.gen', 'pycaw.pycaw', 'pycaw',
            'psutil', 'send2trash', 'pyperclip', 'pygetwindow', 'pywinauto',
            'pyautogui', 'pytweening', 'pyscreeze', 'pymsgbox', 'pyrect',
            'mss', 'mss.tools', 'bs4', 'beautifulsoup4',
            'duckduckgo_search', 'youtube_transcript_api',
            'win10toast', 'win11toast', 'python_kasa', 'kasa',
            'anyio', 'h11', 'httpcore', 'httpx', 'sniffio',
            'watchfiles', 'websockets', 'pyee',
            'typing_inspection', 'tabulate', 'tqdm',
            'charset_normalizer', 'certifi', 'idna', 'urllib3',
            'requests', 'flatbuffers', 'absl',
            'contourpy', 'fonttools', 'cycler', 'kiwisolver',
            'lxml', 'lxml.etree', 'et_xmlfile', 'defusedxml',
            'click', 'colorama', 'distro', 'greenlet',
            'pyasn1', 'pyasn1_modules', 'mashumaro',
            'proto_plus', 'tenacity', 'multidict', 'yarl',
            'propcache', 'aiohappyeyeballs', 'aiosignal',
            'frozenlist', 'attrs', 'python_multipart',
            'pydantic_core', 'annotated_types',
            'pyparsing', 'httplib2', 'google.ai',
            'edge_tts', 'websocket', 'rel',
            'markdown_it', 'mdurl', 'rich', 'pygments',
            'shellingham', 'platformdirs',
            'google.api_core', 'google.auth', 'google.auth.transport',
            'google.auth.transport.requests', 'google.auth.transport.grpc',
            'google.oauth2', 'google.oauth2.credentials',
            'google.protobuf', 'google.protobuf.json_format',
            'grpc', 'grpc.aio', 'grpc.aio._call',
            'scipy', 'scipy.special', 'scipy._lib',
            'screeninfo', 'pywin32', 'win32com', 'win32com.client',
            'pythoncom', 'servicemanager',
            'filelock', 'tqdm', 'colorama']:
    try:
        hiddenimports += collect_submodules(pkg)
    except Exception:
        pass
    if pkg not in hiddenimports:
        hiddenimports.append(pkg)

hiddenimports += [
    'winreg', 'ctypes.wintypes', 'ctypes.macholib',
    'comtypes', 'comtypes.client', 'comtypes.gen',
    'pycaw.pycaw', 'pycaw',
    'pywinauto', 'pywinauto.application', 'pywinauto.findwindows',
    'pywinauto.controls', 'pywinauto.controls.uiawrapper',
    'pywinauto.controls.win32_controls',
    'pywinauto.uia_defines', 'pywinauto.win32structures',
    'win32api', 'win32con', 'win32gui', 'win32process',
]

hiddenimports += [
    'unittest', 'unittest.mock', 'unittest.case',
    'unittest.loader', 'unittest.runner', 'unittest.suite',
    'unittest.result', 'unittest.signals', 'unittest.util',
    'unittest.async_case',
    'html', 'html.parser', 'html.entities',
    'http', 'http.client', 'http.server',
    'email', 'email.mime', 'email.parser', 'email.utils',
    'json', 'xml', 'xml.etree', 'xml.etree.ElementTree',
    'sqlite3', 'socket', 'socketserver',
    'wave', 'struct', 'queue', 'multiprocessing',
    'importlib', 'importlib.util', 'importlib.machinery',
]

datas += [
    ('config/models', 'config/models'),
    ('config/templates', 'config/templates'),
    ('config/brahma_connect.json', 'config'),
    ('config/brahma_connect', 'config/brahma_connect'),
    ('config/create_desktop_shortcut.ps1', 'config'),
    ('assets', 'assets'),
    ('core', 'core'),
    ('memory', 'memory'),
    ('smart_home', 'smart_home'),
    ('brahma_connect', 'brahma_connect'),
    ('dashboard', 'dashboard'),
    ('plugins', 'plugins'),
    ('actions', 'actions'),
    ('agent', 'agent'),
    ('config/__init__.py', 'config'),
    ('auth', 'auth'),
]

for py_file in [
    'main.py', 'ui.py', 'or_client.py', 'plugin_manager.py',
    'brahma_logger.py', 'brahma_init.py', 'brahma_paths.py',
    'workspace_store.py', 'discord_bot.py', 'gesture_utils.py',
    'smart_home_page_new.py',
]:
    if os.path.exists(py_file):
        datas.append((py_file, '.'))

excludes = [
    'tkinter', 'test', 'tests',
    'distutils', 'lib2to3', 'turtle', 'turtledemo',
    'pdb', 'profile', 'pstats',
    'numpy.f2py.tests', 'numpy.tests', 'numpy.distutils',
    'matplotlib.tests', 'matplotlib.testing',
    'pytest', '_pytest',
    'google.genai.tests',
    'IPython', 'jupyter', 'notebook',
    'sphinx', 'docutils',
    'setuptools', 'pip', 'wheel',
    'pydoc', 'doctest',
    '2to3', 'venv', 'ensurepip',
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
    name='BrahmaEchoDebug',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[
        'python311.dll', 'python3.dll',
        'PyQt6\\Qt6\\bin\\*.dll',
        'vcruntime140.dll', 'vcruntime140_1.dll',
        'msvcp140.dll',
    ],
    runtime_tmpdir=None,
    console=True,  # Show console for debug output
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
    name='BrahmaEchoDebug',
)
