@echo off
chcp 65001 >nul
echo ========================================
echo AI-Mod-Master 一键安装脚本 (Windows)
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python!
    echo.
    echo 请先安装 Python 3.10+:
    echo https://www.python.org/downloads/
    echo.
    echo 安装时请勾选 "Add Python to PATH"
    pause
    exit /b 1
)

echo [步骤 1/3] 创建虚拟环境...
if not exist "venv" (
    python -m venv venv
    echo ✓ 虚拟环境创建成功
) else (
    echo ✓ 虚拟环境已存在
)

echo.
echo [步骤 2/3] 激活虚拟环境并安装依赖...
call venv\Scripts\activate.bat
pip install -r requirements.txt

echo.
echo [步骤 3/3] 验证安装...
python -c "from ai_agent.mod_agent import ModAIAgent; print('AI Agent: OK')"
python -c "from core.fo4edit_bridge import FO4EditBridge, MockFO4EditBridge; print('FO4Edit Bridge: OK')"
python -c "from core.esp_parser import ESPParser, ModModifier; print('ESP Parser: OK')"
python -c "from translation.strings_processor import StringsProcessor; print('Strings Processor: OK')"

echo.
echo ========================================
echo 安装完成!
echo.
echo 下一步操作:
echo 1. 安装本地大模型 (推荐 Ollama):
echo    - 下载：https://ollama.ai/download
echo    - 运行：ollama pull qwen2.5:7b
echo.
echo 2. (可选) 安装 FO4Edit:
echo    - 下载：https://github.com/xEdit/xEdit/releases
echo    - 将 FO4Edit.exe 路径配置到程序中
echo.
echo 3. 打包为 EXE:
echo    - 双击运行 build.bat
echo.
echo 4. 直接运行 GUI (开发模式):
echo    - python main_gui.py
echo.
echo ========================================
pause
