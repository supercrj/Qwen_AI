@echo off
chcp 65001 >nul
echo ========================================
echo AI-Mod-Master 打包脚本 (Windows)
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

echo [1/4] 检查 Python 环境...
python -c "import sys; print(f'Python {sys.version}')"

echo.
echo [2/4] 安装依赖...
pip install -r requirements.txt -q

echo.
echo [3/4] 验证模块导入...
python -c "from ai_agent.mod_agent import ModAIAgent; print('✓ AI Agent OK')"
python -c "from core.fo4edit_bridge import FO4EditBridge, MockFO4EditBridge; print('✓ FO4Edit Bridge OK')"
python -c "from core.esp_parser import ESPParser, ModModifier; print('✓ ESP Parser OK')"
python -c "from translation.strings_processor import StringsProcessor; print('✓ Strings Processor OK')"

echo.
echo [4/4] 开始打包...
pyinstaller --clean AI-Mod-Master.spec

if exist "dist\AI-Mod-Master.exe" (
    echo.
    echo ========================================
    echo ✓ 打包成功!
    echo 可执行文件位置：dist\AI-Mod-Master.exe
    echo ========================================
    explorer dist
else (
    echo.
    echo [错误] 打包失败，请检查错误信息
)

pause
