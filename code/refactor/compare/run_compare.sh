#!/usr/bin/env bash
# Run Stata export, Python export, and diff report.
# Usage (from anywhere):
#   bash code/refactor/compare/run_compare.sh
#   bash code/refactor/compare/run_compare.sh --fail-on-mismatch

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
REFACTOR="${REPO_ROOT}/code/refactor"
VENV_PY="${REFACTOR}/.venv/bin/python"

echo "==> Stata export (reghdfe + winsor2)"
bash "${REFACTOR}/scripts/run_stata_do.sh" "${SCRIPT_DIR}/export_regressions.do"
LOG="${REPO_ROOT}/logs/stata/export_regressions.log"
if [[ -f "${LOG}" ]]; then
  if grep -E "^\s*r\([0-9]+\);\s*$" "${LOG}" | grep -v "end of do-file" >/dev/null 2>&1; then
    echo "Stata log may contain errors; see ${LOG}" >&2
    tail -30 "${LOG}" >&2
    exit 1
  fi
fi

if [[ ! -f "${SCRIPT_DIR}/output/stata_regressions.csv" ]]; then
  echo "ERROR: Stata did not write stata_regressions.csv" >&2
  exit 1
fi

echo "==> Python export"
cd "${REPO_ROOT}"
"${VENV_PY}" "${SCRIPT_DIR}/export_python.py"

echo "==> Compare"
"${VENV_PY}" "${SCRIPT_DIR}/compare_results.py" "$@"

echo "Done. See ${SCRIPT_DIR}/output/comparison_report.md"
