# -*- coding: utf-8 -*-
import json
import math
import os

import pytest

REF = os.path.join(os.path.dirname(__file__), "..", "campaigns", "reference")


def load(name):
    with open(os.path.join(REF, name), encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def c1():
    return load("c1_verdict.json")


@pytest.fixture(scope="module")
def c2():
    return load("c2_verdict.json")


@pytest.fixture(scope="module")
def c3():
    return load("c3_verdict.json")


@pytest.fixture(scope="module")
def c4():
    return load("c4_verdict.json")


@pytest.fixture(scope="module")
def c5():
    return load("c5_verdict.json")


@pytest.fixture(scope="module")
def c6():
    return load("c6_verdict.json")


@pytest.fixture(scope="module")
def c7():
    return load("c7_verdict.json")


@pytest.fixture(scope="module")
def c8():
    return load("c8_verdict.json")


class TestC1:
    def test_static_gap(self, c1):
        assert c1["static"]["Delta0"] == pytest.approx(0.523004556028, abs=1e-11)

    def test_response(self, c1):
        assert c1["static"]["s_dDelta_dqpk"] == pytest.approx(-1.00398294,
                                                              abs=1e-7)

    def test_B2_quadratic_law(self, c1):
        assert c1["window"]["B2"] == pytest.approx(-5.49670294e-2, rel=1e-6)
        assert c1["window"]["r2"] > 0.9999998

    def test_sector_hierarchy(self, c1):
        ps = c1["per_sector"]
        assert abs(ps["B2_A_pi2"]) > abs(ps["B2_B_pi3"]) > abs(ps["B2_C_pi7"])

    def test_T2_exact_checks(self, c1):
        t2 = c1["theorem_T2"]
        assert t2["b_flip_evenness_dev"] < 1e-12
        assert t2["a_only_all_order_dev"] < 1e-12
        assert t2["b0_identity_dev"] < 1e-12

    def test_verdicts_pass(self, c1):
        for k, v in c1["verdicts"].items():
            if k == "T2_a_flip_residual":
                continue          # reported-as-data, not a pass/fail verdict
            assert v == "PASS", (k, v)


class TestC2:
    def test_gascheau(self, c2):
        assert c2["gascheau"]["nu"] == pytest.approx(1.0 / 3.0)
        assert c2["gascheau"]["stable"] is False

    def test_free_negative(self, c2):
        p = c2["T5_free_negative"]["P_esc_free"]
        assert 0.15 < p < 0.35          # honest negative, committed window

    def test_trap_seals(self, c2):
        sealed = [g for g in c2["grid"] if g["V0"] >= 0.4]
        assert all(g["P_esc"] < 1e-4 for g in sealed)

    def test_bound_chaos(self, c2):
        lam_f = c2["lyapunov"]["free"]["median"]
        lam_t = c2["lyapunov"]["trap_V08_Om2"]["median"]
        assert lam_f > 0.1 and lam_t > 0.1


class TestC3:
    def test_max_dev(self, c3):
        assert c3["max_dev_formula_vs_mc"] < 5e-3

    def test_anchor(self, c3):
        assert c3["anchor"]["r_at_anchor"] == pytest.approx(0.899996,
                                                            abs=1e-4)

    def test_eta_honest_scope(self, c3):
        x = c3["eta_comparison"]["x_required_for_eta"]
        assert 1e-10 < x < 1e-6


class TestC4:
    def test_reference_gap(self, c4):
        assert c4["detector"]["reference_gap"] == pytest.approx(
            0.5093674355, abs=1e-8)

    def test_unresolved_tail(self, c4):
        assert c4["verdicts"]["T9_unresolved_tail"] == "CONFIRMED"
        assert c4["rows"][0]["beats_in_window"] < 3

    def test_envelope(self, c4):
        assert c4["floor_law"]["envelope_holds_on_resolved"] is True


class TestC5:
    def test_p_eff_climbing(self, c5):
        ps = [p["p"] for p in c5["p_eff"]]
        assert ps[0] > 1.9 and ps[-1] < 2.0

    def test_exact_channel(self, c5):
        assert c5["exact_channel"]["C_exact_s_kappa_over_8"] == pytest.approx(
            -6.2749e-3, rel=1e-3)
        assert c5["exact_channel"]["share_of_measured"] < 0

    def test_lemmaA_machine(self, c5):
        assert c5["lemma_A_machine_check"]["ok"] is True

    def test_continuum_not_claimed(self, c5):
        assert "NOT CLAIMED" in c5["fit"]["Delta_cont_status"]


class TestC6:
    def test_three_branches_present(self, c6):
        names = [b["name"] for b in c6["branches"]]
        assert names == ["Lambda_QCD", "QCD_crossover", "electroweak"]

    def test_qcd_contact_matches_T8(self, c6):
        qcd = next(b for b in c6["branches"]
                   if b["name"] == "QCD_crossover")
        assert qcd["M_contact_kg"] == pytest.approx(6.8140e10, rel=1e-4)

    def test_gap_quantum_order_window(self, c6):
        g = c6["gates"]["G4_order_window"]
        assert 1.0 < g["Lambda_over_E_gap_QCD"] < 10.0
        assert g["ok"] is True

    def test_all_gates_pass(self, c6):
        assert all(g["ok"] for g in c6["gates"].values())

    def test_honesty_notes_carried(self, c6):
        assert len(c6["honest_notes"]) >= 4
        assert all("honesty" in b for b in c6["branches"])


class TestC7:
    def test_regression_gate_exact(self, c7):
        g = c7["regression_gate"]
        assert g["ok"] is True and g["dev"] == 0.0

    def test_free_ladder_monotone(self, c7):
        assert c7["L1_leakage_law"]["monotone_nonincreasing"] is True
        assert c7["L1_leakage_law"]["sigma_star_P05"] == pytest.approx(0.05)

    def test_boundary_shrinks(self, c7):
        f = c7["L2_boundary_collapse"]["shrink_factors_Om0_to_Om2"]
        assert len(f) == 2 and all(v >= 2.0 for v in f.values())

    def test_bound_chaos_without_wall(self, c7):
        b = c7["L3_bound_chaos"]
        assert b["median"] > 0.1 and b["share_positive"] > 0.99


class TestC8:
    def test_exact_no_door(self, c8):
        x = c8["X1_no_door_exact"]
        assert x["ok"] is True and x["r"] == 0.0

    def test_rk4_order(self, c8):
        assert abs(c8["convergence"]["p_eff"] - 4.0) < 0.05

    def test_mpmath_crosscheck(self, c8):
        assert c8["mpmath_anchor"]["ok"] is True
        assert c8["mpmath_anchor"]["dev"] < 1e-9

    def test_door_stays_shape_moves(self, c8):
        assert c8["door_stays"]["ok"] is True
        assert c8["shape_moves"]["ok"] is True
        r = c8["shape_moves"]["r_pair_at_lambda_100_alpha_09"]
        assert r > 0.95                     # the full-imbalance climb

    def test_T7_extension_negative(self, c8):
        assert "NEGATIVE" in c8["verdicts"]["T7_extension"]
