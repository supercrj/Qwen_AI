# -*- mode: python ; coding: utf-8 -*-
# AI-Mod-Master PyInstaller 打包配置文件
# 用于生成 Windows standalone EXE 文件

from PyInstaller.utils.hooks import collect_all, collect_submodules

# 收集所有依赖
datas = []
hiddenimports = []

# 核心模块
datas += [('core', 'core')]
datas += [('translation', 'translation')]
datas += [('ai_agent', 'ai_agent')]

# PyQt6 资源
try:
    qt_datas, qt_binaries, qt_hiddenimports = collect_all('PyQt6')
    datas += qt_datas
    hiddenimports += qt_hiddenimports
except Exception:
    pass

# 添加必要的隐藏导入
hiddenimports += [
    'pydantic',
    'requests',
    'xmltodict',
    'lxml',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'core.esp_parser',
    'core.fo4edit_bridge',
    'core.worker',
    'core.config_manager',
    'translation.strings_processor',
    'ai_agent.mod_agent',
]

a = Analysis(
    ['main_gui.py'],
    pathex=[],
    binaries=qt_binaries if 'qt_binaries' in dir() else [],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'pytest',
        'black',
        'fastapi',
        'uvicorn',
        'langchain',
        'openai',
    ],
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
    name='AI-Mod-Master',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 设为 True 可显示调试信息
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可设置图标：icon='resources/icon.ico'
)
