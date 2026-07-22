#!/usr/bin/env bash
# Create the project venv. Uses requirements.lock (exact versions, for
# replication) when present; falls back to requirements.txt (floors only).
set -euo pipefail
cd "$(dirname "$0")"
python3 -m venv --clear .venv
.venv/bin/python -m pip install --upgrade pip
if [[ -f requirements.lock ]]; then
    .venv/bin/pip install -r requirements.lock
else
    .venv/bin/pip install -r requirements.txt
fi
echo "Done. Activate with: source .venv/bin/activate"
