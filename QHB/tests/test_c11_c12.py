"""C11 vortex anchor and C12 asymmetry lock."""
import math

import pytest
from qhb import asymmetry, vortex
from qhb import constants as C
from qhb.pins import (
    C11_AREF_A0,
    C11_AREF_DELTA,
    C11_AREF_DT,
    C11_AREF_T,
    C11_AREF_THETA,
    C11_ROT_DT,
    C11_ROT_T,
)


def test_c11_rigid_rotation_dev():
    r = vortex.rigid_rotation_check(C11_ROT_DT, C11_ROT_T)
    assert r["dev"] < 1e-13
    assert r["radius_drift"] < 1e-12


def test_c11_omega_value():
    assert pytest.approx(0.477464829275686, rel=1e-14) == C.OMEGA


def test_c11_aref_run_pinned():
    r = vortex.aref_boundedness(C11_AREF_A0, C11_AREF_DELTA, C11_AREF_T,
                                C11_AREF_DT, theta=C11_AREF_THETA)
    assert r["r_max"] == pytest.approx(2.7654, abs=2e-4)
    assert r["H0"] < 0
    assert r["r_max"] < r["bound"]
    assert r["I_drift"] < 1e-12
    assert r["bounded"] and r["wall"] == 12.0


def test_c11_pairwise_bound_theorem():
    # exact bound: max pairwise <= 2 sqrt(I) on the pinned run
    r = vortex.aref_boundedness(C11_AREF_A0, C11_AREF_DELTA, C11_AREF_T,
                                C11_AREF_DT, theta=C11_AREF_THETA)
    assert r["r_max"] <= 2 * math.sqrt(r["I0"]) + 1e-9


def test_c13_anchor_potential_shape():
    # V(s) = V* s^2 e^{2-2s}: max exactly at s=1 with value V*
    assert vortex.anchored_potential(1.0) == C.V_STAR
    assert vortex.anchored_potential(0.5) < C.V_STAR
    assert vortex.anchored_potential(2.0) < C.V_STAR
    h = 1e-7
    d = (vortex.anchored_potential(1 + h) - vortex.anchored_potential(1 - h)) / (2 * h)
    assert abs(d) < 1e-5


def test_c11_escape_zero_over_300():
    r = vortex.anchored_escape_scan(300)
    assert r["escapes"] == 0
    assert r["E_max"] < C.V_STAR


# ---------------- C12 ----------------

def test_t14_worst_case_barrier():
    assert asymmetry.barrier_worst(0.0) == C.DELTA_F_MIN
    assert asymmetry.barrier_worst(C.ETA_CRIT) == pytest.approx(0.0, abs=1e-15)
    assert asymmetry.barrier_worst(C.ETA_CRIT / 2) > 0
    assert asymmetry.barrier_worst(C.ETA_B) > 0.09


def test_t14_profiles_worst_is_two():
    profs = asymmetry.profiles()
    drops = [p["drop_at_unit_eta"] for p in profs]
    assert max(drops) == 2.0
    assert all(d <= 2.0 + 1e-12 for d in drops)
    assert len(profs) == 9


def test_t14_margin_value():
    m = asymmetry.asymmetry_margin()
    assert m["margin"] == pytest.approx(148997540.98360655, abs=1e-2)
    assert m["log10_margin"] == pytest.approx(8.1732, abs=1e-3)


def test_c12_phase_grid_boundary():
    pg = asymmetry.phase_grid_eta(41)
    assert pg["n_open"] == 39 and pg["n_cells"] == 41
    for c in pg["cells"]:
        if c["eta"] < C.ETA_CRIT:
            assert c["status"] == "OPEN"
        else:
            assert c["status"] == "CLOSED"


def test_t15_fill_dynamics_eta_b_zero_saturated():
    fd = asymmetry.fill_dynamics(n_steps=200_000, eta=C.ETA_B, seed=424243)
    assert fd["saturated"] == 0
    assert fd["max_fill"] < 0.01


def test_t15_fill_dynamics_positive_control():
    fd = asymmetry.fill_dynamics(n_steps=400_000, eta=0.5, seed=424243)
    assert fd["saturated"] > 0


def test_t15_nugget_bound():
    nb = asymmetry.nugget_bound()
    assert nb["log10_prob_30quarks"] == pytest.approx(-361.0656, abs=1e-3)
    assert nb["log10_prob_macro_N1e30"] < -1e30


def test_t15_summary_consistent():
    s = asymmetry.c12_summary()
    assert s["eta_crit"] == C.ETA_CRIT
    assert s["tunneling"]["T_zero"] < 1e-12
