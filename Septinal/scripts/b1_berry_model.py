#!/usr/bin/env python3
"""Septinal · b1_berry_model.py — the symbolic twin of Satellite.B1_BerryShift.

The Lean module proves, for the canonical two-level normal form with
quadrature coupling delta/sqrt(2) and unit level separation:

    lambda_lower(delta) = (1 - sqrt(1 + 2 delta^2)) / 2
                        = -delta^2/2 + R(delta),   0 < R(delta) <= delta^4/4.

This twin recomputes the statement symbolically (SymPy exact series) and
numerically (mpmath, 50 digits), writes ``data/berry_series.csv`` and
prints the audit line quoted in the Lean docstring:

    -delta^2/2 + delta^4/4 - delta^6/4 + 5 delta^8/16 - ...

Usage::

    python scripts/b1_berry_model.py            # full audit + CSV
"""

from __future__ import annotations

import csv
from pathlib import Path

import mpmath as mp
import sympy as sp

SEED = 1993
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data"


def main() -> None:
    mp.mp.dps = 50
    delta = sp.symbols("delta", real=True)
    lam = (1 - sp.sqrt(1 + 2 * delta**2)) / 2

    series = sp.series(lam, delta, 0, 12).removeO().expand()
    print("[b1] exact series  :", series)
    coeffs = [sp.Rational(c) for c in
              (-sp.Rational(1, 2), sp.Rational(1, 4), -sp.Rational(1, 4),
               sp.Rational(5, 16), -sp.Rational(7, 16))]
    expansion = sum(c * delta ** (2 * (i + 1)) for i, c in enumerate(coeffs))
    assert sp.simplify(series - expansion) == 0, "series mismatch"
    print("[b1] docstring form: -delta^2/2 + delta^4/4 - delta^6/4 + 5*delta^8/16 - ...  OK")

    lam_f = sp.lambdify(delta, lam, "mpmath")
    rows = []
    for i in range(1, 41):
        d = mp.mpf(i) / 20  # delta in (0, 2], step 0.05
        val = lam_f(d)
        first = -d**2 / 2
        rem = val - first
        bound = d**4 / 4
        assert 0 < rem <= bound, f"remainder bound fails at delta={d}"
        rows.append({"delta": sp.Rational(i, 20), "lambda_lower_50d": mp.nstr(val, 20),
                     "first_order": mp.nstr(first, 20), "remainder_R": mp.nstr(rem, 20),
                     "bound_delta4_over_4": mp.nstr(bound, 20),
                     "remainder_over_bound": mp.nstr(rem / bound, 20)})
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "berry_series.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    d1 = mp.mpf(1) / 10
    print(f"[b1] spot check delta=0.1: lambda={mp.nstr(lam_f(d1), 15)}, "
          f"R={mp.nstr(lam_f(d1) + d1**2/2, 15)} <= delta^4/4 = {mp.nstr(d1**4/4, 15)}")
    print(f"[b1] 40 rows -> data/berry_series.csv  (seed {SEED})  ALL BOUNDS PASS")


if __name__ == "__main__":
    main()
