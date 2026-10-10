"""C9 phase map and C10 competing models."""
import pytest

from qhb import competing, constants as C, phase_map


def test_c9_grid_all_open():
    betas41 = [round(2.80 + 0.04375 * i, 6) for i in range(41)]
    vols9 = [6, 8, 10, 12, 16, 20, 24, 28, 32]
    pg = phase_map.phase_grid(betas41, vols9)
    assert pg["n_cells"] == 369
    assert pg["all_open"] and pg["n_open"] == 369


def test_c9_valley_exact_recovery():
    betas41 = [round(2.80 + 0.04375 * i, 6) for i in range(41)]
    vr = phase_map.valley_refine(betas41)
    assert vr["beta_star"] == pytest.approx(3.3583, abs=1e-9)
    assert vr["delta_F_min"] == pytest.approx(0.181777, abs=1e-12)
    assert vr["curvature"] == pytest.approx(0.7, abs=1e-9)


def test_c9_naive_falsifier():
    nf = phase_map.naive_falsifier()
    assert nf["beta_c_naive"] == 2.9910
    assert nf["ratio_measured"] == pytest.approx(6.3, rel=1e-12)
    assert nf["falsified"]
    assert nf["flank_ratio"] > 1.0


def test_c10_shares_exact_pins():
    sh = competing.fit_shares()
    assert sh["A_pct"] == pytest.approx(91.9509, abs=5e-3)
    assert sh["B_pct"] == pytest.approx(8.0001, abs=5e-3)
    assert sh["C_pct"] == pytest.approx(0.049, abs=5e-3)
    assert sh["additivity_bias"] == pytest.approx(1.3e-4, abs=2e-5)


def test_c10_braking_control_exact_zero():
    assert abs(competing.braking_estimator_control()) < 1e-12
    assert competing.braking_estimator_B2() == pytest.approx(0.4011, abs=1e-3)


def test_c10_wing_power():
    ow = competing.out_of_window_residual()
    assert ow["residual_power"] == pytest.approx(4.071, abs=2e-3)


def test_c10_even_sector_symmetry():
    # f_A and f_C are even about t=5, f_B odd - by construction
    for t in (1.3, 2.9, 4.1, 6.7):
        assert competing.f_A(t) == pytest.approx(competing.f_A(10 - t), rel=1e-12)
        assert competing.f_C(t) == pytest.approx(competing.f_C(10 - t), rel=1e-12)
        assert competing.f_B(t) == pytest.approx(-competing.f_B(10 - t), rel=1e-12)
