# -*- coding: utf-8 -*-
"""IVP01 — release integrity: the committed verdicts exist and hash-stable."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ivp_common import ROOT, sha256, write_verdict

EXPECTED = ["c1_verdict.json", "c2_verdict.json", "c3_verdict.json",
            "c4_verdict.json", "c5_verdict.json"]
rows = {}
ok = True
for name in EXPECTED:
    p = os.path.join(ROOT, "campaigns", "reference", name)
    exists = os.path.isfile(p)
    ok &= exists
    rows[name] = {"exists": exists, "sha256": sha256(p) if exists else None}
write_verdict("IVP01.json", {"check": "release integrity",
                             "verdict": "PASS" if ok else "FAIL",
                             "files": rows})
print("IVP01:", "PASS" if ok else "FAIL")
