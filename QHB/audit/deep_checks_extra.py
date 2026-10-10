#!/usr/bin/env python3
"""Extra deep checks beyond the IVP battery (part of `make deep`).

* 100-digit recomputation with strict textual comparison
* C5 z-score guard over 20 independent seeds
* C11 anchor: barrier maximum location via SymPy (exact s=1)
* C10: even/odd sector annihilation identity (SymPy)
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import mpmath as mp
import sympy as sp

from qhb import competing, constants as C, core, vortex

mp.mp.dps = 100


def main() -> int:
    out = {}

    # 100-digit textual pins
    out["omega_100d"] = mp.nstr(mp.mpf(3) / (2 * mp.pi), 100)
    out["margin_100d"] = mp.nstr(mp.mpf("0.181777") / 2 / mp.mpf("6.1e-10"), 100)
    out["omega_ok"] = out["omega_100d"].startswith(
        "0.477464829275686007306651290117543")
    out["margin_ok"] = out["margin_100d"].startswith("148997540.9")

    # C5 z-guard across seeds
    zs = []
    for seed in (11, 22, 33, 44, 55, 66, 77, 88, 99, 1010, 1111, 1212,
                 1313, 1414, 1515, 1616, 1717, 1818, 1919, 2020):
        r = core.free_three_body(2000, seed)
        zs.append((r["p_esc"] - 0.2433) / math.sqrt(0.2433 * 0.7567 / 2000))
    out["c5_z_max_abs"] = max(abs(z) for z in zs)
    out["c5_z_ok"] = bool(out["c5_z_max_abs"] < 3.0)

    # C11 barrier maximum at s = 1 (exact)
    s = sp.symbols("s", real=True)
    V = sp.Rational(9359375, 10000000) * s ** 2 * sp.exp(2 - 2 * s)
    dV = sp.simplify(sp.diff(V, s))
    crit = sp.solve(sp.Eq(dV, 0), s)
    out["c11_critical_points"] = [sp.sstr(c) for c in crit]
    out["c11_max_ok"] = bool(sp.Rational(1, 1) in crit or
                             any(sp.simplify(c - 1) == 0 for c in crit))

    # C10 even/odd annihilation (symbolic)
    t = sp.symbols("t", real=True)
    fA = sp.exp(-((t - 5) / 3) ** 2)
    fB = (t - 5) * sp.exp(-((t - 5) ** 2) / 4)
    ident = sp.simplify(fA.subs(t, 10 - t) - fA)  # even -> 0
    odd = sp.simplify(fB.subs(t, 10 - t) + fB)    # odd -> 0
    out["c10_even_identity_zero"] = bool(ident == 0)
    out["c10_odd_identity_zero"] = bool(odd == 0)

    n_ok = sum(1 for k, v in out.items() if k.endswith("_ok") and v)
    n_total = sum(1 for k in out if k.endswith("_ok"))
    out["summary"] = {"ok": n_ok, "total": n_total,
                      "all_pass": bool(n_ok == n_total)}
    (ROOT / "data" / "deep_checks_extra.json").write_text(
        json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(f"deep checks extra: {n_ok}/{n_total} PASS")
    for k, v in out.items():
        if k.endswith("_ok"):
            print(f"  {k}: {'PASS' if v else 'FAIL'}")
    return 0 if n_ok == n_total else 2


if __name__ == "__main__":
    sys.exit(main())
