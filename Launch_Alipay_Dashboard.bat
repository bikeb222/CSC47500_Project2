@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found.
    echo Please make sure the .venv folder exists in this project directory.
    pause
    exit /b 1
)

start "" cmd /c "timeout /t 3 >nul && start http://127.0.0.1:8050"
".venv\Scripts\python.exe" app.py

endlocal
