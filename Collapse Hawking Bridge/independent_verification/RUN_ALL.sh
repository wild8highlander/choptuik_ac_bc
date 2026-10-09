#!/usr/bin/env bash
# RUN_ALL.sh — run the full IVP-15 independent verification suite.
#
# Usage (from anywhere):
#   bash independent_verification/RUN_ALL.sh
#
# Optional environment:
#   IVP_ZIP=/path/to/Collapse-Hawking-Bridge-2.0.0.zip   (for IVP-01)
#   IVP_FAST=1    skip the heavy numerical ladders (IVP-09..12, 13)
#
# Every script writes results/<IVPnn>.json + a log under results/logs/.
# Runtime: ~35-45 min on one core (IVP-09..12 dominate); ~5 min with
# IVP_FAST=1.
set -u
cd "$(dirname "$0")" || exit 1
mkdir -p results/logs

echo "======================================================================"
echo " INDEPENDENT VERIFICATION PROTOCOL (IVP-15) — Collapse-Hawking Bridge"
echo "======================================================================"

run() {
  local id="$1" script="$2"
  echo ""
  echo "----------------------------------------------------------------------"
  echo ">>> ${id}"
  echo "----------------------------------------------------------------------"
  if [ -n "${IVP_FAST:-}" ] && [[ "$script" == *IVP09* || "$script" == *IVP11* ]]; then
    echo "   skipped (IVP_FAST=1)"
    return 0
  fi
  case "$script" in
    *.sh) bash "$script" ;;
    *)    python3 "$script" ;;
  esac
  local rc=$?
  echo "<<< ${id} exit=${rc}"
  return 0   # keep going regardless; the summary shows the verdicts
}

run "IVP-01" IVP01_release_integrity.py
run "IVP-02" IVP02_clean_environment.sh
run "IVP-03" IVP03_dependency_audit.py
run "IVP-04" IVP04_constants_rederive.py
run "IVP-05" IVP05_dimensions.py
run "IVP-06" IVP06_roberts_symbolic.py
run "IVP-07" IVP07_convergence.py
run "IVP-08" IVP08_constraints.py
if [ -z "${IVP_FAST:-}" ]; then
  run "IVP-09" IVP09_threshold_blind.py      # heavy: full blind ladder
  run "IVP-10" IVP10_threshold_robustness.py # needs IVP-09
  run "IVP-11" IVP11_gamma_blind.py          # heavy: deep scans
  run "IVP-12" IVP12_resolution_floor.py     # needs IVP-09 + IVP-11
  run "IVP-13" IVP13_echo_blind.py           # needs IVP-09
  run "IVP-14" IVP14_delta_gamma.py          # needs IVP-11 + IVP-13
fi
run "IVP-15" IVP15_cross_language.py

echo ""
echo "======================================================================"
echo " VERDICT SUMMARY"
echo "======================================================================"
python3 summarize.py
