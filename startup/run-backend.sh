#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV_ACTIVATE="$ROOT/.venv/bin/activate"
REQUIREMENTS="$ROOT/requirements.txt"

# ── 1. Activate .venv ────────────────────────────────────────────────
if [ -z "${VIRTUAL_ENV:-}" ]; then
    if [ ! -f "$VENV_ACTIVATE" ]; then
        echo "[!] .venv not found — creating virtual environment..."
        python3 -m venv "$ROOT/.venv"
    fi
    echo "[*] Activating .venv..."
    # shellcheck disable=SC1090
    source "$VENV_ACTIVATE"
else
    echo "[*] Virtual environment already active."
fi

# ── 2. Check / install dependencies ─────────────────────────────────
echo "[*] Checking dependencies..."
if ! pip install -r "$REQUIREMENTS" --quiet > /dev/null 2>&1; then
    echo "[!] Dependency install failed — retrying with output..."
    pip install -r "$REQUIREMENTS"
fi
echo "[OK] Dependencies up to date."

# ── 3. Start backend ────────────────────────────────────────────────
echo "[*] Starting FastAPI backend..."
echo "    http://localhost:8000/docs"
cd "$ROOT"
uvicorn src.api.app:app --reload
