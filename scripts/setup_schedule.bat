@echo off
REM 秋招Agent 定时任务配置（Windows 任务计划程序）
REM 用法: setup_schedule.bat [小时] [分钟]
REM 示例: setup_schedule.bat 9 0

setlocal

set SCRIPT_DIR=%~dp0..
set PYTHON_PATH=python
set HOUR=%1
set MINUTE=%2
if "%HOUR%"=="" set HOUR=9
if "%MINUTE%"=="" set MINUTE=0

set TASK_NAME=QiuzhaoAgent

echo === 秋招Agent 定时任务配置 (Windows) ===
echo 脚本目录: %SCRIPT_DIR%
echo 执行时间: 每天 %HOUR%:%MINUTE%
echo.

REM 删除旧任务（忽略错误）
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1

REM 创建新任务
schtasks /create ^
    /tn "%TASK_NAME%" ^
    /tr "\"%PYTHON_PATH%\" \"%SCRIPT_DIR%\launcher.py\" run --lite" ^
    /sc daily ^
    /st %HOUR%:%MINUTE% ^
    /rl highest ^
    /f

if %errorlevel% equ 0 (
    echo [OK] 定时任务已创建！
    echo.
    echo 常用命令:
    echo   手动触发: schtasks /run /tn "%TASK_NAME%"
    echo   查看状态: schtasks /query /tn "%TASK_NAME%"
    echo   删除任务: schtasks /delete /tn "%TASK_NAME%" /f
) else (
    echo [FAIL] 创建失败，请以管理员身份运行
)

endlocal
