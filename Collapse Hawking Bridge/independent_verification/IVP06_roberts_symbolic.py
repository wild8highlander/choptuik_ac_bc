#!/usr/bin/env python3
"""
IVP-06 — independent symbolic residual test of the Roberts-Oshiro
solution against the Einstein-scalar system solved by the engine.

The engine (engine/solver.py) solves, in double-null coordinates
ds^2 = -alpha^2 du dv + r^2 dOmega^2 (omega := ln alpha):

    (SC)  Phi_uv = -(r_u Phi_v + r_v Phi_u)/r
    (UV)  r_uv   = -(r_u r_v + alpha^2/4)/r
    (C1)  r_uu   = 2 omega_u r_u - (kappa/2) r Phi_u^2
    (C2)  r_vv   = 2 omega_v r_v - (kappa/2) r Phi_v^2
    (TH)  omega_uv = alpha^2 m / (2 r^3) - (kappa/2) Phi_u Phi_v
    (MD)  m      = (r/2)(1 + 4 r_u r_v / alpha^2)   [Misner-Sharp]

The verifier independently inserts the published Roberts-Oshiro exact
solution (alpha = 1, sigma in (0, 1/2)):

    r^2 = 1/4 [ (1 - 4 sigma^2) v^2 - 2 u v + u^2 ]
    Phi = 1/2 ln | (1 - 2 sigma - u/v) / (1 + 2 sigma - u/v) |

into all five equations + the mass definition, using SymPy DIFFERENTIATION
from scratch (nothing is imported from the engine).  All residuals are
reduced to sqrt-free rational form (multiplying by positive powers of
r^2) and must simplify to exactly ZERO.

Additionally, (C1) is checked with kappa as a FREE symbol: the residual
must factor as (kappa - 2) * F, which independently PROVES that the
engine normalization kappa = 8 pi G = 2 is the unique normalization for
which the exact solution satisfies the constraint.

A 30-digit mpmath spot check on a (u, v) grid (sigma = 0.1) confirms the
symbolic result numerically.
"""
import os
import sys

import mpmath as mp
import sympy as sp

mp.mp.dps = 30

IVP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, IVP_DIR)
from ivp_common import log, save_result, worst_status

u, v, s, kap = sp.symbols("u v sigma kappa", real=True, positive=True)


def roberts_derivatives():
    """All needed derivatives of the Roberts solution as sqrt-free forms.

    Returns dict with r2, its derivatives, Phi, and its derivatives,
    where r_u = r2_u/(2R), etc., and R^2 = r2 is eliminated by carrying
    the required power of r2 explicitly.
    """
    r2 = ((1 - 4 * s**2) * v**2 - 2 * u * v + u**2) / 4
    r2_u = sp.diff(r2, u)
    r2_v = sp.diff(r2, v)
    r2_uu = sp.diff(r2, u, 2)
    r2_vv = sp.diff(r2, v, 2)
    r2_uv = sp.diff(r2, u, 1, v, 1)

    a = 1 - 2 * s - u / v
    b = 1 + 2 * s - u / v
    Phi = sp.Rational(1, 2) * sp.log(a / b)
    Phi_u = sp.diff(Phi, u)
    Phi_v = sp.diff(Phi, v)
    Phi_uv = sp.diff(Phi, u, v)

    return {
        "r2": sp.simplify(r2),
        "r2_u": sp.simplify(r2_u), "r2_v": sp.simplify(r2_v),
        "r2_uu": sp.simplify(r2_uu), "r2_vv": sp.simplify(r2_vv),
        "r2_uv": sp.simplify(r2_uv),
        "Phi": Phi, "Phi_u": sp.simplify(Phi_u),
        "Phi_v": sp.simplify(Phi_v), "Phi_uv": sp.simplify(Phi_uv),
    }


def residuals(D, kappa=2):
    """Residuals of (SC), (UV), (C1), (C2), (TH)+(MD) in sqrt-free form.

    Every residual below is the original residual multiplied by a
    POSITIVE factor (a power of r^2 / r^3), so vanishing of the reduced
    form is equivalent to vanishing of the residual in the domain
    r > 0, v > 0, 1 +- 2 sigma - u/v != 0.
    """
    r2, r2_u, r2_v = D["r2"], D["r2_u"], D["r2_v"]
    r2_uu, r2_vv, r2_uv = D["r2_uu"], D["r2_vv"], D["r2_uv"]
    Phi_u, Phi_v, Phi_uv = D["Phi_u"], D["Phi_v"], D["Phi_uv"]

    # alpha = 1 for Roberts; kappa parametrizes the constraint equations
    res = {}

    # (SC): Phi_uv + (r_u Phi_v + r_v Phi_u)/r = 0
    #   r_u/r^2 = r2_u/(2 r2); multiply by 2 r2 > 0:
    res["SC"] = sp.simplify(2 * r2 * Phi_uv + r2_u * Phi_v + r2_v * Phi_u)

    # (UV): r_uv + (r_u r_v + alpha^2/4)/r = 0
    #   r_uv = (2 r2_uv r2 - r2_u r2_v)/(4 r2 R);  (r_u r_v + 1/4)/R =
    #   (r2_u r2_v + r2)/(4 r2 R);  multiply by 4 r2 R > 0:
    res["UV"] = sp.simplify(2 * r2_uv * r2 - r2_u * r2_v
                            + r2_u * r2_v + r2)

    # (C1): r_uu = 2 omega_u r_u - (kappa/2) r Phi_u^2, omega_u = 0 (alpha=1)
    #   r_uu = (r2_uu r2 - r2_u^2/2)/(2 r2 R); multiply by 4 r2 R:
    res[f"C1(kappa={kappa})"] = sp.simplify(
        r2_uu * r2 - r2_u**2 / 2 + kappa * r2**2 * Phi_u**2)

    # (C2): r_vv = -(kappa/2) r Phi_v^2
    res[f"C2(kappa={kappa})"] = sp.simplify(
        r2_vv * r2 - r2_v**2 / 2 + kappa * r2**2 * Phi_v**2)

    # (MD): m = (R/2)(1 + 4 r_u r_v) = (R/2)(1 + r2_u r2_v / r2)
    # (TH): 0 = m/(2 R^3) - Phi_u Phi_v  =>  m = 2 R^3 Phi_u Phi_v
    # identity to verify:  (1/2)(1 + r2_u r2_v/r2) = 2 r2 Phi_u Phi_v
    #   multiply by 2 r2:
    res["TH+MD"] = sp.simplify(r2 + r2_u * r2_v - 4 * r2**2 * Phi_u * Phi_v)

    return res


def main():
    log("=" * 72)
    log("IVP-06 — independent symbolic residual test (Roberts-Oshiro)")
    log("=" * 72)

    D = roberts_derivatives()

    log("\n[A] symbolic residuals (kappa = 2), domain r > 0, v > 0")
    rows = {}
    checks = {}
    res2 = residuals(D, kappa=2)
    for name, expr in res2.items():
        val = sp.simplify(expr)
        rows[name] = str(val)
        ok = val == 0
        checks[f"residual_{name}_zero"] = ok
        log(f"    [{'OK ' if ok else 'FAIL'}] {name:<16} residual = {val}")

    log("\n[B] normalization proof: (C1) with kappa as a free symbol")
    res_free = residuals(D, kappa=kap)
    expr_free = sp.simplify(res_free["C1(kappa=kappa)"])
    factored = sp.factor(expr_free)
    log(f"    C1 residual (free kappa) factors as: {factored}")
    contains_k_minus_2 = False
    if factored.has(kap):
        # check the polynomial in kappa vanishes at kappa = 2
        contains_k_minus_2 = sp.simplify(expr_free.subs(kap, 2)) == 0
        nonzero_off2 = sp.simplify(expr_free.subs(kap, sp.Rational(3, 2))) != 0
    else:
        nonzero_off2 = expr_free != 0
    checks["C1_kappa_free_vanishes_at_2"] = bool(contains_k_minus_2)
    checks["C1_kappa_free_NONZERO_away_from_2"] = bool(nonzero_off2)
    log(f"    vanishes at kappa = 2          : {contains_k_minus_2}")
    log(f"    NON-zero at kappa = 3/2        : {nonzero_off2}")
    log("    => kappa = 8 pi G = 2 is the unique normalization consistent")
    log("       with the exact solution (independent proof of B2 in IVP-05)")

    log("\n[C] 30-digit numeric spot check (sigma = 0.1)")
    s_val = mp.mpf("0.1")
    worst = mp.mpf(0)
    for uu in (mp.mpf("-0.2"), mp.mpf("0.1"), mp.mpf("0.4")):
        for vv in (mp.mpf("0.8"), mp.mpf("1.3")):
            for name, expr in res2.items():
                val = mp.mpf(str(sp.N(expr.subs({u: uu, v: vv, s: s_val}), 30)))
                worst = max(worst, abs(val))
    log(f"    worst |residual| over grid: {mp.nstr(worst, 3)}")
    checks["numeric_spot_check_below_1e-20"] = bool(worst < mp.mpf("1e-20"))

    status = worst_status(["PASS" if x else "FAIL" for x in checks.values()])
    log(f"\nIVP-06 overall: {status}")
    save_result("IVP06", {
        "status": status,
        "pre_registered": {
            "method": "SymPy differentiation from scratch of the published " +
                      "Roberts-Oshiro form; residuals reduced sqrt-free; " +
                      "must simplify to exactly 0; kappa free-symbol proof",
            "note": "stronger than numeric regression: residuals vanish " +
                    "IDENTICALLY, not approximately",
        },
        "residuals": rows,
        "kappa_factorization": str(factored),
        "numeric_worst_residual": float(worst),
        "checks": checks,
    })
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
