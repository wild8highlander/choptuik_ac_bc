#!/usr/bin/env bash
# ============================================================================
# 02_termux_run.sh — run the einstein_direct validation + campaign on Termux
#
# Usage:
#   bash 02_termux_run.sh            # full: pytest + fixed-grid campaign + zoom campaign
#   bash 02_termux_run.sh --quick    # reduced grid sizes, ~15 min on a phone
#
# The scripts auto-locate the einstein_direct/ folder next to this file or
# inside a local clone of the repository.
# ============================================================================
set -u
QUICK=0
[ "${1:-}" = "--quick" ] && QUICK=1
step() { printf "==> %s\n" "$*"; }
ok()   { printf "  [OK] %s\n" "$*"; }
err()  { printf "  [ERROR] %s\n" "$*"; }

HERE="$(cd "$(dirname "$0")" && pwd)"
ED=""
for cand in "$HERE/einstein_direct" "$HERE/../einstein_direct" "$HOME/choptuik_ac_bc/einstein_direct"; do
  [ -f "$cand/solver.py" ] && ED="$cand" && break
done
[ -z "$ED" ] && { err "einstein_direct/ not found — run 03_push_to_github.sh first or cd next to it"; exit 1; }
ok "module: $ED"
cd "$ED"

step "1/3 Validation suite (pytest)"
python3 -m pytest tests/ -q || { err "validation failed"; exit 1; }

step "2/3 Campaigns"
if [ "$QUICK" = "1" ]; then
  # reduced profile: fixed-grid bisection at N=600, zoom campaign as-is
  python3 choptuik_scaling.py --n-bisect 600 --n-scale 800 --decades 2.0
else
  python3 choptuik_scaling.py --n-bisect 1200
fi
python3 zoom_campaign.py
python3 zoom_campaign_v3.py
python3 spinor_analysis.py
python3 spinor_figures.py

step "3/3 Results"
ls -la results/
ok "Done. JSON results are in einstein_direct/results/"
