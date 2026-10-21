@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m unittest discover -s tests -v
) else (
    where py >nul 2>nul
    if errorlevel 1 (
        python -m unittest discover -s tests -v
    ) else (
        py -3 -m unittest discover -s tests -v
    )
)
exit /b %errorlevel%
