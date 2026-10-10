# -*- coding: utf-8 -*-
"""IVP08 — seed determinism: the MC cell is bit-identical across runs."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ivp_common import ROOT, write_verdict
sys.path.insert(0, ROOT)
import numpy as np
from engine.solver import wu_mc

r1 = wu_mc(0.5, 1.0, n_real=50_000)
r2 = wu_mc(0.5, 1.0, n_real=50_000)
ok = r1[0] == r2[0] and r1[2] == r2[2]
write_verdict("IVP08.json", {"check": "seed determinism",
                             "verdict": "PASS" if ok else "FAIL",
                             "r_mc_run1": r1[0], "r_mc_run2": r2[0],
                             "seed": 20261010})
print("IVP08:", "PASS" if ok else "FAIL")
