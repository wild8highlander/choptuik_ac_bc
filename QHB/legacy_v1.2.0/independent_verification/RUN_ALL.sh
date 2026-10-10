#!/usr/bin/env bash
# IVP-11 — run the whole audit
set -e
cd "$(dirname "$0")"
for i in 01 02 03 04 05 06 07 08 09 10 11; do
    python3 IVP${i}_*.py
done
python3 summarize.py
