<#
.SYNOPSIS
    Activate the virtual environment, verify dependencies, and start the FastAPI backend.
#>

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Definition)
$VenvActivate = Join-Path $Root '.venv\Scripts\Activate.ps1'
$Requirements = Join-Path $Root 'requirements.txt'

# ── 1. Activate .venv ────────────────────────────────────────────────
if (-not $env:VIRTUAL_ENV) {
    if (-not (Test-Path $VenvActivate)) {
        Write-Host '[!] .venv not found — creating virtual environment...' -ForegroundColor Yellow
        python -m venv (Join-Path $Root '.venv')
    }
    Write-Host '[*] Activating .venv...' -ForegroundColor Cyan
    & $VenvActivate
} else {
    Write-Host '[*] Virtual environment already active.' -ForegroundColor Green
}

# ── 2. Check / install dependencies ─────────────────────────────────
Write-Host '[*] Checking dependencies...' -ForegroundColor Cyan
pip install -r $Requirements --quiet 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host '[!] Dependency install failed — retrying with output...' -ForegroundColor Yellow
    pip install -r $Requirements
    if ($LASTEXITCODE -ne 0) {
        Write-Host '[X] Could not install dependencies. Exiting.' -ForegroundColor Red
        exit 1
    }
}
Write-Host '[OK] Dependencies up to date.' -ForegroundColor Green

# ── 3. Start backend ────────────────────────────────────────────────
Write-Host '[*] Starting FastAPI backend...' -ForegroundColor Cyan
Write-Host '    http://localhost:8000/docs' -ForegroundColor DarkGray
Push-Location $Root
uvicorn src.api.app:app --reload
Pop-Location
