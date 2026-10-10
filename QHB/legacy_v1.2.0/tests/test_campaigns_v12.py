# -*- coding: utf-8 -*-
"""Pins for the v1.2.0 campaigns C9 (phase map), C10 (competing models),
C11 (vortex anchor + static barrier)."""
import json
import math
import os

import pytest

REF = os.path.join(os.path.dirname(__file__), "..", "campaigns", "reference")


def load(name):
    with open(os.path.join(REF, name), encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def c9():
    return load("c9_verdict.json")


@pytest.fixture(scope="module")
def c10():
    return load("c10_verdict.json")


@pytest.fixture(scope="module")
def c11():
    return load("c11_verdict.json")


class TestC9PhaseMap:
    def test_all_cells_open(self, c9):
        for row in c9["map"]["rows"]:
            assert row["phases_present"] == ["OPEN"]

    def test_P1_no_closure(self, c9):
        g = c9["gates"]["P1_no_closure"]
        assert g["ok"] is True
        assert g["map_min_Delta_F"] == pytest.approx(0.124449, abs=1e-5)
        assert g["map_min_Delta_F"] > g["floor"]

    def test_P2_valley_refinement(self, c9):
        g = c9["gates"]["P2_valley_refinement"]
        assert g["ok"] is True
        assert g["max_dev"] < 0.05

    def test_P3_N_stability(self, c9):
        g = c9["gates"]["P3_N_stability"]
        assert g["ok"] is True
        assert all(s < 0.1 for s in g["shifts"])

    def test_P4_counterexample(self, c9):
        g = c9["gates"]["P4_counterexample"]
        ce = c9["counterexample"]
        assert g["ok"] is True
        assert ce["beta_c_quadratic_forecast"] == pytest.approx(2.9910,
                                                                abs=1e-3)
        assert ce["ratio_to_floor"] > 3.0

    def test_valley_committed_geometry(self, c9):
        v = next(r for r in c9["valley"] if abs(r["q_pk"] - 0.4) < 1e-9)
        assert v["beta_star"] == pytest.approx(3.3583, abs=0.05)
        assert v["Delta_F_min"] == pytest.approx(0.181777, abs=1e-4)
        assert v["above_floor"] is True

    def test_regime_bound_carried(self, c9):
        assert "q_pk >= 0.2" in c9["map"]["regime_bound"]


class TestC10CompetingModels:
    def test_causal_ordering(self, c10):
        s = c10["causal_shares"]
        assert s["A"] > s["B"] > s["C"]
        assert s["A"] == pytest.approx(0.9195, abs=5e-4)
        assert s["C"] < 0.001

    def test_B2_ABC_matches_C1(self, c10):
        # C10 uses a zero-intercept estimator (shift = B2 beta^2 with the
        # committed Delta_0 subtracted); C1 fits both parameters.  The two
        # estimators agree to 3.2e-4 relative — the honest cross-check band.
        abc = next(r for r in c10["ablation"] if r["config"] == "ABC")
        assert abc["B2"] == pytest.approx(-5.49670294e-2, rel=5e-3)

    def test_braking_only_invisible(self, c10):
        none = next(r for r in c10["ablation"] if r["config"] == "none")
        assert none["B2"] == 0.0
        assert c10["gates"]["Q2_braking_only_invisible"]["ok"] is True

    def test_evenness_all_configs(self, c10):
        assert c10["gates"]["Q1_evenness_all_configs"]["ok"] is True
        for r in c10["ablation"]:
            assert r["b_flip_dev"] < 1e-12

    def test_additivity(self, c10):
        g = c10["gates"]["Q3_additivity"]
        assert g["ok"] is True
        assert g["max_cross_share"] < 0.01
        assert g["max_cross_share"] == pytest.approx(1.2976e-4, rel=1e-2)

    def test_forecast_failure_carried(self, c10):
        rows = c10["forecast"]["rows"]
        shares = [r["error_share"] for r in rows]
        assert shares == sorted(shares)            # monotone growth
        assert shares[-1] > 0.02
        p = c10["forecast"]["effective_residual_power"]
        assert 3.5 < p < 4.5                       # the quartic wing

    def test_honest_scope_note(self, c10):
        assert any("does not compare QHB against external QCD data" in n
                   for n in c10["honest_notes"])


class TestC11VortexBarrier:
    def test_T11_spectrum(self, c11):
        b1 = c11["blocks"]["B1_T11_exact"]
        assert b1["ok"] is True
        assert b1["max_re_on_imag_pairs"] < 1e-12
        assert b1["charpoly_identity_dev"] < 1e-12
        assert b1["zero_pair_max_magnitude"] < 1e-6
        assert b1["omega_exact"] == pytest.approx(3.0 / (2.0 * math.pi),
                                                  rel=1e-15)

    def test_T11_rotation(self, c11):
        b2 = c11["blocks"]["B2_T11_rotation"]
        assert b2["ok"] is True
        assert b2["omega_dev"] < 1e-6
        assert b2["shape_err_max"] < 1e-10
        assert max(b2["invariants_drift"].values()) < 1e-10

    def test_T12_manifold(self, c11):
        b3 = c11["blocks"]["B3_T12_manifold"]
        assert b3["ok"] is True
        assert b3["launch_ok"] is True
        assert b3["invariants_drift_max"] < 1e-10
        assert b3["r_max"] < 12.0
        assert b3["r_max"] == pytest.approx(2.765423, abs=1e-4)
        assert b3["rigid"] is False

    def test_T13_V_star(self, c11):
        b4 = c11["blocks"]["B4_T13_barrier"]
        assert b4["V_star"] == pytest.approx(0.9359375, rel=1e-9)
        assert b4["cells"][-1]["escape_exactly_impossible"] is True

    def test_T13_static_cells(self, c11):
        b4 = c11["blocks"]["B4_T13_barrier"]
        assert b4["ok"] is True
        for c in b4["cells"]:
            assert c["P_esc"] == 0.0
            assert c["n_escaped"] == 0
            assert c["bound_violation_max"] < 1e-3
            assert c["E_drift_abs_max"] < 1e-4
        assert min(c["bound_margin_min"] for c in b4["cells"]) > 2.0

    def test_T13_oscillating_complement(self, c11):
        w = c11["blocks"]["B4_T13_barrier"]["oscillating_complement"]
        assert w["median_abs_dE"] > 0.01
        assert "finite-time" in w["note"]

    def test_all_gates_pass(self, c11):
        for k, v in c11["gates"].items():
            assert v is True, (k, v)
