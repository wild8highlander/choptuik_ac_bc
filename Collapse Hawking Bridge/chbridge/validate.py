"""
validate.py — high-precision re-verification of every project constant.

All closed-form constants are recomputed in 50-digit arithmetic with
mpmath, independently of the float values committed in constants.py.
Run as a script, it prints a check table; as a module, it gives booleans
used by the pytest suite (tests/test_constants.py).

Checks
------
 1. b_Ch = 1 - cos(2 pi/7) = 2 sin^2(pi/7)          (exact identity)
 2. b_Ch vs gamma_Ch = 0.374                         (0.67% framework gap)
 3. PAGE_FRACTION = 1 - 2^{-3/2} = 0.6464466...
 4. t_Page/t_evap consistency, S(M)/k_B ~ M^2, T_H ~ 1/M, t_evap ~ M^3
 5. CMB contact mass: T_H(M_CMB) = T_CMB (both directions)
 6. Planck units: l_P, t_P, m_P self-consistency  (m_P = hbar/(l_P c) ...)
 7. Delta*gamma anchor product = 3.44 * 0.374 = 1.28656 vs target 1.27
    (ARITHMETIC CONSISTENCY of the project's own anchors — not a
    physics measurement; the engine-level test is governed by
    PREREGISTRATION.md and is honestly INCONCLUSIVE at committed
    resolutions)
 8. Kretschmann at horizon: K(M) * M^4 = 3c^8/(4G^4)  (scale invariance)
"""

import mpmath as mp

mp.mp.dps = 50

from .constants import (
    DGAMMA_TARGET,
    __version__,
    b_Ch,
    echo_delta,
    gamma_Ch,
    kretschmann_horizon,
    l_P,
    m_P,
    t_P,
)
from .hawking import PAGE_FRACTION, S_BH, T_H, equal_CMB_mass, t_evap

# --- mpmath mirrors of Part A ------------------------------------------------
_G = mp.mpf("6.67430e-11")
_c = mp.mpf("299792458")
_h = mp.mpf("6.62607015e-34")
_hbar = _h / (2 * mp.pi)
_kB = mp.mpf("1.380649e-23")
_TCMB = mp.mpf("2.72548")


def check_b_Ch():
    """b_Ch = 1 - cos(2pi/7) = 2 sin^2(pi/7) and the 0.67% framework gap."""
    b_ref = 1 - mp.cos(2 * mp.pi / 7)
    ok_identity = abs(mp.mpf(b_Ch) - b_ref) < mp.mpf("1e-16")
    gap = abs(b_ref - mp.mpf(gamma_Ch)) / b_ref
    return {"ok": bool(ok_identity and gap < mp.mpf("0.007")),
            "b_Ch_ref": b_ref, "gap_pct": float(100 * gap)}


def check_page_fraction():
    """PAGE_FRACTION = 1 - 2^{-3/2}."""
    ref = 1 - mp.power(2, mp.mpf("-3/2"))
    return {"ok": abs(mp.mpf(PAGE_FRACTION) - ref) < mp.mpf("1e-16"),
            "ref": float(ref)}


def check_power_laws():
    """S ~ M^2, T ~ 1/M, t_evap ~ M^3 numerically at two masses."""
    M1, M2 = mp.mpf("1e12"), mp.mpf("1e22")
    tol = mp.mpf("1e-9")   # RELATIVE tolerance
    S1, S2 = mp.mpf(S_BH(float(M1))), mp.mpf(S_BH(float(M2)))
    T1, T2 = mp.mpf(T_H(float(M1))), mp.mpf(T_H(float(M2)))
    t1, t2 = mp.mpf(t_evap(float(M1))), mp.mpf(t_evap(float(M2)))
    ok = (abs((S2 / S1) / (M2 / M1)**2 - 1) < tol
          and abs((T1 / T2) / (M2 / M1) - 1) < tol
          and abs((t2 / t1) / (M2 / M1)**3 - 1) < tol)
    return {"ok": bool(ok)}


def check_cmb_contact():
    """T_H(M_CMB) == T_CMB and inverse formula round-trip."""
    M = mp.mpf(equal_CMB_mass())
    T = _hbar * _c**3 / (8 * mp.pi * _G * M * _kB)
    M_ref = _hbar * _c**3 / (8 * mp.pi * _G * _kB * _TCMB)
    return {"ok": bool(abs(T - _TCMB) / _TCMB < mp.mpf("1e-12")
                       and abs(M - M_ref) / M_ref < mp.mpf("1e-6")),
            "M_CMB": float(M)}


def check_planck_units():
    """l_P^5 = hbar G / c^3 * l_P ... consistency: m_P = hbar/(l_P c)."""
    lp = mp.sqrt(_hbar * _G / _c**3)
    mp_m = _hbar / (lp * _c)
    tp = lp / _c
    return {"ok": bool(abs(lp - mp.mpf(l_P)) / lp < mp.mpf("1e-12")
                       and abs(mp_m - mp.mpf(m_P)) / mp_m < mp.mpf("1e-12")
                       and abs(tp - mp.mpf(t_P)) / tp < mp.mpf("1e-12"))}


def check_dgamma():
    """Anchor product Delta*gamma vs the FROZEN C3 target 1.27.

    v2.2.0 semantics (external audit, point 10): this check verifies the
    ARITHMETIC CONSISTENCY of the project's own two anchors (3.44 x 0.374
    = 1.28656) with the frozen target 1.27 +- 0.05 (PREREGISTRATION.md).
    It is NOT a physics measurement: both factors are anchors.  The
    engine-level product (both factors measured) is the physical test and
    is honestly INCONCLUSIVE at every committed resolution (floor-
    dominated gamma, fewer than three resolved echo peaks).
    """
    prod = mp.mpf(echo_delta) * mp.mpf(gamma_Ch)
    dev = abs(prod - mp.mpf(DGAMMA_TARGET))
    return {"ok": bool(dev < mp.mpf("0.02")),
            "product": float(prod), "dev": float(dev)}


def check_kretschmann():
    """K(M)*M^4 is M-independent = 3c^8/(4G^4)."""
    ref = 3 * _c**8 / (4 * _G**4)
    for M in ("1e12", "1e22", "1.98892e30"):
        K = mp.mpf(kretschmann_horizon(float(M))) * mp.mpf(M)**4
        if abs(K - ref) / ref > mp.mpf("1e-9"):
            return {"ok": False}
    return {"ok": True}


ALL_CHECKS = {
    "b_Ch identity + 0.67% gap": check_b_Ch,
    "PAGE_FRACTION": check_page_fraction,
    "S~M^2, T~1/M, t~M^3": check_power_laws,
    "CMB contact": check_cmb_contact,
    "Planck units": check_planck_units,
    "Delta*gamma anchor arithmetic (not a measurement)": check_dgamma,
    "Kretschmann scale law": check_kretschmann,
}


def run_all():
    """Run every check; returns dict name -> result dict."""
    return {name: fn() for name, fn in ALL_CHECKS.items()}


if __name__ == "__main__":
    results = run_all()
    width = max(len(k) for k in results)
    print(f"{'check':<{width}}  {'status':<6}  detail")
    print("-" * (width + 46))
    for name, res in results.items():
        status = "PASS" if res["ok"] else "FAIL"
        detail = {k: (round(v, 6) if isinstance(v, float) else v)
                  for k, v in res.items() if k != "ok"}
        print(f"{name:<{width}}  {status:<6}  {detail}")
    n_ok = sum(r["ok"] for r in results.values())
    print(f"\n{n_ok}/{len(results)} checks PASS "
          f"(mpmath dps={mp.mp.dps}, chbridge v{__version__})")
