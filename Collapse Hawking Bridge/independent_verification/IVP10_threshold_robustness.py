#!/usr/bin/env python3
"""
IVP-10 — threshold robustness / perturbation test (falsification).

Uses the verifier's OWN blind A* from IVP-09 (results/IVP09.json — the
suite's own measurement, never a committed value).  For epsilon in
{1e-2, 1e-3, 1e-4, 1e-5}:

    A* (1 - eps)  must classify SUBcritical
    A* (1 + eps)  must classify SUPERcritical

at N = 800 (and, as a cross-check, N = 1600 for eps >= 1e-4).

Any violation would mean the threshold classification is an artifact of
a single numerical criterion.  Note the fixed-grid caveat: A* is a
fixed-grid quantity, so at coarser grids the closest perturbations may
legitimately flip; the test therefore runs at a resolution where the
ladder has converged (N >= 800).
"""
import json
import os
import sys

IVP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, IVP_DIR)
from ivp_common import classification, log, run_gaussian, save_result

EPS_LIST = [1e-2, 1e-3, 1e-4, 1e-5]


def main():
    log("=" * 72)
    log("IVP-10 — threshold robustness / perturbation test")
    log("=" * 72)

    ivp09_path = os.path.join(IVP_DIR, "results", "IVP09.json")
    if not os.path.exists(ivp09_path):
        log("IVP09 result not found — run IVP09_threshold_blind.py first")
        return 2
    with open(ivp09_path) as f:
        ivp09 = json.load(f)
    a_star_800 = ivp09["ladder"]["N800"]["a_star"]
    a_star_1600 = ivp09["ladder"]["N1600"]["a_star"]
    log(f"\nverifier-own blind A*: N800 = {a_star_800:.8f}, "
        f"N1600 = {a_star_1600:.8f}\n")

    rows = []
    ok_all = True
    log("[A] perturbation classification at N = 800")
    for eps in EPS_LIST:
        d_lo, _ = run_gaussian(a_star_800 * (1 - eps), 800)
        d_hi, _ = run_gaussian(a_star_800 * (1 + eps), 800)
        sub_ok = not classification(d_lo)
        sup_ok = classification(d_hi)
        ok = sub_ok and sup_ok
        ok_all &= ok
        rows.append({"eps": eps, "A_below": a_star_800 * (1 - eps),
                     "A_above": a_star_800 * (1 + eps),
                     "below_supercritical": classification(d_lo),
                     "above_supercritical": classification(d_hi),
                     "ok": ok})
        log(f"    eps = {eps:.0e}: A- = {a_star_800*(1-eps):.8f} -> "
            f"{'super (BAD)' if not sub_ok else 'sub'};  "
            f"A+ = {a_star_800*(1+eps):.8f} -> "
            f"{'super' if sup_ok else 'sub (BAD)'}  "
            f"[{'OK' if ok else 'VIOLATION'}]")

    log("\n[B] cross-check at N = 1600 (eps >= 1e-4)")
    for eps in (1e-3, 1e-4):
        d_lo, _ = run_gaussian(a_star_1600 * (1 - eps), 1600)
        d_hi, _ = run_gaussian(a_star_1600 * (1 + eps), 1600)
        sub_ok = not classification(d_lo)
        sup_ok = classification(d_hi)
        ok = sub_ok and sup_ok
        ok_all &= ok
        rows.append({"eps": eps, "grid": 1600,
                     "below_supercritical": classification(d_lo),
                     "above_supercritical": classification(d_hi), "ok": ok})
        log(f"    eps = {eps:.0e}: below -> "
            f"{'super (BAD)' if not sub_ok else 'sub'}, above -> "
            f"{'super' if sup_ok else 'sub (BAD)'}  "
            f"[{'OK' if ok else 'VIOLATION'}]")

    status = "PASS" if ok_all else "FAIL"
    log(f"\nIVP-10 overall: {status}")
    save_result("IVP10", {
        "status": status,
        "pre_registered": {
            "source_of_A_star": "verifier-own blind IVP-09 measurement",
            "criterion": "A*(1-eps) subcritical AND A*(1+eps) supercritical "
                         "for every pre-registered epsilon",
            "caveat": "fixed-grid A*: coarser grids may legitimately flip "
                      "the closest perturbations",
        },
        "rows": rows,
        "checks": {"all_perturbations_classified_correctly": ok_all},
    })
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
