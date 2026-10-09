# -*- coding: utf-8 -*-
"""Scale ladders and the validation layer."""
import math

from chbridge import ladder as L
from chbridge.constants import (a0, H0, Mpc, c, gamma_Ch, b_Ch, M_sun,
                                kretschmann_horizon, kretschmann_planck)
from chbridge.hawking import equal_CMB_mass, surface_gravity
from chbridge import validate as V


def test_a0_mond_coincidence():
    """a0 / (cH0/2pi) ~ 1.15 — a comparison, never a derivation."""
    H0_SI = H0 / Mpc
    ratio = a0 / (c * H0_SI / (2 * math.pi))
    assert 1.10 < ratio < 1.20


def test_gamma_vs_bch_gap():
    gap = abs(gamma_Ch - b_Ch) / b_Ch
    assert abs(gap - 0.0067) < 0.0005


def test_surface_gravity_ordering():
    """kappa decreases with M along the ladder."""
    M_cmb = equal_CMB_mass()
    assert (surface_gravity(M_sun) < surface_gravity(M_cmb)
            and surface_gravity(M_cmb) < surface_gravity(1e12))


def test_kretschmann_scale_law():
    """K(M) * M^4 is constant = 3c^8/(4G^4)."""
    ref = kretschmann_horizon(M_sun) * M_sun ** 4
    for M in (1e12, 4.5e22, 1e30):
        assert abs(kretschmann_horizon(M) * M ** 4 - ref) / ref < 1e-9


def test_kretschmann_planck_value():
    """1/l_P^4 matches the direct formula c^6/(hbar^2 G^2) (rel. tol)."""
    from chbridge.constants import hbar, G
    rel = abs(kretschmann_planck() - c ** 6 / (hbar ** 2 * G ** 2)) / kretschmann_planck()
    assert rel < 1e-12


def test_ladder_writer_runs(tmp_path):
    info = L.write_outputs(str(tmp_path))
    assert info["accel_rows"] == 7
    assert info["length_rows"] == 8
    assert info["curvature_rows"] == 5
    assert info["constants_rows"] == 8


def test_validate_all_pass():
    """Every 50-digit mpmath check passes."""
    res = V.run_all()
    failed = [k for k, r in res.items() if not r["ok"]]
    assert not failed, f"failed checks: {failed}"
