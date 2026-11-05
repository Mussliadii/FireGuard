#!/usr/bin/env bash
# One-shot local dev setup for the FastAPI inference backend.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Done. Activate with: source backend/venv/bin/activate"
