#!/usr/bin/env bash
# Run Stata batch with logs under logs/stata/ (repo root passed to the .do file).
#
# Usage:
#   bash code/refactor/scripts/run_stata_do.sh path/to/script.do [extra-do-args...]
#
# The .do file should accept the repository root as its first argument (see export_regressions.do).

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: run_stata_do.sh path/to/script.do [args...]" >&2
  exit 2
fi

DO_FILE="$1"
shift

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
LOG_DIR="${REPO_ROOT}/logs/stata"
STATA_BIN="${STATA_BIN:-/usr/local/stata/stata-mp}"

if [[ ! -f "${DO_FILE}" ]]; then
  echo "ERROR: do-file not found: ${DO_FILE}" >&2
  exit 1
fi

if ! command -v "${STATA_BIN}" >/dev/null 2>&1; then
  echo "ERROR: Stata not found at ${STATA_BIN}. Set STATA_BIN." >&2
  exit 127
fi

DO_ABS="$(cd "$(dirname "${DO_FILE}")" && pwd)/$(basename "${DO_FILE}")"
DO_BASE="$(basename "${DO_ABS}" .do)"

mkdir -p "${LOG_DIR}"
cd "${LOG_DIR}"

"${STATA_BIN}" -b do "${DO_ABS}" "${REPO_ROOT}" "$@"

LOG="${LOG_DIR}/${DO_BASE}.log"
if [[ -f "${LOG}" ]]; then
  echo "Stata log: ${LOG}"
else
  echo "WARNING: expected log not found at ${LOG}" >&2
fi
