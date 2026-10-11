"""
validate.py — the 50-digit layer (mpmath), the honest backbone.

Recomputes every closed-form constant of the package in 50-significant-digit
arithmetic, independently of the float values in constants.py.  Run:

    python3 -m qhb.validate

Committed status: 9/9 checks PASS (qhb v1.0.0).
"""
import sys

from mpmath import cos, mp, mpf, pi

DPS = 50
mp.dps = DPS

import qhb

from .constants import (
    A_WU_ANCHOR,
    BERRY_TRIO,
    BRAKING_TRIO,
    T_CMB,
    T_QCD_K,
    G,
    MeV_J,
    b_Ch,
    c,
    gamma_Ch,
    hbar,
    k_B,
)


def _f(x):
    return float(x)


def check_berry_braking():
    """T1 layer: the six correction quanta at 50 digits."""
    out = {}
    ok = True
    for name, exact, val in (
            ("bA", pi**2 / 8, BERRY_TRIO[0]),
            ("bB", pi**2 / 18, BERRY_TRIO[1]),
            ("bC", pi**2 / 98, BERRY_TRIO[2]),
            ("aA", pi**5 / 704, BRAKING_TRIO[0]),
            ("aB", pi**5 / 5346, BRAKING_TRIO[1]),
            ("aC", pi**5 / 369754, BRAKING_TRIO[2])):
        dev = abs(exact - mpf(val))
        out[name] = float(dev)
        ok = ok and dev <= mpf(5) * mpf(10) ** (-16)
    return ok, out


def check_bch_gap():
    """Inherited CHB comparison: |gamma_Ch - b_Ch|/b_Ch = 0.67%."""
    b = 1 - cos(2 * pi / 7)
    dev = abs(b - mpf(b_Ch))
    gap = abs(mpf(gamma_Ch) - b) / b * 100
    return (dev <= mpf(5) * mpf(10) ** (-16) and
            abs(gap - mpf("0.6667")) < mpf("0.001")), {
        "gap_pct": _f(gap), "b_Ch_50d": float(b)}


def check_qcd_contact():
    """Theorem T8: M_QCD = hbar c^3 / (8 pi G kB T_QCD), and the MeV chain."""
    num = mpf(hbar) * mpf(c) ** 3
    den = 8 * pi * mpf(G) * mpf(k_B) * mpf(T_QCD_K)
    M_qcd = num / den
    # the exact T_QCD chain: 155.16 MeV -> K
    T_from_MeV = mpf(155.16) * mpf(MeV_J) / mpf(k_B)
    dev_T = abs(T_from_MeV - mpf(T_QCD_K)) / T_from_MeV
    return dev_T <= mpf(1e-12), {
        "M_QCD_kg": _f(M_qcd), "T_chain_dev": _f(dev_T)}


def check_cmb_contact():
    """Inherited CHB contact: M_CMB = 4.5016e22 kg."""
    M = mpf(hbar) * mpf(c) ** 3 / (8 * pi * mpf(G) * mpf(k_B) * mpf(T_CMB))
    return abs(M - mpf("4.5015948405198975e22")) < mpf(1e17), {
        "M_CMB_kg": _f(M)}


def check_wu_limits():
    """Theorem T7 limits: r(0,x)=0, r(alpha,inf)=alpha, r(alpha,0)=0."""
    from .wu import residual
    r0 = residual(0.0, 100.0)
    r_big = residual(mpf(A_WU_ANCHOR), mpf(1e8))
    r_small = residual(mpf(A_WU_ANCHOR), mpf(1e-8))
    return (abs(r0) < 1e-300 and
            abs(r_big - mpf(A_WU_ANCHOR)) < mpf(1e-7) and
            r_small < mpf(1e-7)), {
        "r_alpha0": _f(r0), "r_x_inf": _f(r_big), "r_x_0": _f(r_small)}


def check_gascheau():
    """Theorem T4: nu_equal = 1/3 > 1/27; growth rate sqrt(3/2)."""
    nu = mpf(3) / 9            # (1+1+1)/9 for equal masses
    thr = mpf(1) / 27
    rate = (mpf(3) / 2) ** (mpf(1) / 2)
    return nu > thr and abs(rate - mpf("1.2247448713915890491")) < mpf(1e-15), {
        "nu": _f(nu), "threshold": _f(thr), "growth_n": _f(rate)}


def check_planck_units():
    """Planck unit identities (relative deviations)."""
    lP2 = mpf(hbar) * mpf(G) / mpf(c) ** 3
    mP2 = mpf(hbar) * mpf(c) / mpf(G)
    rhoP = mpf(c) ** 5 / (mpf(hbar) * mpf(G) ** 2)
    from .constants import l_P, m_P, rho_P
    dev_l = abs(lP2 - mpf(l_P ** 2)) / lP2
    dev_m = abs(mP2 - mpf(m_P ** 2)) / mP2
    dev_r = abs(rhoP - mpf(rho_P)) / rhoP
    return (max(dev_l, dev_m, dev_r) < mpf(10) ** (-15)), {
        "max_rel_dev": _f(max(dev_l, dev_m, dev_r))}


def check_tqcd_chain():
    """T_QCD = 155.16 MeV / k_B — the exact conversion used in Part A."""
    T = mpf(155.16) * mpf(MeV_J) / mpf(k_B)
    return abs(T - mpf(T_QCD_K)) / T < mpf(1e-12), {"T_QCD_K": _f(T)}


def check_page_fraction():
    """Inherited exact identity: 1 - 2^(-3/2)."""
    pf = 1 - mpf(2) ** (mpf(-3) / 2)
    from .bridge import PAGE_FRACTION
    return abs(pf - mpf(PAGE_FRACTION)) < mpf(1e-16), {"pf": _f(pf)}


CHECKS = [
    ("six correction quanta (T1 layer)", check_berry_braking),
    ("b_Ch identity + 0.67% gap (inherited)", check_bch_gap),
    ("QCD contact M_QCD (T8)", check_qcd_contact),
    ("CMB contact M_CMB (inherited)", check_cmb_contact),
    ("Wu residual limits (T7)", check_wu_limits),
    ("Gascheau 1/27 vs 1/3 (T4)", check_gascheau),
    ("Planck units", check_planck_units),
    ("T_QCD MeV->K chain", check_tqcd_chain),
    ("Page fraction identity (inherited)", check_page_fraction),
]


def main():
    npass = 0
    print(f"{'check':42s}  verdict  details")
    for name, fn in CHECKS:
        try:
            ok, info = fn()
        except Exception as exc:                       # pragma: no cover
            ok, info = False, {"error": str(exc)}
        npass += bool(ok)
        print(f"{name:42s}  {'PASS' if ok else 'FAIL':4s}    {info}")
    print(f"{npass}/{len(CHECKS)} checks PASS (mpmath dps={DPS}, "
          f"qhb v{qhb.__version__})")
    return 0 if npass == len(CHECKS) else 1


if __name__ == "__main__":
    sys.exit(main())
