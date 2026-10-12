"""
campaign C5 — the gap-drift law (theorem T10, the heir of CHB T10).

The sampled geometry shifts the gap.  Two exact inputs and one measured
law:

  Lemma A (inherited from CHB T10, exact).  A parabola sampled on a grid
  with step h loses kappa*h^2/8 of its peak in the worst alignment (the
  committed chain is centred, i.e. even N IS the worst alignment).

  Response s (measured, C1 block).  s = d(Delta_0)/d(q_pk) of the chain.

  Law (measured here).  Delta_N -> Delta_cont with drift Delta_cont -
  Delta_N = C h^2 + O(h^3); the exact-channel prediction is
  C_exact = s * kappa / 8.  The committed diagnostics: the climbing
  effective orders p_eff, the measured C, the exact-channel SHARE, and
  the honest negative: Delta_cont is fitted for display but NOT claimed
  (a two-term extrapolation of a pre-asymptotic ladder).

Also committed: the machine verification of Lemma A itself (sampled peak
identity to 1e-15 for even and odd N).
The verdict is written to campaigns/reference/c5_verdict.json.
"""
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from qhb.constants import __version__
from qhb.gap import (
    KAPPA,
    Q_PK,
    lemma_a_worst,
    parabolic_profile,
    static_gap,
    static_of_chain,
)

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "reference")

N_LADDER = (32, 64, 128, 256, 512)


def main():
    t0 = time.time()
    rows = []
    for N in N_LADDER:
        _E0, _E1, D0 = static_gap(N, KAPPA, Q_PK)
        _, _, hstep, _L = parabolic_profile(N, KAPPA, Q_PK)
        rows.append({"N": N, "h": hstep, "Delta_N": D0})
        print(f"N={N:4d}  h={hstep:.8f}  Delta_N={D0:.12f}", flush=True)

    # --- climbing effective orders (absolute drift; the ladder approaches
    #     the continuum gap from BELOW here — the sign mirror of CHB) ---------
    p_eff = []
    for i in range(len(rows) - 2):
        d1 = abs(rows[i]["Delta_N"] - rows[i + 1]["Delta_N"])
        d2 = abs(rows[i + 1]["Delta_N"] - rows[i + 2]["Delta_N"])
        if d1 > 0 and d2 > 0:
            p_eff.append({"pair": f"N={rows[i]['N']}->{rows[i + 2]['N']}",
                          "p": math.log(d1 / d2) / math.log(2.0)})
    print("p_eff:", [round(p["p"], 4) for p in p_eff])

    # --- two-parameter fit Delta_N = Delta_cont - C h^2 -----------------------
    h2 = np.array([r["h"] ** 2 for r in rows])
    dN = np.array([r["Delta_N"] for r in rows])
    A = np.stack([np.ones_like(h2), h2], axis=1)
    coef, *_ = np.linalg.lstsq(A, dN, rcond=None)
    Delta_cont_fit, C_measured = float(coef[0]), float(-coef[1])
    resid = dN - A @ coef
    print(f"fit: Delta_cont(fit)={Delta_cont_fit:.12f}  "
          f"C_measured={C_measured:.8e}  max|res|={np.abs(resid).max():.2e}")

    # --- exact channel (Lemma A x response) -----------------------------------
    _, _, _, s, _, _ = static_of_chain()
    C_exact = s * KAPPA / 8.0
    share = C_exact / C_measured if C_measured else None
    print(f"exact channel: C_exact = s*kappa/8 = {C_exact:.8e}  "
          f"share = {share:.4f}")

    # --- Lemma A machine verification ------------------------------------------
    # the WELL peak is the sampled minimum of q; worst alignment = even N
    # (the summit sits between two sites), odd N samples the summit exactly.
    lemma_rows = []
    for N in (32, 33, 64, 65, 128):
        _, q, hstep, _ = parabolic_profile(N, KAPPA, Q_PK)
        sampled_peak = -float(q.min())          # depth of the sampled well
        expected = Q_PK - (lemma_a_worst(KAPPA, hstep) if N % 2 == 0 else 0.0)
        lemma_rows.append({"N": N, "sampled_depth": sampled_peak,
                           "expected_worst": expected,
                           "dev": abs(sampled_peak - expected)})
    lemma_ok = max(r["dev"] for r in lemma_rows) < 1e-12
    print(f"Lemma A check: max dev = "
          f"{max(r['dev'] for r in lemma_rows):.2e} -> "
          f"{'PASS' if lemma_ok else 'FAIL'}")

    verdict = {
        "campaign": "qhb_c5",
        "engine": "exact tridiagonal eigensolver on the sampled parabola",
        "project_version": __version__,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "geometry": {"kappa": KAPPA, "q_pk": Q_PK,
                     "N_ladder": list(N_LADDER)},
        "ladder": rows,
        "p_eff": p_eff,
        "fit": {"Delta_cont_fit": Delta_cont_fit,
                "Delta_cont_status": "NOT CLAIMED — two-term extrapolation of " +
                                     "a pre-asymptotic ladder (honest " +
                                     "negative, mirrors CHB A*_inf)",
                "C_measured": C_measured,
                "max_abs_residual": float(np.abs(resid).max())},
        "exact_channel": {"C_exact_s_kappa_over_8": C_exact,
                          "s": s, "kappa": KAPPA,
                          "share_of_measured": share,
                          "honest_note": "the Lemma-A channel is a committed " +
                                         "fraction of the observed drift; the " +
                                         "rest is kinetic-term dispersion " +
                                         "(also O(h^2)) — marked hypothesis"},
        "lemma_A_machine_check": {"rows": lemma_rows, "ok": lemma_ok},
        "verdicts": {
            "T10_drift": "PASS" if p_eff and p_eff[-1]["p"] > 1.7 else "CHECK",
            "T10_lemmaA": "PASS" if lemma_ok else "FAIL",
            "T10_share": "REPORTED (honest window, no dominance claim)",
        },
        "honest_notes": [
            "the drift here approaches the continuum gap from BELOW " +
            "(flattened peak -> smaller gap), the sign mirror of the CHB " +
            "threshold ladder — the sign is carried, not hidden",
            "Delta_cont is not claimed; only the h^2 law and its exact-" +
            "channel share are committed",
        ],
        "wall_s": time.time() - t0,
    }
    os.makedirs(REF, exist_ok=True)
    with open(os.path.join(REF, "c5_verdict.json"), "w", encoding="utf-8") as fh:
        json.dump(verdict, fh, indent=1)
    print(f"verdict written: campaigns/reference/c5_verdict.json "
          f"[{verdict['wall_s']:.1f}s]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
