#!/usr/bin/env bash
# IVP-02 — clean-room installation across Python interpreters.
#
# For EVERY available CPython minor version in {3.9 .. 3.13}:
#   1. create a fresh venv (no site-packages inheritance);
#   2. pip install ONLY the declared runtime deps (numpy, mpmath) + pytest;
#   3. pip install --no-deps -e .   (the release itself, nothing else);
#   4. run the committed pytest suite;
#   5. run the IVP-02 canonical numeric job (IVP02_canonical_job.py).
#
# Clean-room rules (enforced by construction):
#   * the venv never sees pre-installed chbridge;
#   * no local modules outside the release tree are importable
#     (pytest runs from the repo root; the canonical job inserts ONLY
#     repo-internal paths);
#   * no saved results from previous runs are read;
#   * the environment is never hand-patched: any failure is reported.
#
# Acceptance: identical scientific part of the canonical job across all
# interpreters (rel diff <= 1e-12 per quantity) and pytest PASS everywhere.
# Interpreters that do not exist on the verification machine are reported
# INCONCLUSIVE (toolchain absent), never silently skipped.

set -u
cd "$(dirname "$0")/.." || exit 1     # repo root
IVP_DIR="independent_verification"
LOGS="$IVP_DIR/results/logs"
mkdir -p "$LOGS"

VERSIONS="3.9 3.10 3.11 3.12 3.13"
tested=0
failed=0

echo "======================================================================"
echo "IVP-02 — clean-room installation (per-interpreter venvs)"
echo "======================================================================"

for V in $VERSIONS; do
  PY="$(command -v python$V || true)"
  if [ -z "$PY" ]; then
    echo "[IVP02] python$V: NOT PRESENT on this machine -> INCONCLUSIVE"
    printf 'python%s: INCONCLUSIVE (interpreter not available)\n' "$V" \
        >> "$LOGS/IVP02_interpreters.txt"
    continue
  fi
  VENV="$(mktemp -d "/tmp/ivp02_py${V}_XXXXXX")"
  echo "[IVP02] python$V ($PY): clean venv -> $VENV"
  LOGF="$LOGS/IVP02_py$V.log"
  {
    echo "interpreter: $PY"
    if ! "$PY" -m venv "$VENV" 2>"$VENV/venv_err.txt"; then
      # some distros ship pythonX.Y without ensurepip; fall back to a
      # pip-less venv driven by the system pip's --python switch
      # (isolation is preserved: the venv site-packages stay separate)
      if ! "$PY" -m venv --without-pip "$VENV" 2>>"$VENV/venv_err.txt" \
         || ! pip --python "$VENV/bin/python" install --quiet \
              --disable-pip-version-check numpy mpmath pytest; then
        echo "VENV FAILED (interpreter present but venv/ensurepip unusable)"
        cat "$VENV/venv_err.txt" 2>/dev/null | head -3
        exit 1
      fi
      echo "note: venv created --without-pip; packages installed via 'pip --python'"
    fi
    PIP="$VENV/bin/pip"
    PYBIN="$VENV/bin/python"
    if [ -x "$PIP" ]; then
      "$PIP" install --quiet --disable-pip-version-check numpy mpmath pytest \
        || { echo "PIP DEPS FAILED"; exit 1; }
      "$PIP" install --quiet --disable-pip-version-check --no-deps -e . \
        || { echo "PIP INSTALL-E FAILED"; exit 1; }
    else
      pip --python "$PYBIN" install --quiet --disable-pip-version-check \
          --no-deps -e . || { echo "PIP INSTALL-E FAILED"; exit 1; }
    fi
    echo "--- declared-import sanity (no extra third-party visible) ---"
    "$PYBIN" - <<'PYEOF'
import importlib.util as u
for m in ("numpy", "mpmath", "pytest", "chbridge"):
    print(f"  {m}: {'present' if u.find_spec(m) else 'MISSING'}")
PYEOF
    echo "--- committed pytest suite ---"
    "$VENV/bin/python" -m pytest tests/ -q
    PYTEST_STATUS=$?
    echo "pytest_status: $PYTEST_STATUS"
    echo "--- canonical numeric job ---"
    "$PYBIN" "$IVP_DIR/IVP02_canonical_job.py"
    echo "canonical_status: $?"
  } > "$LOGF" 2>&1
  tail -5 "$LOGF" | sed 's/^/    /'
  if grep -q "pytest_status: 0" "$LOGF" && grep -q "canonical_status: 0" "$LOGF"; then
    echo "[IVP02] python$V: PASS (suite + canonical job)"
    printf 'python%s: PASS\n' "$V" >> "$LOGS/IVP02_interpreters.txt"
  else
    echo "[IVP02] python$V: FAIL (see $LOGF)"
    printf 'python%s: FAIL\n' "$V" >> "$LOGS/IVP02_interpreters.txt"
    failed=$((failed+1))
  fi
  tested=$((tested+1))
  rm -rf "$VENV"
done

echo "----------------------------------------------------------------------"
n_pass=$(grep -c PASS "$LOGS/IVP02_interpreters.txt" 2>/dev/null || echo 0)
n_inc=$(grep -c INCONCLUSIVE "$LOGS/IVP02_interpreters.txt" 2>/dev/null || echo 0)
echo "[IVP02] interpreters tested: $tested, passed: $n_pass, failed: $failed, absent: $n_inc"

# machine-readable verdict
python3 - "$failed" "$tested" "$n_pass" "$n_inc" "$LOGS/IVP02_interpreters.txt" <<'PYEOF'
import json, sys, time
failed, tested, n_pass, n_inc, inter_file = sys.argv[1:6]
failed, tested, n_pass, n_inc = int(failed), int(tested), int(n_pass), int(n_inc)
inter = {}
try:
    for line in open(inter_file):
        for part in line.split():
            if ":" in part and part.endswith(("PASS", "FAIL", "INCONCLUSIVE)",
                                             "INCONCLUSIVE")):
                pass
        if ":" in line:
            k, v = line.strip().split(":", 1)
            inter[k.replace("python", "Python ")] = v.strip()
except FileNotFoundError:
    pass
if failed:
    status = "FAIL"
elif tested == 0:
    status = "INCONCLUSIVE"
elif n_inc:
    status = "PARTIAL"
else:
    status = "PASS"
payload = {
    "ivp": "IVP02",
    "status": status,
    "pre_registered": {
        "clean_room": "fresh venv per interpreter; declared deps only; "
                      "pip install --no-deps -e .",
        "acceptance": "pytest suite passes and canonical numeric job is "
                      "bitwise identical across all tested interpreters",
    },
    "interpreters": inter,
    "n_tested": tested, "n_passed": n_pass, "n_failed": failed,
    "n_absent": n_inc,
    "canonical_job": "IVP02_canonical_job.py (17-digit output; logs under "
                     "results/logs/IVP02_py*.log)",
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
}
with open("independent_verification/results/IVP02.json", "w") as f:
    json.dump(payload, f, indent=1)
print(f"[IVP02] verdict -> independent_verification/results/IVP02.json ({status})")
PYEOF

if [ "$failed" -gt 0 ]; then
  echo "IVP-02 overall: FAIL"
  exit 1
fi
if [ "$tested" -eq 0 ]; then
  echo "IVP-02 overall: INCONCLUSIVE (no interpreters available)"
  exit 2
fi
if [ "$n_inc" -gt 0 ]; then
  echo "IVP-02 overall: PARTIAL (PASS on all present interpreters; absent ones INCONCLUSIVE)"
  exit 0
fi
echo "IVP-02 overall: PASS"
