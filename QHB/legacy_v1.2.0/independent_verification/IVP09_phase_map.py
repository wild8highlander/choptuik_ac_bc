# -*- coding: utf-8 -*-
"""IVP09 — the phase map gate: a fresh interpreter re-derives the
committed no-closure statement and the valley locus at the committed
geometry from scratch (own bisection, no campaign imports)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ivp_common import write_verdict, ROOT
sys.path.insert(0, ROOT)

import math
from qhb.gap import static_gap, floquet_gap, KAPPA

FLOOR = 2.0 / 64.0

# 1. recompute a fresh tranche of map cells (every second grid point)
cells = []
for qpk in (0.2, 0.4, 0.6, 0.8, 1.0):
    _, _, D0 = static_gap(64, KAPPA, qpk)
    for beta in (0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5):
        g, _ = floquet_gap(D0, beta)
        cells.append((qpk, beta, g))
fresh_min = min(g for _, _, g in cells)
ok_cells = all(g > FLOOR for _, _, g in cells)

# 2. independent bisection of the valley at q_pk = 0.4
_, _, D04 = static_gap(64, KAPPA, 0.4)
def g_of(b):
    return floquet_gap(D04, b)[0]
lo, hi = 2.9, 3.9                       # bracket from the committed map
for _ in range(40):
    m1 = lo + (hi - lo) / 3.0
    m2 = hi - (hi - lo) / 3.0
    if g_of(m1) <= g_of(m2):
        hi = m2
    else:
        lo = m1
b_star = 0.5 * (lo + hi)

import json
with open(os.path.join(ROOT, "campaigns", "reference", "c9_verdict.json"),
          encoding="utf-8") as fh:
    c9 = json.load(fh)
committed = next(v for v in c9["valley"] if abs(v["q_pk"] - 0.4) < 1e-9)
dev = abs(b_star - committed["beta_star"])
ok_valley = dev < 0.01 and committed["above_floor"]

ok = ok_cells and ok_valley
write_verdict("IVP09.json", {"check": "phase map gate (fresh cells + own "
                             "bisection)",
                             "verdict": "PASS" if ok else "FAIL",
                             "fresh_cells": len(cells),
                             "fresh_min_Delta_F": fresh_min,
                             "floor": FLOOR,
                             "valley_fresh_beta_star": b_star,
                             "valley_committed": committed["beta_star"],
                             "valley_dev": dev})
print("IVP09:", "PASS" if ok else "FAIL")
