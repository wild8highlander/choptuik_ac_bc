"""Pinned constants (N1-N8) and derived model quantities."""
import math

from qhb import constants as C


def test_omega_exact():
    assert C.OMEGA == 3.0 / (2.0 * math.pi)
    assert abs(C.OMEGA - 0.47746482927568600731) < 1e-18


def test_valley_pins():
    assert C.BETA_STAR == 3.3583
    assert C.DELTA_F_MIN == 0.181777


def test_gap_valley_minimum():
    for db in (-0.2, -0.05, 0.01, 0.1, 0.35):
        assert C.delta_F_of_beta(C.BETA_STAR + db) > C.DELTA_F_MIN


def test_delta_at_naive_and_threshold():
    assert abs(C.delta_F_of_beta(C.BETA_C_NAIVE) - 0.2289952515) < 1e-12
    assert abs(C.DELTA_THRESH - 0.03634845261904761) < 1e-12
    assert abs(C.DELTA_AT_NAIVE / C.DELTA_THRESH - 6.3) < 1e-9


def test_sigma_law():
    assert C.sigma_of_beta(C.BETA_STAR) == C.SIGMA0
    assert C.sigma_of_beta(4.0) > C.SIGMA0


def test_spin_constants():
    assert abs(C.C1_SPIN - math.pi ** 2 / 8) < 1e-18
    assert abs(C.C2_SPIN - math.pi ** 5 / 704) < 1e-18


def test_eta_crit_and_margin():
    assert C.ETA_CRIT == C.DELTA_F_MIN / 2.0
    assert abs(C.ETA_CRIT - 0.0908885) < 1e-12
    assert abs(C.ASYM_MARGIN - 148997540.98360655) < 1e-2


def test_v_star():
    assert C.V_STAR == 0.9359375


def test_wkb_zero():
    expected = (2.0 / (3.0 * C.SIGMA_STAR)) * (C.SIGMA_STAR * C.L_BOX) ** 1.5
    assert abs(C.S_WKB_ZERO - expected) < 1e-12
    assert C.TUNNEL_T_ZERO < 1e-12


def test_seeds_present():
    assert {C.SEED_MAIN, C.SEED_MC, C.SEED_BOOT, C.SEED_C11} and True
    assert C.SEED_MC != 0
