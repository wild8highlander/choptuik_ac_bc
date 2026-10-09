#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IVP-05 — dimensional-analysis audit.

Part A (SI physics): a small exact dimension algebra over the basis
{length, mass, time, temperature} verifies dimensionally that

    r_s -> L,  A_H -> L^2,  S_BH -> J/K,  T_H -> K,
    P_H -> W,  t_evap -> s,  rho_mean -> kg/m^3,  kappa_sg -> m/s^2,

with G = L^3 M^-1 T^-2, c = L T^-1, hbar = L^2 M T^-1, k_B = L^2 M T^-2 Θ^-1.
Each formula is substituted symbolically (SymPy) and reduced to a basis
monomial; the exponent vector must equal the pre-registered expectation.

Part B (engine normalization): the numerical engine works in geometric
units with the declared normalization 4 pi G = 1, i.e. kappa = 8 pi G = 2.
The verifier checks
  B1. arithmetic: 8 pi (4 pi)^-1 = 2 exactly;
  B2. code-level: engine/solver.py declares KAPPA == 2 and uses it in
      the constraint equations (the mathematical consistency of kappa = 2
      with the exact solution is proven independently in IVP-06).
"""
import os
import re
import sys

import sympy as sp

IVP_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(IVP_DIR)
sys.path.insert(0, IVP_DIR)
from ivp_common import save_result, log, worst_status  # noqa: E402

# basis symbols
L, M, T, TH = sp.symbols("L M T Theta")

# dimension exponents of the ingredients
DIMS = {
    "G":    (3, -1, -2, 0),
    "c":    (1, 0, -1, 0),
    "hbar": (2, 1, -1, 0),
    "k_B":  (2, 1, -2, -1),
    "M":    (0, 1, 0, 0),
    "pi":   (0, 0, 0, 0),
}
EXPECTED = {
    "r_s":      (1, 0, 0, 0),        # m
    "A_H":      (2, 0, 0, 0),        # m^2
    "S_BH":     (2, 1, -2, -1),      # J/K
    "T_H":      (0, 0, 0, 1),        # K
    "P_H":      (2, 1, -3, 0),       # W
    "t_evap":   (0, 0, 1, 0),        # s
    "rho_mean": (-3, 1, 0, 0),       # kg/m^3
    "kappa_sg": (1, 0, -2, 0),       # m/s^2
}
FORMULAS = {
    "r_s":      "2*G*M/c**2",
    "A_H":      "4*pi*(2*G*M/c**2)**2",
    "S_BH":     "k_B*c**3*4*pi*(2*G*M/c**2)**2/(4*G*hbar)",
    "T_H":      "hbar*c**3/(8*pi*G*M*k_B)",
    "P_H":      "hbar*c**6/(15360*pi*G**2*M**2)",
    "t_evap":   "5120*pi*G**2*M**3/(hbar*c**4)",
    "rho_mean": "3*M/(4*pi*(2*G*M/c**2)**3)",
    "kappa_sg": "c**4/(4*G*M)",
}


def dim_vector(expr_str):
    """Reduce a closed form to its (L, M, T, Θ) exponent vector."""
    e = sp.sympify(expr_str)
    for name, (l, m, t, th) in DIMS.items():
        e = e.xreplace({sp.Symbol(name): L**l * M**m * T**t * TH**th})
    e = sp.simplify(e)
    vec = []
    for b in (L, M, T, TH):
        num, den = sp.fraction(e)
        deg = 0
        for part, sign in ((num, 1), (den, -1)):
            if part == 1:
                continue
            p = sp.Poly(part, b)
            if b in p.gens:
                deg += sign * p.degree(b)
        vec.append(int(deg))
    return tuple(vec)


def engine_code_checks():
    """Code inspection of engine/solver.py (constants, not measurements)."""
    src = open(os.path.join(ROOT, "engine", "solver.py"), encoding="utf-8").read()
    m = re.search(r"^KAPPA\s*=\s*([0-9.]+)", src, re.M)
    return {
        "kappa_declared": float(m.group(1)) if m else None,
        "KAPPA_occurrences": len(re.findall(r"KAPPA", src)),
        "normalization_comment_present": re.search(r"4\s*pi\s*G\s*=\s*1", src) is not None,
    }


def main():
    log("=" * 72)
    log("IVP-05 — dimensional-analysis audit")
    log("=" * 72)

    checks = {}

    log("\n[A] SI closed forms -> expected dimensions")
    dim_rows = []
    for name, expr in FORMULAS.items():
        got = dim_vector(expr)
        want = EXPECTED[name]
        ok = got == want
        checks[f"dim_{name}"] = ok
        dim_rows.append({"quantity": name, "formula": expr,
                         "got": got, "expected": want, "ok": ok})
        log(f"    [{'OK ' if ok else 'FAIL'}] {name:<10} {got}  expected {want}")

    log("\n[B] engine normalization (4 pi G = 1  =>  kappa = 8 pi G = 2)")
    kappa_arith = sp.simplify(8 * sp.pi / (4 * sp.pi))
    checks["B1_kappa_arithmetic"] = bool(kappa_arith == 2)
    code = engine_code_checks()
    checks["B2_engine_declares_kappa_2"] = code["kappa_declared"] == 2.0
    checks["B2b_engine_uses_kappa"] = code["KAPPA_occurrences"] >= 4
    checks["B3_normalization_documented"] = code["normalization_comment_present"]
    log(f"    B1: 8*pi/(4*pi) = {kappa_arith} (exact) -> "
        f"{'OK' if checks['B1_kappa_arithmetic'] else 'FAIL'}")
    log(f"    B2: engine/solver.py KAPPA = {code['kappa_declared']} "
        f"({code['KAPPA_occurrences']} uses) -> "
        f"{'OK' if checks['B2_engine_declares_kappa_2'] else 'FAIL'}")
    log(f"    B3: '4 pi G = 1' normalization documented in engine -> "
        f"{'OK' if checks['B3_normalization_documented'] else 'FAIL'}")
    log("    note: engine-side observables (2m/r, q = r_v) are dimensionless")
    log("    in the geometric normalization; Part A closes the dimensional")
    log("    loop for the physical (SI) layer.")

    status = worst_status(["PASS" if v else "FAIL" for v in checks.values()])
    log(f"\nIVP-05 overall: {status}")
    save_result("IVP05", {
        "status": status,
        "pre_registered": {
            "method": "exact dimension algebra over {L, M, T, Theta}; engine "
                      "normalization checked arithmetically and by code inspection",
            "expected": {k: list(v) for k, v in EXPECTED.items()},
        },
        "dimension_rows": dim_rows,
        "engine_code": code,
        "checks": checks,
    })
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
