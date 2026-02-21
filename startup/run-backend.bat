@echo off
setlocal

set "ROOT=%~dp0.."
set "VENV_ACTIVATE=%ROOT%\.venv\Scripts\activate.bat"
set "REQUIREMENTS=%ROOT%\requirements.txt"

:: ── 1. Activate .venv ───────────────────────────────────────────────
if defined VIRTUAL_ENV (
    echo [*] Virtual environment already active.
) else (
    if not exist "%VENV_ACTIVATE%" (
        echo [!] .venv not found — creating virtual environment...
        python -m venv "%ROOT%\.venv"
    )
    echo [*] Activating .venv...
    call "%VENV_ACTIVATE%"
)

:: ── 2. Check / install dependencies ────────────────────────────────
echo [*] Checking dependencies...
pip install -r "%REQUIREMENTS%" --quiet >nul 2>&1
if errorlevel 1 (
    echo [!] Dependency install failed — retrying with output...
    pip install -r "%REQUIREMENTS%"
    if errorlevel 1 (
        echo [X] Could not install dependencies. Exiting.
        exit /b 1
    )
)
echo [OK] Dependencies up to date.

:: ── 3. Start backend ───────────────────────────────────────────────
echo [*] Starting FastAPI backend...
echo     http://localhost:8000/docs
pushd "%ROOT%"
uvicorn src.api.app:app --reload
popd

endlocal
