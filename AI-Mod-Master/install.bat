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
python -c "from ai_agent.mod_agent import ModAIAgent; print('✓ 所有模块安装成功')"

echo.
echo ========================================
echo 安装完成!
echo.
echo 下一步:
echo 1. 运行 build.bat 打包为 EXE
echo 2. 或直接运行：python main_gui.py
echo.
echo 本地大模型配置说明:
echo - Ollama: http://localhost:11434/v1
echo - LM Studio: http://localhost:1234/v1
echo ========================================
pause
