#!/bin/bash
# Reinstall Lean toolchain + Mathlib cache (survives sandbox recycle: lives under my-project)
set -x
export ELAN_HOME=/home/z/my-project/.elan
export PATH="$ELAN_HOME/bin:$PATH"
mkdir -p "$ELAN_HOME"

cd /tmp
curl -sSfL -o elan-init.sh https://elan.lean-lang.org/elan-init.sh || exit 1
sh elan-init.sh -y --default-toolchain leanprover/lean4:v4.21.0 2>&1 | tail -5

LEANROOT=/home/z/my-project/leanwork/choptuik_ac_bc/formal_choptuik/Septinal/lean
cd "$LEANROOT" || exit 1

lake exe cache get! 2>&1 | tail -6
echo "=== BUILD Stage4d baseline ==="
lake build SeptinalYM.Stage4d 2>&1 | tail -8
echo "=== DONE rc=$? ==="
