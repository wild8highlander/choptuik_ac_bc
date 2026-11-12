#!/bin/bash
# Iteratively build missing olean modules until Stage4d's own errors appear
export ELAN_HOME=/home/z/my-project/.elan
export PATH="$ELAN_HOME/bin:$PATH"
L=/home/z/my-project/leanwork/choptuik_ac_bc/formal_choptuik/Septinal/lean
cd "$L" || exit 1

for i in $(seq 1 40); do
  # free transient space
  find .lake/packages -name "*.ilean" -delete 2>/dev/null
  find .lake/packages -type d -name ir -exec rm -rf {} + 2>/dev/null
  find .lake/build -name "*.ilean" -delete 2>/dev/null
  find .lake/build -type d -name ir -exec rm -rf {} + 2>/dev/null

  OUT=$(timeout 300 lake env lean SeptinalYM/Stage4d.lean 2>&1)
  MISS=$(echo "$OUT" | grep -o "object file '[^']*' of module [A-Za-z0-9_.]*" | head -1 \
         | sed "s/object file '//; s/' of module /:/")
  if [ -z "$MISS" ]; then
    echo "=== CYCLE $i: no missing imports; showing real errors ==="
    echo "$OUT" | grep "error:" | head -30
    echo "=== REALERRCOUNT $(echo "$OUT" | grep -c 'error:') ==="
    exit 0
  fi
  MOD="${MISS#*:}"
  echo "=== CYCLE $i: building missing module $MOD ==="
  timeout 400 lake build "$MOD" 2>&1 | tail -2
  df -h / | tail -1
done
echo "=== gave up after 40 cycles ==="
