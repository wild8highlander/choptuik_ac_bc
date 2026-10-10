#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Iron-QA: master numbers of the QHB canon, checked against machine JSON layers.

Every assertion is a dotted-path lookup with an explicit tolerance, so a silent
regression in any layer fails the build instead of propagating into documents.
"""
import json, math, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
FAIL = []

def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def dig(d, path):
    cur = d
    for part in path.split("/"):
        if isinstance(cur, list):
            part = int(part)
        elif part not in cur:
            return KeyError(path)
        cur = cur[part]
    return cur

def chk(label, value, expected, tol=0.0, rel=0.0):
    ok = False
    try:
        if rel > 0:
            ok = abs(value - expected) <= rel * abs(expected)
        else:
            ok = abs(value - expected) <= tol
    except TypeError:
        ok = value == expected
    status = "PASS" if ok else "FAIL"
    if not ok:
        FAIL.append(f"{label}: got {value!r}, expected {expected!r} (tol={tol}, rel={rel})")
    print(f"  [{status}] {label}: {value!r}")

def near(label, value, expected, digits):
    chk(label, value, expected, tol=0.5 * 10 ** (-digits))

print("[check_numbers] canon v1.3.0 (via qhb.constants)")
sys.path.insert(0, str(ROOT))
import qhb.constants as K  # noqa: E402

def kget(name):
    return getattr(K, name)

canon = [
    ("BETA_STAR", 3.3583), ("DELTA_F_MIN", 0.181777),
    ("BETA_C_NAIVE", 2.9910), ("V_STAR", 0.9359375), ("ETA_CRIT", 0.0908885),
]
for name, exp in canon:
    try:
        near(f"qhb.constants.{name}", float(kget(name)), exp, 12)
    except AttributeError:
        FAIL.append(f"qhb.constants.{name}: attribute not found")

print("[check_numbers] extra layer (v2.0.0)")
ex = load("monolith/extra_research/extra_research_results.json")
chk("cross_version.max_abs_dev < 4.3e-5", dig(ex, "cross_version_summary/max_abs_dev") < 4.3e-5, True)
chk("cross_version.n_comparisons", dig(ex, "cross_version_summary/n_comparisons"), 13)
chk("symbolic.T14 present", str(dig(ex, "symbolic/T14_worst_drop_unit_profiles")) != "", True)

print("[check_numbers] roadmap layer (v2.1.0)")
rm = load("monolith/roadmap_research/roadmap_results.json")
chk("R1 order p ~ 0.99998", dig(rm, "r1_continuum/order_p_1024_65536"), 0.99998, tol=2e-5)
chk("R2 max_dev_branches < 5e-9", dig(rm, "r2_anisotropic/max_dev_branches") < 5e-9, True)
chk("R2 omega(gamma=1) = 3/(2pi)", dig(rm, "r2_anisotropic/omega_T16_rows/2/omega_pred"), 3 / (2 * math.pi), rel=1e-12)
chk("R3 T_death(1e12) = 0.00341392", dig(rm, "r3_thermal/T_death_N1e12"), 0.003413920073633568, tol=1e-9)
chk("R3 eta_crit(0) = 0.0908885", dig(rm, "r3_thermal/eta_crit_zero"), 0.0908885, tol=1e-12)

print("[check_numbers] analytic layer (v2.2.0)")
t19 = load("monolith/analytic_layer/v220_t19.json")
chk("T19 charpoly(C0) griddev = 0", dig(t19, "charpoly/C0_equals_target_griddev"), 0.0, tol=1e-15)
chk("T19 charpoly(J0) griddev = 0", dig(t19, "charpoly/J0_equals_target_griddev"), 0.0, tol=1e-15)
chk("T19 block decomposition griddev = 0",
    dig(t19, "theorem_T19/block_product_equals_charpoly_griddev"), 0.0, tol=1e-15)
chk("T19.split identity poly_zero", dig(t19, "corollary_C1_splitting/poly_identity_zero"), True)
co = load("monolith/analytic_layer/v220_cosmo.json")
rows = dig(co, "P_C1_deadline_law/rows")
r12 = next(r for r in rows if abs(r["N"] - 1e12) < 1)
chk("P-C1 t_death/t_c (alpha=1/2, N=1e12)", r12["alpha_half"], 672.8407033755242, rel=1e-12)
chk("P-C1 T_death(N=1e12)", r12["T_death"], 0.003413920073633568, rel=1e-12)
chk("P-C3 t_lim(T_c) = 4.0369875e-11", float(dig(co, "P_C3_dynamic_deadline/t_lim_at_Tc")),
    4.0369875e-11, rel=1e-9)
la = load("monolith/analytic_layer/v220_ladders.json")
lb = dig(la, "L_B_step_ladder/rows/0")
chk("L-B omega_exact = 3/(2pi)", lb["omega_exact"], 3 / (2 * math.pi), rel=1e-12)
chk("L-B order ~ 4.0956", float(lb["order_fit"]), 4.0956, tol=5e-4)
chk("L-B richardson dev < 2.5e-11", float(lb["richardson_dev"]) < 2.5e-11, True)
last = lb["rows"][-1]
chk("L-B finest-step err < 4e-10", last["err"] < 4e-10, True)

print(f"[check_numbers] {len(FAIL)} failures")
for f in FAIL:
    print("  FAIL:", f)
return_code = 1 if FAIL else 0
if __name__ == "__main__":
    sys.exit(return_code)
