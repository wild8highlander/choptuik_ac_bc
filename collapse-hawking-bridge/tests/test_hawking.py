# -*- coding: utf-8 -*-
"""Closed-form Schwarzschild thermodynamics: book-level reference numbers."""
import math

from chbridge import hawking as H
from chbridge.constants import T_CMB, M_sun, yr


def test_schwarzschild_radius_solar():
    """r_s(M_sun) = 2954 m for M_sun = 1.98892e30 kg."""
    assert abs(H.r_s(M_sun) - 2954.0) / 2954.0 < 1e-4


def test_hawking_temperature_solar():
    """T_H(M_sun) ~ 6.17e-8 K."""
    assert abs(H.T_H(M_sun) - 6.17e-8) / 6.17e-8 < 1e-2


def test_entropy_solar():
    """S_BH(M_sun)/k_B ~ 1.05e77 (matches bridge_master saturated solar row)."""
    s = H.S_BH(M_sun) / 1.380649e-23
    assert abs(s - 1.049430e77) / 1.049430e77 < 1e-3


def test_power_laws():
    """T ~ 1/M, S ~ M^2, t_evap ~ M^3, P ~ 1/M^2, kappa ~ 1/M."""
    import numpy as np
    M = np.array([1e12, 1e15, 1e18])
    T = np.array([H.T_H(m) for m in M])
    S = np.array([H.S_BH(m) for m in M])
    t = np.array([H.t_evap(m) for m in M])
    P = np.array([H.P_H(m) for m in M])
    kap = np.array([H.surface_gravity(m) for m in M])
    assert abs((T[0] / T[2]) - 1e6) / 1e6 < 1e-9
    assert abs((S[2] / S[0]) - 1e12) / 1e12 < 1e-9
    assert abs((t[2] / t[0]) - 1e18) / 1e18 < 1e-9
    assert abs((P[0] / P[2]) - 1e12) / 1e12 < 1e-9
    assert abs((kap[0] / kap[2]) - 1e6) / 1e6 < 1e-9


def test_page_fraction_exact():
    assert abs(H.t_page(1e12) / H.t_evap(1e12) - H.PAGE_FRACTION) < 1e-15
    assert abs(H.PAGE_FRACTION - 0.6464466094067262) < 1e-15


def test_cmb_contact():
    """T_H(M_CMB) = T_CMB; M_CMB ~ 4.5e22 kg (moon-mass)."""
    M = H.equal_CMB_mass()
    assert abs(H.T_H(M) - T_CMB) / T_CMB < 1e-12
    assert abs(M - 4.50e22) / 4.50e22 < 2e-3
    assert abs(M / 7.342e22 - 0.613) < 0.01   # ~0.61 lunar masses


def test_mean_density_scaling():
    """rho_bar ~ M^-2."""
    r1 = H.rho_mean(1e12)
    r2 = H.rho_mean(1e18)
    assert abs((r1 / r2) - 1e12) / 1e12 < 1e-9


def test_human_formatting():
    assert "yr" in H.fmt_time(H.t_evap(1e12))
    assert H.fmt_len(2953.25) == "2953 m"
    assert H.fmt_len(0.002) == "2 mm"


def test_page_continuity_at_kink():
    """At t_Page: (1-t/t_evap) = 2^{-3/2} => S_BH = S0/2 from BOTH sides."""
    frac = H.PAGE_FRACTION
    u = (1.0 - frac) ** (1.0 / 3.0)
    S_bh = u ** 2
    assert abs(S_bh - 0.5) < 1e-12          # left branch value
    assert abs((1.0 - S_bh) - 0.5) < 1e-12  # right branch (S0 - S_BH)
