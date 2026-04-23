@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    py -3.12 -m venv .venv
    call ".venv\Scripts\python.exe" -m pip install --upgrade pip
    call ".venv\Scripts\python.exe" -m pip install -r requirements.txt
)

start "" cmd /c "timeout /t 3 >nul && start http://127.0.0.1:8060"
".venv\Scripts\python.exe" app.py

endlocal
