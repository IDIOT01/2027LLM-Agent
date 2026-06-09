@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"

echo ===============================
echo   OfferRadar
echo ===============================
echo.

REM === 检查 Python ===
where python >nul 2>&1
if errorlevel 1 (
    where python3 >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] 未找到 Python
        echo   请安装 Python 3.9+: https://www.python.org/downloads/
        echo   安装时务必勾选 "Add Python to PATH"
        echo.
        pause
        exit /b 1
    )
    set PY=python3
) else (
    set PY=python
)
echo [OK] Python 已就绪

REM === 安装依赖 ===
%PY% -c "import openpyxl; import yaml" >nul 2>&1
if errorlevel 1 (
    echo [INFO] 首次运行，正在安装依赖...
    %PY% -m pip install openpyxl pyyaml -q
)

REM === 直接启动 ===
echo.
echo   浏览器即将打开: http://127.0.0.1:8686
echo   所有配置可在网页上直接修改
echo   关闭此窗口可停止服务
echo.
%PY% launcher.py dashboard
pause
