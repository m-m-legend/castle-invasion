@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" main.py %*
) else (
    where py >nul 2>nul
    if errorlevel 1 (
        python main.py %*
    ) else (
        py -3 main.py %*
    )
)
if errorlevel 1 (
    echo.
    echo Falha ao executar. Verifique se o Python 3.10 ou superior esta instalado.
    pause
    exit /b 1
)
