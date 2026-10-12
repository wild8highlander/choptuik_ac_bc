#!/usr/bin/env bash
# run_logged.sh — a logged, hash-stamped verification run of dsi_lab.
#
# One-shot mode (runs everything in one go):
#     bash scripts/run_logged.sh            # = make verify
#     bash scripts/run_logged.sh test quick # subset
#
# Stage mode (for slow hosts / CI steps — one shared log):
#     bash scripts/run_logged.sh start                 # header, prints STAMP
#     bash scripts/run_logged.sh stage STAMP test      # append: make test
#     bash scripts/run_logged.sh stage STAMP validate
#     bash scripts/run_logged.sh stage STAMP run
#     bash scripts/run_logged.sh finish STAMP          # sha256 footer
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
mkdir -p logs

_stamp() { date -u +%Y%m%dT%H%M%SZ; }

_header() {
  {
    echo "==============================================================="
    echo "DSI lab logged verification run"
    echo "  UTC    : $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
    echo "  host   : $(uname -srm)"
    echo "  git    : $(git rev-parse --short HEAD 2>/dev/null || echo 'no git')"
    echo "  python : $(python3 --version)"
    python3 - <<'PY' 2>/dev/null || true
import numpy, scipy, matplotlib
print(f"  numpy  : {numpy.__version__}")
print(f"  scipy  : {scipy.__version__}")
print(f"  mpl    : {matplotlib.__version__}")
PY
    echo "==============================================================="
  } >> "$LOG"
}

_footer() {
  RC=$1
  {
    echo "==============================================================="
    echo "sha256 of results/*.json after the run:"
    sha256sum results/*.json
    echo "exit code: $RC"
    echo "==============================================================="
  } >> "$LOG"
  tail -4 "$LOG"
  echo "LOG: $LOG (exit $RC)"
}

if [ "${1:-}" = "start" ]; then
  STAMP="$(_stamp)"
  LOG="logs/run_${STAMP}.log"
  echo "$STAMP"
  : > "$LOG"
  LOG="$LOG" _header
  echo "LOG: $LOG (started)" >&2
  exit 0
fi

if [ "${1:-}" = "stage" ]; then
  STAMP="${2:?stamp required}"; shift 2
  LOG="logs/run_${STAMP}.log"
  {
    echo ""
    echo "###############################################################"
    echo "# STAGE: $*"
    echo "###############################################################"
  } >> "$LOG"
  set +e
  PYTHONUNBUFFERED=1 make "$@" >> "$LOG" 2>&1
  RC=$?
  set -e
  echo "stage done: $* (exit $RC)"
  exit "$RC"
fi

if [ "${1:-}" = "finish" ]; then
  STAMP="${2:?stamp required}"
  LOG="logs/run_${STAMP}.log"
  set +e
  _footer 0
  exit 0
fi

# --- one-shot mode ----------------------------------------------------------
STAMP="$(_stamp)"
LOG="logs/run_${STAMP}.log"
: > "$LOG"
LOG="$LOG" _header
set +e
if [ "$#" -gt 0 ]; then
  make "$@" >> "$LOG" 2>&1
else
  make verify >> "$LOG" 2>&1
fi
RC=$?
set -e
LOG="$LOG" _footer "$RC"
exit "$RC"
