"""Constants of the project: exact identities and committed campaign values."""
import math
import os

import chbridge.constants as K
from chbridge.hawking import PAGE_FRACTION


def test_b_ch_exact_identity():
    """b_Ch = 1 - cos(2pi/7) = 2 sin^2(pi/7)."""
    assert abs(K.b_Ch - (1 - math.cos(2 * math.pi / 7))) < 1e-15
    assert abs(K.b_Ch - 2 * math.sin(math.pi / 7) ** 2) < 1e-15


def test_b_ch_reference_value():
    """The 16-digit reference value 0.37651019814126640."""
    assert abs(K.b_Ch - 0.37651019814126640) < 1e-15


def test_b_ch_framework_gap():
    """b_Ch sits 0.67% from the literature exponent gamma_Ch = 0.374."""
    gap = abs(K.b_Ch - K.gamma_Ch) / K.b_Ch
    assert gap < 0.007
    assert abs(gap - 0.0067) < 0.0005


def test_septinial_phase():
    assert abs(K.delta_C - math.pi / 7) < 1e-15


def test_page_fraction():
    assert abs(PAGE_FRACTION - (1.0 - 2.0 ** -1.5)) < 1e-15
    assert abs(PAGE_FRACTION - 0.6464466094067262) < 1e-15


def test_dgamma_anchor_product():
    """3.44 * 0.374 = 1.28656 — the ANCHOR ARITHMETIC of the C3 invariant.

    v2.2.0: this is arithmetic consistency between the project's own two
    anchors and the frozen target — NOT a physics measurement (the
    engine-level test is governed by PREREGISTRATION.md and is honestly
    INCONCLUSIVE at committed resolutions).
    """
    assert abs(K.DGAMMA_LIT - 3.44 * 0.374) < 1e-12
    assert abs(K.DGAMMA_LIT - 1.28656) < 1e-9
    assert abs(K.DGAMMA_LIT - K.DGAMMA_TARGET) < K.DGAMMA_TOL


def test_package_version_pin():
    """The package version is 2.2.0 everywhere it must be."""
    assert K.__version__ == "2.2.0"
    with open(os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), "VERSION")) as f:
        assert f.read().strip() == "2.2.0"


def test_qnm_relative_shift():
    assert abs(K.qnm_rel_shift - 1.0 / (1200 * math.pi ** 2)) < 1e-18
    assert abs(K.qnm_rel_shift - 8.44343e-5) < 1e-9


def test_clock_theorems_exact():
    assert abs(K.tau_star_baseline - 6.75) < 1e-15
    assert abs(K.tau_star_one_brick - 1323.0 / (196.0 - math.pi ** 2)) < 1e-12
    assert abs(K.berry_kappa - (2.0 - math.pi ** 2 / 98.0)) < 1e-15


def test_campaign_astar_ladder():
    """Committed C1 grid-honesty ladder + remediated deep reference (F-1).

    v2.0.1: the threshold DRIFTS with resolution; A*_800 vs the remediated
    N=1600 reference disagree at 2.79e-3 (the stale 2.0.0 claim of a
    1.06e-6 agreement was an audit finding, retracted).
    """
    c = K.CAMPAIGN
    assert c["a_star_N200"] > c["a_star_N400"] > c["a_star_N800"]
    assert abs(c["a_star_N800"] - 0.08053436279296877) < 1e-12
    # the deep reference is BELOW the N=800 threshold (ladder drifts down)
    assert c["a_star_reference_N1600"] < c["a_star_N800"]
    assert c["a_star_ladder_N3200"] < c["a_star_reference_N1600"]
    # honest drift, retracted 1.06e-6 claim
    drift = abs(c["a_star_N800"] - c["a_star_reference_N1600"])
    assert abs(drift - c["a_star_drift_N800_to_N1600"]) < 1e-12
    assert 2e-3 < drift < 4e-3


def test_planck_units_cross():
    """m_P = sqrt(hbar c / G) ~ 2.176e-8 kg; l_P ~ 1.616e-35 m."""
    assert abs(K.m_P - 2.176434e-8) / 2.176434e-8 < 1e-4
    assert abs(K.l_P - 1.616255e-35) / 1.616255e-35 < 1e-4
    assert abs(K.t_P - K.l_P / K.c) < 1e-50
