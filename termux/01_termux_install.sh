#!/usr/bin/env bash
# ============================================================================
# 01_termux_install.sh — one-shot Termux environment setup for einstein_direct
# Repository: https://github.com/wild8highlander/choptuik_ac_bc
#
# Installs: python, git, build tools, numpy/scipy (pkg wheels when needed),
#           sympy, pytest.
# Safe to re-run (idempotent).
# ============================================================================
set -u
step() { printf "==> %s\n" "$*"; }
ok()   { printf "  [OK] %s\n" "$*"; }
err()  { printf "  [ERROR] %s\n" "$*"; }

step "Updating Termux packages"
pkg update -y && pkg upgrade -y || err "pkg update failed (check network)"

step "Installing base packages"
pkg install -y python git clang libjpeg-turbo libandroid-execinfo || true
pkg install -y python-numpy python-scipy || true   # Termux science wheels (fast path)

step "Installing Python dependencies"
# numpy/scipy: prefer pkg wheels; fall back to pip only if missing
python3 - <<'EOF' || pip install --no-cache-dir numpy scipy
import numpy, scipy
EOF
pip install --no-cache-dir sympy pytest mpmath || err "pip install failed"

step "Verifying the stack"
python3 -c "import numpy, scipy, sympy, pytest, mpmath; print('numpy', numpy.__version__); print('scipy', scipy.__version__); print('sympy', sympy.__version__)" \
  && ok "python stack ready" || err "python stack incomplete"

ok "Done. Next: bash 02_termux_run.sh"
