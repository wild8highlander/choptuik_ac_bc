"""C1-C4 campaigns."""
import math

import pytest

from qhb import constants as C, core


def test_c1_grid_all_open():
    betas = [round(2.80 + 0.21875 * i, 6) for i in range(9)]
    vols = [6, 8, 10, 12, 16, 20, 24, 28, 32]
    t = core.c1_gap_table(betas, vols)
    assert t["all_open"]
    assert t["grid_min"] == pytest.approx(0.1744897100496875, abs=1e-12)
    assert t["grid_argmin"] == [3.45625, 6]


def test_c1_finite_volume_correction():
    g_inf = C.delta_F_of_beta(3.4)
    assert core.gap_finite_volume(3.4, 1e9) == pytest.approx(g_inf, abs=1e-9)
    assert core.gap_finite_volume(3.4, 6) < g_inf


def test_c2_wilson_law_exact():
    s = C.sigma_of_beta(C.BETA_STAR)
    R, T = 2.0, 3.0
    assert core.wilson_loop(C.BETA_STAR, R, T) == pytest.approx(
        math.exp(-s * R * T), rel=1e-15)


def test_c2_measurement_recovers_sigma():
    loops = [(1, 1), (1, 2), (2, 1), (2, 2), (3, 2), (4, 3)]
    for b in (2.9, C.BETA_STAR, 4.4):
        assert core.sigma_measure(b, loops) == pytest.approx(
            C.sigma_of_beta(b), rel=1e-12)


def test_c3_correction_sign_and_size():
    base = core.bridge_temperature(C.BETA_STAR, corrections=False)
    full = core.bridge_temperature(C.BETA_STAR, corrections=True)
    assert full > base
    assert 100 * (full / base - 1) == pytest.approx(11.28, abs=0.01)


def test_c3_spin_exact_100d():
    vals = core.spin_constants_exact(100)
    assert vals["c1"].startswith("1.23370055013616982735431137498")
    assert vals["c2"].startswith("0.43468705225182024611184845176")


def test_c4_tail_not_resolved():
    a = core.c4_tail_audit(C.BETA_STAR)
    assert a["tail_resolved"] is False
    assert a["degenerate"] and a["n_pos"] == 50 and a["n_neg"] == 0
    assert a["upper_bound_95"] > a["tail_amplitude_max"]


def test_runs_test_random_sequence():
    seq = [1, -1, -1, 1, 1, -1, 1, -1]
    assert abs(core.runs_test_z(seq)) < 1.0
    # alternating sequence: maximally many runs -> large positive z
    assert core.runs_test_z([1, -1] * 4) > 1.9


def test_runs_test_degenerate():
    assert core.runs_test_z([1] * 10) == -999.0
