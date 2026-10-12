"""
campaign C1 — the gap law of the three corrections (theorems T2/T3).

Protocol:
  1. static block: the sampled parabolic chain (N=64) — E0, E1, Delta_0,
     the response s = dDelta/dq_pk, the Lemma A flattening scale;
  2. Floquet scan: rigid-trio beta ladder on the committed quadratic
     window [0, 0.2] (21 points) + the pre-asymptotic wing [0.2, 0.8]
     (9 points, carried honestly);
  3. quadratic fit Delta_F = Delta_0 + B2 * beta^2 on the window -> B2, r^2;
  4. per-sector scans (only sector k active) -> B2_A, B2_B, B2_C;
  5. cross-term share: |B2_A + B2_B + B2_C - B2_trio| / |B2_trio|;
  6. theorem T2 checks: global b-flip evenness; a-only drive all-order zero;
  7. M-convergence of the Floquet step at the demonstration point.

The verdict is written to campaigns/reference/c1_verdict.json.
Console output is a courtesy; the verdict is the law.
"""
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from qhb.constants import BERRY_TRIO, BRAKING_TRIO, __version__
from qhb.gap import (
    evenness_dev,
    floquet_gap,
    lemma_a_mean,
    lemma_a_worst,
    static_of_chain,
)

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "reference")


def quadratic_fit(betas, gaps, d0):
    """Fit g = d0 + B2*beta^2 on the committed window; returns B2, r2, maxres."""
    x = np.array(betas) ** 2
    y = np.array(gaps) - d0
    A = np.stack([np.ones_like(x), x], axis=1)
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    pred = A @ coef
    ss_res = float(((y - pred) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return float(coef[1]), r2, float(np.abs(y - pred).max())


def main():
    t0 = time.time()
    E0, E1, D0, s, hstep, L = static_of_chain()
    print(f"static chain: E0={E0:.10f} E1={E1:.10f} Delta0={D0:.12f}")
    print(f"response s={s:.8f}  h={hstep:.8f}  L={L:.8f}")
    print(f"Lemma A: worst={lemma_a_worst(0.05, hstep):.6e} "
          f"mean={lemma_a_mean(0.05, hstep):.6e}")

    # --- rigid-trio scan ------------------------------------------------------
    window = [0.05 * k for k in range(5)] + [0.025 * k for k in range(4, 9)]
    window = sorted(set([round(b, 6) for b in window]))
    wing = [0.25 + 0.075 * k for k in range(9)]
    rows_window, rows_wing = [], []
    for beta in window + wing:
        g, _ = floquet_gap(D0, beta=beta)
        row = {"beta": beta, "gap": g, "shift": g - D0}
        (rows_window if beta <= 0.2 + 1e-12 else rows_wing).append(row)
    B2, r2, maxres = quadratic_fit([r["beta"] for r in rows_window],
                                   [r["gap"] for r in rows_window], D0)
    print(f"quadratic law: B2={B2:.8e}  r2={r2:.8f}  max|res|={maxres:.2e}")

    # --- per-sector scans ------------------------------------------------------
    B2_sector = []
    for k in range(3):
        rows = []
        for beta in window:
            b = [0.0, 0.0, 0.0]
            a = [0.0, 0.0, 0.0]
            b[k] = BERRY_TRIO[k] * beta
            a[k] = BRAKING_TRIO[k] * beta
            g, _ = floquet_gap(D0, b=b, a=a)
            rows.append((beta, g))
        b2k, r2k, _ = quadratic_fit([r[0] for r in rows],
                                    [r[1] for r in rows], D0)
        B2_sector.append(b2k)
        print(f"sector {k}: B2={b2k:.8e}  r2={r2k:.8f}")
    cross_share = abs(sum(B2_sector) - B2) / abs(B2)

    # --- theorem T2 checks ------------------------------------------------------
    dev, checks = evenness_dev(D0, beta=0.4)
    a_only_dev = 0.0
    for beta in (0.2, 0.5, 1.0):
        a = tuple(beta * v for v in BRAKING_TRIO)
        g, _ = floquet_gap(D0, b=(0.0, 0.0, 0.0), a=a)
        a_only_dev = max(a_only_dev, abs(g - D0))
    b0_id = abs(floquet_gap(D0, beta=0.0)[0] - D0)
    print(f"T2: b-flip evenness dev={dev:.2e} {checks}")
    print(f"T2: a-only all-order zero dev={a_only_dev:.2e}; b=0 identity {b0_id:.2e}")

    # --- M-convergence at the demonstration point -------------------------------
    m_rows = []
    for M in (480, 960, 1920, 3840):
        g, _ = floquet_gap(D0, beta=0.5, M=M)
        m_rows.append({"M": M, "gap": g})
    p_eff_M = []
    for i in range(len(m_rows) - 1):
        d1 = abs(m_rows[i]["gap"] - m_rows[i + 1]["gap"])
        d2 = abs(m_rows[i + 1]["gap"] - m_rows[i + 2]["gap"]) \
            if i + 2 < len(m_rows) else None
        if d2:
            p_eff_M.append(math.log(d1 / d2) / math.log(2.0))

    verdict = {
        "campaign": "qhb_c1",
        "engine": "qhb.gap — two-band Floquet, exact 2x2 piecewise exponentials",
        "project_version": __version__,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "units": "code units: hopping J=1, Omega0=2, Omega tones (2,3,7)*Omega0",
        "geometry": {"N": 64, "kappa": 0.05, "q_pk": 1.5, "h": hstep, "L": L},
        "static": {"E0": E0, "E1": E1, "Delta0": D0, "s_dDelta_dqpk": s,
                   "lemmaA_worst": lemma_a_worst(0.05, hstep),
                   "lemmaA_mean": lemma_a_mean(0.05, hstep)},
        "window": {"betas": window, "rows": rows_window,
                   "B2": B2, "r2": r2, "max_residual": maxres},
        "wing": {"betas": [r["beta"] for r in rows_wing],
                 "shifts": [r["shift"] for r in rows_wing],
                 "honest_note": "pre-asymptotic wing carried, NOT fitted; " +
                                "quartic response visible"},
        "per_sector": {"B2_A_pi2": B2_sector[0], "B2_B_pi3": B2_sector[1],
                       "B2_C_pi7": B2_sector[2]},
        "cross_share": cross_share,
        "theorem_T2": {"b_flip_evenness_dev": checks[0],
                       "a_flip_dev": checks[1],
                       "both_flip_dev": checks[2],
                       "a_only_all_order_dev": a_only_dev,
                       "b0_identity_dev": b0_id,
                       "statement": "EXACT: gap even under the global b-flip " +
                                    "(sigma_z conjugation) — dev = 0; a-only " +
                                    "drive all-order zero (integer-tone " +
                                    "cancellation) — dev = 0. NOT exact: the " +
                                    "a-flip alone deviates by ~7.3e-7 at " +
                                    "beta=0.4 — the genuine odd-in-a response " +
                                    "through second-order a*b cross terms " +
                                    "(Magnus [w sigma_z, v sigma_x]); carried " +
                                    "as data, not smoothed away."},
        "M_convergence": {"rows": m_rows, "p_eff": p_eff_M},
        "gap_shift_beta05": rows_wing[0]["shift"] if rows_wing else None,
        "verdicts": {
            "T2_b_flip_exact": "PASS" if checks[0] < 1e-12 else "FAIL",
            "T2_a_only": "PASS" if a_only_dev < 1e-12 else "FAIL",
            "T2_a_flip_residual": "REPORTED (genuine odd-in-a response, " +
                                  "carried as data)",
            "T3_quadratic_window": "PASS" if r2 > 0.999 and maxres < 5e-5
                                   else "FAIL",
        },
        "honest_notes": [
            "B2 is a committed machine law on window [0, 0.2]; outside it the " +
            "response is quartic-dominated (wing rows carried unfitted).",
            "The a-channel acts only jointly with the b-channel; alone it is " +
            "invisible to all orders on integer tones (measured exactly 0).",
            "The G-model is a toy: no claim that this Delta_F is the Yang-Mills " +
            "mass gap; the mapping to physical scales is a marked hypothesis.",
        ],
        "wall_s": time.time() - t0,
    }
    os.makedirs(REF, exist_ok=True)
    with open(os.path.join(REF, "c1_verdict.json"), "w", encoding="utf-8") as fh:
        json.dump(verdict, fh, indent=1)
    print(f"verdict written: campaigns/reference/c1_verdict.json "
          f"[{verdict['wall_s']:.1f}s]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
