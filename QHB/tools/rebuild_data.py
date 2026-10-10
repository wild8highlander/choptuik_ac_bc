#!/usr/bin/env python3
"""Determinism guard: rebuild all data tables and compare SHA-256 hashes.

Usage: python3 tools/rebuild_data.py
Writes data/rebuild_hashes.json; exits 2 on any byte drift.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def hashes() -> dict:
    out = {}
    for f in sorted(DATA.glob("*.json")):
        if f.name == "rebuild_hashes.json":
            continue
        out[f.name] = hashlib.sha256(f.read_bytes()).hexdigest()
    return out


def main() -> int:
    before = hashes()
    subprocess.run([sys.executable, str(ROOT / "tools" / "run_all.py")],
                   check=True, capture_output=True)
    after = hashes()
    drift = sorted(k for k in after if before.get(k) != after[k])
    print(f"tables: {len(after)}; byte drift: {len(drift)}")
    (DATA / "rebuild_hashes.json").write_text(json.dumps(
        {"n_tables": len(after), "n_drift": len(drift), "drift": drift,
         "deterministic": not drift, "hashes": after},
        indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if not drift else 2


if __name__ == "__main__":
    sys.exit(main())
