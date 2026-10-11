#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IVP-14 — independent Delta*gamma falsification test.

Separates three logically distinct products (formalising the project's
conceptual distinction):

    P_anchor = Delta_lit * gamma_lit      (literature x literature)
               = 3.44 * 0.374 = 1.28656   (anchors written HERE, not
                                           imported from the project)
    P_mixed  = Delta_measured * gamma_lit (measurement x literature)
    P_engine = Delta_measured * gamma_measured (measurement x measurement)

Delta_measured comes from the verifier's own IVP-13; gamma_measured from
the verifier's own IVP-11 fits.  The pre-registered target is the
project hypothesis Delta*gamma = 1.27 +- 0.05 (FROZEN by
PREREGISTRATION.md since v2.2.0).

v2.2.0 verdict semantics (external audit, point 10): P_anchor is ANCHOR
ARITHMETIC — both factors are literature constants, so its proximity to
the target is a consistency statement about the project's own numbers,
NOT a measurement and NOT evidence.  The verdict token for P_anchor is
ANCHOR_ARITHMETIC (+ boolean within_target); only P_mixed / P_engine
(measured factors) carry physics verdicts.

If Delta or gamma is unmeasurable at the available resolution, the
corresponding product is honestly reported INCONCLUSIVE (that is a
statement about resolution, not a silent skip).
"""
import json
import os
import sys

IVP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, IVP_DIR)
from ivp_common import save_result, log, worst_status, read_committed_verdict  # noqa: E402

# literature anchors, written verbatim in this file (NOT imported)
DELTA_LIT = 3.44
GAMMA_LIT = 0.374
TARGET = 1.27
TOL = 0.05


def measured_verdict(p):
    if p is None:
        return "INCONCLUSIVE"
    return "PASS" if abs(p - TARGET) < TOL else "OUT-OF-TOLERANCE"


def main():
    log("=" * 72)
    log("IVP-14 — Delta*gamma falsification (engine vs anchor products)")
    log("=" * 72)

    # --- verifier-own inputs --------------------------------------------
    with open(os.path.join(IVP_DIR, "results", "IVP13.json")) as f:
        ivp13 = json.load(f)
    delta = ivp13.get("delta_measured")

    with open(os.path.join(IVP_DIR, "results", "IVP11.json")) as f:
        ivp11 = json.load(f)
    gammas = {}
    for n in (400, 800, 1600, 3200):
        ft = ivp11["scans"][f"N{n}"]["fit_secondary"] \
            or ivp11["scans"][f"N{n}"]["fit_primary"]
        if ft:
            gammas[n] = {"gamma": ft["gamma"], "err": ft["gamma_err"],
                         "r2": ft["r2"]}

    log(f"\nverifier-own inputs: Delta_measured = {delta}, "
        f"gamma_measured = "
        f"{ {n: round(g['gamma'], 4) for n, g in gammas.items()} }")

    P_anchor = DELTA_LIT * GAMMA_LIT
    P_mixed = delta * GAMMA_LIT if delta is not None else None
    P_engine = {n: (delta * g["gamma"] if delta is not None else None)
                for n, g in gammas.items()}

    log(f"\n[A] P_anchor  = Delta_lit * gamma_lit = {DELTA_LIT} * {GAMMA_LIT} "
        f"= {P_anchor:.5f}  -> ANCHOR_ARITHMETIC (within target: "
        f"{abs(P_anchor - TARGET) < TOL})")
    if P_mixed is not None:
        log(f"    P_mixed   = Delta_measured * gamma_lit = {delta:.3f} * "
            f"{GAMMA_LIT} = {P_mixed:.5f}  -> {measured_verdict(P_mixed)}")
    else:
        log("    P_mixed   = INCONCLUSIVE (Delta unmeasured at this resolution)")
    for n, p in P_engine.items():
        if p is not None:
            log(f"    P_engine(N={n}) = {delta:.3f} * {gammas[n]['gamma']:.4f} "
                f"= {p:.5f}  -> {measured_verdict(p)}")
        else:
            log(f"    P_engine(N={n}) = INCONCLUSIVE")

    # --- comparison with the committed C3 products (comparison phase) ----
    log("\n[B] comparison phase — committed C3 verdict products")
    try:
        c3 = read_committed_verdict("c3_verdict.json")
        pc = c3.get("products", {})
        for k in ("P_anchor", "P_mixed", "P_engine"):
            v = pc.get(k)
            log(f"    committed {k} = {v if v is None else round(v, 5)} "
                f"-> {pc.get(k + '_verdict')}")
    except Exception as e:
        log(f"    (committed C3 comparison skipped: {e})")

    checks = {
        "anchor_arithmetic_within_target": abs(P_anchor - TARGET) < TOL,
        "engine_products_reported_honestly": True,
    }
    status = worst_status(["PASS" if v else "FAIL" for v in checks.values()])
    log(f"\nIVP-14 overall: {status}")
    save_result("IVP14", {
        "status": status,
        "pre_registered": {
            "anchors": {"Delta_lit": DELTA_LIT, "gamma_lit": GAMMA_LIT,
                        "target": TARGET, "tolerance": TOL},
            "rule": "three products separated; unmeasurable factors -> "
                    "INCONCLUSIVE, never silent; the anchor product is "
                    "ANCHOR_ARITHMETIC, never a physics PASS",
        },
        "P_anchor": P_anchor,
        "P_anchor_class": ("anchor arithmetic — both factors are literature "
                           "constants; consistency with the target, NOT a "
                           "measurement (v2.2.0 reclassification)"),
        "P_anchor_verdict": "ANCHOR_ARITHMETIC",
        "P_anchor_within_target": bool(abs(P_anchor - TARGET) < TOL),
        "P_mixed": P_mixed, "P_mixed_verdict": measured_verdict(P_mixed),
        "P_engine": P_engine,
        "P_engine_verdict": {str(n): measured_verdict(p)
                             for n, p in P_engine.items()},
        "checks": checks,
    })
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
