"""C5-C8 campaigns."""
import math

import pytest
from qhb import constants as C
from qhb import core
from qhb.pins import C5_N_TRIALS, C5_SEED


def test_c5_escape_threshold_exact():
    e = core.escape_threshold()
    assert abs(e - 0.9912109128777571) < 1e-12
    # analytic tail probability equals the target to fp64 pin precision
    import mpmath as mp
    mp.mp.dps = 40
    tail = mp.gammainc(3, 8 * mp.mpf(str(e)) / 2, mp.inf) / 2
    assert abs(tail - 0.2433) < mp.mpf("1e-15")


def test_c5_mc_pinned_seed():
    r = core.free_three_body(C5_N_TRIALS, C5_SEED)
    assert r["escapes"] == 2433
    assert r["p_esc"] == 0.2433
    assert abs(r["binomial_se"] - math.sqrt(0.2433 * 0.7567 / 10000)) < 1e-12


def test_c5_mc_within_3sigma_any_seed():
    r = core.free_three_body(2000, seed=42)
    z = (r["p_esc"] - 0.2433) / math.sqrt(0.2433 * 0.7567 / 2000)
    assert abs(z) < 3.0


def test_c6_fermat_point_equilateral():
    v = core.fermat_point((0, 0), (1, 0), (0.5, math.sqrt(3) / 2))
    assert v[0] == pytest.approx(0.5, abs=1e-9)
    assert v[1] == pytest.approx(math.sqrt(3) / 6, abs=1e-9)


def test_c6_y_spectrum_min_equilateral():
    shapes = [(1, 1, 1), (1.2, 1, 1), (1.5, 1, 1), (1, 1.2, 1), (1, 1, 1.2),
              (1.5, 1.5, 1), (2, 1.5, 1.5), (2, 2, 1), (2, 2, 2)]
    spec = core.y_string_energy(shapes, C.BETA_STAR)
    e_min = min(s["E_Y"] for s in spec)
    assert spec[0]["E_Y"] == e_min
    assert spec[0]["arm_total"] == pytest.approx(math.sqrt(3), rel=1e-9)


def test_c7_window_closed():
    tw = core.tunneling_window()
    assert tw["closed"]
    assert tw["S_zero"] == pytest.approx(13.856406460551018, rel=1e-12)
    assert tw["T_zero"] == pytest.approx(9.214637827196525e-13, rel=1e-9)
    assert tw["window_E_max"] == pytest.approx(0.005906, abs=2e-4)


def test_c7_monotonicity():
    assert core.wkb_action(0.0) > core.wkb_action(0.5) > core.wkb_action(1.0) > 0


def test_c8_bootstrap_pinned():
    betas = [round(2.80 + 0.21875 * i, 6) for i in range(9)]
    r = core.c8_bootstrap(betas)
    assert r["boot_bias"] == pytest.approx(0.004644, abs=2e-4)
    assert r["boot_bias"] < 0.5 * r["boot_se"]
    assert r["jackknife_bias"] < r["boot_bias"]


def test_c8_ci_covers_theta():
    betas = [round(2.80 + 0.21875 * i, 6) for i in range(9)]
    r = core.c8_bootstrap(betas)
    assert r["ci95"][0] <= r["theta_hat"] <= r["ci95"][1]
