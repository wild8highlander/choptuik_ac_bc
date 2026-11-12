#!/bin/bash
# Iterate: free space, resume lake build SeptinalYM.Stage4d until success or real errors
export ELAN_HOME=/home/z/my-project/.elan
export PATH="$ELAN_HOME/bin:$PATH"
L=/home/z/my-project/leanwork/choptuik_ac_bc/formal_choptuik/Septinal/lean
LOG=/home/z/my-project/leanwork/logs/b_loop2.log
cd "$L" || exit 1

for i in $(seq 1 60); do
  find .lake/packages -name "*.ilean" -delete 2>/dev/null
  find .lake/packages -type d -name ir -exec rm -rf {} + 2>/dev/null
  find .lake/build -name "*.ilean" -delete 2>/dev/null
  find .lake/build -type d -name ir -exec rm -rf {} + 2>/dev/null

  echo "=== ITER $i $(df -h / | tail -1) ===" >> "$LOG"
  timeout 550 lake build SeptinalYM.Stage4d >> "$LOG" 2>&1
  RC=$?
  if grep -q "error: resource exhausted" "$LOG"; then
    echo "=== ITER $i: ENOSPC, retrying ===" >> "$LOG"
    continue
  fi
  if [ $RC -eq 124 ]; then
    echo "=== ITER $i: timeout, retrying ===" >> "$LOG"
    continue
  fi
  ERRS=$(grep -c "error:" "$LOG" 2>/dev/null)
  echo "=== FINAL rc=$RC errs=$ERRS ===" >> "$LOG"
  grep "error:" "$LOG" | head -25 >> "$LOG"
  exit 0
done
echo "=== 60 iters exhausted ===" >> "$LOG"
