#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IVP-04 — independent re-derivation of all physical constants.

The verifier NEVER imports chbridge.constants / chbridge.hawking while
measuring.  All constants are re-implemented here in 50-digit mpmath
arithmetic from CODATA-2018 / IAU-2015 definitions, then the closed
forms are evaluated at fixed test masses:

    r_s    = 2 G M / c^2
    A_H    = 4 pi r_s^2
    S_BH   = k_B c^3 A / (4 G hbar)
    T_H    = hbar c^3 / (8 pi G M k_B)
    P_H    = hbar c^6 / (15360 pi G^2 M^2)
    t_evap = 5120 pi G^2 M^3 / (hbar c^4)
    rho_b  = 3 M / (4 pi r_s^3)
    kap    = c^4 / (4 G M)
    M_CMB  = hbar c^3 / (8 pi G k_B T_CMB)      (T_H(M_CMB) = T_CMB)
    l_P, t_P, m_P, T_P, rho_P  (Planck units)

COMPARISON PHASE (end): the same closed forms are evaluated from
`chbridge` (float64) at the same test masses and compared; pre-registered
agreement tolerance is rel <= 1e-9 (float64 roundoff budget), and
derived Planck units must agree to rel <= 1e-12.
"""
import math
import os
import sys

import mpmath as mp

IVP_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(IVP_DIR)
sys.path.insert(0, IVP_DIR)
sys.path.insert(0, ROOT)
from ivp_common import save_result, log, worst_status  # noqa: E402

mp.mp.dps = 50

# ---------------------------------------------------------------------------
# [MEASUREMENT PHASE] verifier-own constants (CODATA 2018, exact SI defs)
# ---------------------------------------------------------------------------
G_ = mp.mpf("6.67430e-11")          # m^3 kg^-1 s^-2
c_ = mp.mpf("299792458")            # m/s (exact)
h_ = mp.mpf("6.62607015e-34")       # J s (exact)
hbar_ = h_ / (2 * mp.pi)
kB_ = mp.mpf("1.380649e-23")        # J/K (exact)
T_CMB_ = mp.mpf("2.72548")          # K (COBE/FIRAS)
M_SUN_NOMINAL = mp.mpf("1.98892e30")  # kg, solar input mass (project spec input)

TEST_MASSES = ["1e12", "4.5016e22", "1.98892e30"]


def closed_forms(M):
    M = mp.mpf(M)
    r_s = 2 * G_ * M / c_ ** 2
    A = 4 * mp.pi * r_s ** 2
    S = kB_ * c_ ** 3 * A / (4 * G_ * hbar_)
    T = hbar_ * c_ ** 3 / (8 * mp.pi * G_ * M * kB_)
    P = hbar_ * c_ ** 6 / (15360 * mp.pi * G_ ** 2 * M ** 2)
    t = 5120 * mp.pi * G_ ** 2 * M ** 3 / (hbar_ * c_ ** 4)
    rho = 3 * M / (4 * mp.pi * r_s ** 3)
    kap = c_ ** 4 / (4 * G_ * M)
    return {"r_s": r_s, "S_BH_over_kB": S / kB_, "T_H": T, "P_H": P,
            "t_evap": t, "rho_mean": rho, "kappa_sg": kap}


def planck_units():
    l_P = mp.sqrt(hbar_ * G_ / c_ ** 3)
    t_P = l_P / c_
    m_P = mp.sqrt(hbar_ * c_ / G_)
    T_P = m_P * c_ ** 2 / kB_
    rho_P = c_ ** 5 / (hbar_ * G_ ** 2)
    return {"l_P": l_P, "t_P": t_P, "m_P": m_P, "T_P": T_P, "rho_P": rho_P}


def m_cmb():
    return hbar_ * c_ ** 3 / (8 * mp.pi * G_ * kB_ * T_CMB_)


def round_trip_check():
    """T_H(M_CMB) must equal T_CMB (both directions, 50 digits)."""
    M = m_cmb()
    T = hbar_ * c_ ** 3 / (8 * mp.pi * G_ * M * kB_)
    return abs(T - T_CMB_) / T_CMB_


def main():
    log("=" * 72)
    log("IVP-04 — independent re-derivation of constants (mpmath dps=50)")
    log("=" * 72)

    mine = {M: closed_forms(M) for M in TEST_MASSES}
    pu = planck_units()
    M_cmb = m_cmb()
    rt = round_trip_check()

    log("\n[A] verifier-own re-derivation (mpmath, 50 digits)")
    for M, vals in mine.items():
        log(f"    M = {M}:")
        for k, v in vals.items():
            log(f"        {k:<14} = {mp.nstr(v, 12)}")
    log("    Planck units:")
    for k, v in pu.items():
        log(f"        {k:<14} = {mp.nstr(v, 12)}")
    log(f"    M_CMB (T_H = T_CMB) = {mp.nstr(M_cmb, 10)} kg   "
        f"(round-trip |dT|/T = {mp.nstr(rt, 3)})")

    # internal consistency of the re-derivation itself
    checks = {
        "T_H(M_CMB) == T_CMB": bool(rt < mp.mpf("1e-30")),
        "S_BH * T_H == M c^2 / 2 (first law)":
            all(abs(vals["S_BH_over_kB"] * vals["T_H"] * kB_
                    - mp.mpf(M) * c_ ** 2 / 2) /
                (mp.mpf(M) * c_ ** 2 / 2) < mp.mpf("1e-30")
                for M, vals in mine.items()),
        "t_evap == M c^2 / (3 P_H) (luminosity integral, P ~ M^-2)":
            all(abs(vals["t_evap"] - mp.mpf(M) * c_ ** 2 / (3 * vals["P_H"]))
                / vals["t_evap"] < mp.mpf("1e-30") for M, vals in mine.items()),
        "rho_mean * r_s^3 == 3M/4pi (definition)":
            all(abs(vals["rho_mean"] * (vals["r_s"]) ** 3
                    - 3 * mp.mpf(M) / (4 * mp.pi)) /
                (3 * mp.mpf(M) / (4 * mp.pi)) < mp.mpf("1e-30")
                for M, vals in mine.items()),
    }

    # ------------------------------------------------------------------
    # [COMPARISON PHASE] chbridge float64 implementations vs this suite
    # ------------------------------------------------------------------
    log("\n[B] comparison phase — chbridge float64 vs verifier (50-digit)")
    from chbridge import hawking as H  # noqa: E402  (comparison only)
    from chbridge import constants as C  # noqa: E402  (comparison only)

    rows = []
    for M in TEST_MASSES:
        ref = mine[M]
        pairs = [
            (f"r_s({M})",            float(ref["r_s"]),            H.r_s(float(M))),
            (f"S_BH/kB({M})",        float(ref["S_BH_over_kB"]),   H.S_BH(float(M)) / H.k_B),
            (f"T_H({M})",            float(ref["T_H"]),            H.T_H(float(M))),
            (f"P_H({M})",            float(ref["P_H"]),            H.P_H(float(M))),
            (f"t_evap({M})",         float(ref["t_evap"]),         H.t_evap(float(M))),
            (f"rho_mean({M})",       float(ref["rho_mean"]),       H.rho_mean(float(M))),
            (f"kappa_sg({M})",       float(ref["kappa_sg"]),       H.surface_gravity(float(M))),
        ]
        for label, a, b in pairs:
            rd = abs(a - b) / max(abs(b), 1e-300)
            rows.append({"quantity": label, "verifier": a, "chbridge": b,
                         "rel_diff": rd, "ok": bool(rd <= 1e-9)})

    pu_pairs = [
        ("l_P",   float(pu["l_P"]),   C.l_P),
        ("t_P",   float(pu["t_P"]),   C.t_P),
        ("m_P",   float(pu["m_P"]),   C.m_P),
        ("T_P",   float(pu["T_P"]),   C.T_P),
        ("rho_P", float(pu["rho_P"]), C.rho_P),
    ]
    for label, a, b in pu_pairs:
        rd = abs(a - b) / max(abs(b), 1e-300)
        rows.append({"quantity": label, "verifier": a, "chbridge": b,
                     "rel_diff": rd, "ok": bool(rd <= 1e-12)})

    rows.append({"quantity": "M_CMB", "verifier": float(M_cmb),
                 "chbridge": H.equal_CMB_mass(),
                 "rel_diff": abs(float(M_cmb) - H.equal_CMB_mass()) / float(M_cmb),
                 "ok": bool(abs(float(M_cmb) - H.equal_CMB_mass()) / float(M_cmb) <= 1e-9)})

    n_bad = 0
    for r in rows:
        mark = "OK " if r["ok"] else "DIFF"
        if not r["ok"]:
            n_bad += 1
        log(f"    [{mark}] {r['quantity']:<22} verifier={r['verifier']:.12e}  "
            f"chbridge={r['chbridge']:.12e}  rel={r['rel_diff']:.2e}")

    # provenance note on the solar input mass (INPUT choice, not an error)
    iau_solar = mp.mpf("1.3271244e20") / G_   # GM_sun(nominal, IAU 2015) / G
    solar_note = {
        "project_input_M_sun": float(M_SUN_NOMINAL),
        "iau2015_GM_over_G": float(iau_solar),
        "rel_diff": float(abs(M_SUN_NOMINAL - iau_solar) / iau_solar),
        "verdict": "INPUT-PROVENANCE note: chbridge uses M_sun = 1.98892e30 kg; "
                   "the IAU 2015 nominal solar mass parameter gives 1.98841e30 kg "
                   "(rel diff ~2.6e-4). This is a declared input constant, not a "
                   "derived value; every closed form above was compared at the "
                   "project's own input mass, so no check depends on this choice.",
    }
    log(f"\n[C] provenance note (input constants): M_sun input = "
        f"{solar_note['project_input_M_sun']:.6e}, "
        f"IAU GM/G = {solar_note['iau2015_GM_over_G']:.6e} "
        f"(rel {solar_note['rel_diff']:.2e}) — informational")

    all_checks = dict(checks)
    all_checks["chbridge_closed_forms_agree"] = n_bad == 0
    status = worst_status(["PASS" if v else "FAIL" for v in all_checks.values()])
    log(f"\nIVP-04 overall: {status}  ({n_bad} float64 mismatches > tolerance)")
    save_result("IVP04", {
        "status": status,
        "pre_registered": {
            "method": "re-derive all closed forms in mpmath dps=50 from CODATA-2018 "
                      "exact definitions; import chbridge only in comparison phase",
            "tolerances": {"float64 closed forms": 1e-9, "Planck units": 1e-12},
        },
        "internal_checks": checks,
        "comparison_rows": rows,
        "n_mismatches": n_bad,
        "solar_mass_provenance": solar_note,
    })
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
