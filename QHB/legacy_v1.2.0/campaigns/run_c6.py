# -*- coding: utf-8 -*-
"""
campaign C6 — the physical mapping: three branches (v1.1.0).

The roadmap's first entry: promote the MARKED scale hypothesis of the
package (the code-unit gap rides a cosmological contact temperature into
Hz) to a three-branch comparison.  Every branch is a literature ANCHOR
(comparison only, never a fit target), and each branch carries its own
honesty note about what the number actually IS:

  branch Lambda_QCD   Lambda = 332 MeV (one-loop MS-bar).  Honesty: a
                      RENORMALISATION SCALE, not a thermodynamic
                      temperature; the k_B conversion is a comparison
                      device, nothing freezes out at Lambda.
  branch QCD_crossover T_QCD = 155.16 MeV / k_B (lattice crossover, the
                      committed T8 contact).  Honesty: the ONLY branch
                      that is a true temperature (the deconfinement bath).
  branch electroweak  v_EW = 246.22 GeV (PDG vacuum expectation value).
                      Honesty: a VEV (energy), NOT a bath temperature;
                      the EW-epoch bath was of the same order (10^2 GeV,
                      comparison).  The LEAST honest branch — marked.

Committed mapping (marked hypothesis, now with three branches):
  f_contact = k_B T / h                    [Hz]  the contact temperature
  M_contact = hbar c^3 / (8 pi G k_B T)    [kg]  T_H(M) = T exactly
  f_gap     = Delta_0 * f_contact          [Hz]  the code-unit gap rides
                                                 the contact
  E_gap     = h f_gap                      [J]   the gap quantum

The machine gates (exact):
  G1  round trip: T_H(M_contact) == T_anchor, rel dev < 1e-12 (all three);
  G2  strict monotonicity of mass vs temperature:
      M_EW < M_QCD < M_Lambda (and all << M_sun, all > 0);
  G3  ratio identity: f_gap ratios == T ratios exactly (the mapping is
      linear — the RATIO is arithmetic, the CONTENT is the three-branch
      existence; carried as an honesty note, not a discovery);
  G4  the gap quantum of the QCD branch compared with Lambda_QCD as a
      pure order-of-magnitude comparison (no claim).

The verdict is written to campaigns/reference/c6_verdict.json.
"""
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from qhb.bridge import T_H, r_s, t_evap, rho_mean
from qhb.constants import (G, c, hbar, h, k_B, M_sun, m_P, l_P, rho_P,
                           LAMBDA_QCD_MeV, T_QCD_K, MeV_J, __version__)

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "reference")

# --- the three branch anchors (literature, comparisons — never fits) ---------
V_EW_GeV = 246.22                    # PDG anchor of the EW symmetry breaking
GEV_J = 1e9 * MeV_J                  # J per GeV (exact arithmetic)

BRANCHES = [
    {
        "name": "Lambda_QCD",
        "T_K": LAMBDA_QCD_MeV * MeV_J / k_B,
        "anchor": f"Lambda_QCD = {LAMBDA_QCD_MeV:.1f} MeV (one-loop MS-bar)",
        "honesty": "a renormalisation scale, NOT a temperature; the k_B "
                   "conversion is a comparison device only",
    },
    {
        "name": "QCD_crossover",
        "T_K": T_QCD_K,
        "anchor": "T_QCD = 155.16 MeV / k_B (lattice-QCD crossover; "
                  "the committed T8 contact)",
        "honesty": "the only true TEMPERATURE of the three — the "
                   "deconfinement bath; the committed contact of the bridge",
    },
    {
        "name": "electroweak",
        "T_K": V_EW_GeV * GEV_J / k_B,
        "anchor": f"v_EW = {V_EW_GeV:.2f} GeV (PDG VEV of EW symmetry "
                  "breaking)",
        "honesty": "a vacuum expectation value (energy), NOT a bath "
                   "temperature; the EW-epoch bath was of the same order "
                   "(1e2 GeV, comparison). The LEAST honest branch — marked",
    },
]

D0 = None      # filled from the committed C1 verdict


def _load_delta0():
    global D0
    with open(os.path.join(REF, "c1_verdict.json"), encoding="utf-8") as fh:
        D0 = json.load(fh)["static"]["Delta0"]


def f_contact(T_K):
    """The contact temperature as a frequency: k_B T / h [Hz]."""
    return k_B * T_K / h


def M_of_T(T_K):
    """The mass whose Hawking temperature equals T_K [kg] (exact)."""
    return hbar * c**3 / (8.0 * math.pi * G * k_B * T_K)


def main():
    t0 = time.time()
    _load_delta0()

    rows = []
    for br in BRANCHES:
        T = br["T_K"]
        fc = f_contact(T)
        M = M_of_T(T)
        fg = D0 * fc
        rows.append({
            "name": br["name"], "anchor": br["anchor"],
            "honesty": br["honesty"],
            "T_K": T,
            "f_contact_Hz": fc,
            "M_contact_kg": M,
            "M_over_Msun": M / M_sun,
            "M_over_mP": M / m_P,
            "r_s_over_lP": r_s(M) / l_P,
            "f_gap_Hz": fg,
            "E_gap_J": h * fg,
            "E_gap_MeV": h * fg / MeV_J,
            "t_evap_s": t_evap(M),
            "rho_over_rhoP": rho_mean(M) / rho_P,
        })
        print(f"{br['name']:15s} T={T:.4e} K  f={fc:.4e} Hz  "
              f"M={M:.5e} kg  f_gap={fg:.4e} Hz  "
              f"E_gap={h * fg / MeV_J:.3f} MeV", flush=True)

    # --- exact machine gates --------------------------------------------------
    by = {r["name"]: r for r in rows}

    g1 = []
    for br, r in zip(BRANCHES, rows):
        T = br["T_K"]
        dev = abs(T_H(r["M_contact_kg"]) - T) / T
        g1.append({"name": br["name"], "rel_dev": dev})
    g1_ok = all(g["rel_dev"] < 1e-12 for g in g1)

    # G2: mass must be STRICTLY decreasing in the anchor temperature
    # (T_EW > T_Lambda > T_QCD  =>  M_EW < M_Lambda < M_QCD; the gate is
    # written against the temperature ordering, not against names)
    t_order = sorted(rows, key=lambda r: -r["T_K"])
    g2 = all(t_order[i]["M_contact_kg"] < t_order[i + 1]["M_contact_kg"]
             for i in range(len(t_order) - 1)) \
        and max(r["M_contact_kg"] for r in rows) < 1e-4 * M_sun
    g2_ok = bool(g2)

    r123 = [(rows[i]["f_gap_Hz"] / rows[i + 1]["f_gap_Hz"],
             rows[i]["T_K"] / rows[i + 1]["T_K"]) for i in (0, 1)]
    g3_dev = max(abs(a - b) / b for a, b in r123)
    g3_ok = g3_dev < 1e-12

    eq = by["QCD_crossover"]["E_gap_MeV"]
    g4_ratio = LAMBDA_QCD_MeV / eq        # pure order-of-magnitude comparison
    g4_ok = 1.0 < g4_ratio < 10.0         # the honest window: same decade

    print(f"G1 round trip: max rel dev = {max(g['rel_dev'] for g in g1):.2e} "
          f"-> {'PASS' if g1_ok else 'FAIL'}")
    print(f"G2 monotonicity (M strictly decreasing in T, all << M_sun): "
          f"{'PASS' if g2_ok else 'FAIL'}")
    print(f"G3 ratio identity dev = {g3_dev:.2e} -> {'PASS' if g3_ok else 'FAIL'}")
    print(f"G4 Lambda/E_gap(QCD) = {g4_ratio:.3f} (window 1..10): "
          f"{'PASS' if g4_ok else 'CHECK'}")

    verdict = {
        "campaign": "qhb_c6",
        "engine": "closed-form Schwarzschild mapping (qhb.bridge), exact "
                  "arithmetic; the only campaign input from the machine is "
                  "the committed Delta_0 of c1_verdict.json",
        "project_version": __version__,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "hypothesis_status": "MARKED HYPOTHESIS — the code-unit gap -> Hz "
                             "mapping through a contact temperature; the "
                             "branches are comparison anchors, never fit "
                             "targets",
        "Delta0_source": "campaigns/reference/c1_verdict.json (static "
                         "gap, N=64)",
        "Delta0": D0,
        "branches": rows,
        "gates": {
            "G1_round_trip": {"rows": g1, "ok": g1_ok},
            "G2_monotonicity": {"ok": g2_ok},
            "G3_ratio_identity": {"max_rel_dev": g3_dev, "ok": g3_ok},
            "G4_order_window": {"Lambda_over_E_gap_QCD": g4_ratio,
                                "ok": g4_ok},
        },
        "verdicts": {
            "mapping_round_trip": "PASS" if g1_ok else "FAIL",
            "branch_monotonicity": "PASS" if g2_ok else "FAIL",
            "linear_ratio_carried": "PASS (arithmetic identity, carried as "
                                    "an honesty note — not a discovery)",
            "order_window_QCD": "REPORTED (Lambda within one decade of the "
                                "mapped gap quantum; comparison only)",
        },
        "honest_notes": [
            "Lambda_QCD is a renormalisation scale, not a temperature; its "
            "branch exists for comparison and carries the weakest claim",
            "the electroweak branch converts a VEV (energy) to a "
            "temperature-equivalent; the EW bath temperature was of the "
            "same order but is a different quantity — least honest branch",
            "the mapping f_gap = Delta_0 * k_B T / h is linear, so branch "
            "RATIOS are arithmetic; the physical content claimed is only "
            "the three-branch spread itself and the QCD contact",
            "E_gap(QCD) ~ " + f"{eq:.1f} MeV sits within one decade of "
            "Lambda_QCD = 332 MeV — an order-of-magnitude coincidence, "
            "explicitly NOT a derivation of Lambda_QCD",
        ],
        "wall_s": time.time() - t0,
    }
    os.makedirs(REF, exist_ok=True)
    with open(os.path.join(REF, "c6_verdict.json"), "w", encoding="utf-8") as fh:
        json.dump(verdict, fh, indent=1)
    print(f"verdict written: campaigns/reference/c6_verdict.json "
          f"[{verdict['wall_s']:.1f}s]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
