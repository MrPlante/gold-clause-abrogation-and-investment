#!/usr/bin/env bash
# Create the project venv from requirements.lock (the exact replication
# environment; direct vs transitive deps documented in its header).
set -euo pipefail
cd "$(dirname "$0")"
python3 -m venv --clear .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -r requirements.lock
echo "Done. Activate with: source .venv/bin/activate"
