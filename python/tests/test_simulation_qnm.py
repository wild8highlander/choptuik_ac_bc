"""Tests for simulation, QNM, hypothesis, and geometry modules.

Covers the modules that were previously untested:
- src/simulation/simulator.py  (Simulator)
- src/core/qnm.py              (QNMPredictor: shift, detectability, serialization)
- src/core/spinor_phases.py    (64-structure enumeration, distribution)
- src/core/klein_curve.py      (PSL(2,7) generators and relations)
- src/core/hypothesis.py       (HypothesisTester)
- src/core/surfaces.py         (surface specs)

All reference values come from the monograph by Ishak Khamzatovich Isaev.
"""

import numpy as np
import pytest
from src.core.hypothesis import HypothesisConfig, HypothesisTester
from src.core.klein_curve import KleinCurve
from src.core.qnm import DEFAULT_EVENTS, BHEvent, QNMPredictor
from src.core.spinor_phases import SpinorPhases
from src.core.surfaces import BOLZA, BRING, MACBEATH, SurfaceSpec
from src.simulation.simulator import Simulator


# ──────────────────────────────────────────────
# Simulator (sweeps + convergence)
# ──────────────────────────────────────────────
class TestSimulator:
    """Tests for the parameter-sweep simulation engine."""

    def test_sweep_delta_c_shapes(self):
        sim = Simulator()
        res = sim.sweep_delta_C(n_points=50)
        assert len(res["delta_C"]) == 50
        assert len(res["delta_bc"]) == 50
        assert len(res["delta_ch_base"]) == 50
        assert len(res["delta_ch_full"]) == 50
        assert len(res["deviation_pct"]) == 50

    def test_sweep_delta_c_values_at_reference(self):
        sim = Simulator()
        res = sim.sweep_delta_C(n_points=200)
        dC = np.pi / 7
        lam = 3.338
        # The engine evaluates the same formula on its grid; verify at the
        # nearest grid point to the reference delta_C
        grid = np.asarray(res["delta_C"])
        idx = int(np.argmin(np.abs(grid - dC)))
        d = grid[idx]
        expected_full = lam + d**2 / 2 - d**5 / 22 + 0.125 * d**4 + 0.5 * d**6
        assert res["delta_ch_full"][idx] == pytest.approx(expected_full, abs=1e-9)
        expected_base = lam + d**2 / 2 - d**5 / 22
        assert res["delta_ch_base"][idx] == pytest.approx(expected_base, abs=1e-9)

    def test_sweep_delta_c_optimal_near_reference(self):
        sim = Simulator()
        res = sim.sweep_delta_C(n_points=2000)
        # |f(dC) - 3.443| vanishes between 0.44 and 0.446, near pi/7 = 0.4488
        assert 0.43 < res["optimal_delta_C"] < 0.46
        assert res["min_deviation_pct"] < 0.2

    def test_sweep_lambda_1_optimal_near_reference(self):
        sim = Simulator()
        res = sim.sweep_lambda_1(n_points=2000)
        assert res["optimal_lambda_1"] == pytest.approx(3.838, abs=5e-3)

    def test_convergence_analysis_order6(self):
        sim = Simulator()
        res = sim.convergence_analysis(max_order=6)
        sums = res["partial_sums"]
        assert [p["order"] for p in sums] == [1, 2, 3, 4, 5, 6]
        # After order 6 the full formula value must match the monograph reference
        full = sums[-1]["value"]
        assert full == pytest.approx(3.447040, abs=1e-5)

    def test_convergence_series_stabilizes(self):
        sim = Simulator()
        res = sim.convergence_analysis(max_order=10)
        vals = [p["value"] for p in res["partial_sums"]]
        # No corrections beyond order 6 -> value must stay constant
        assert len(set(vals[6:])) == 1

    def test_results_and_logs_populated(self):
        sim = Simulator()
        sim.sweep_delta_C(n_points=10)
        sim.convergence_analysis(max_order=2)
        assert "sweep_delta_C" in sim.results
        assert "convergence" in sim.results
        assert sim.get_logs()  # non-empty log


# ──────────────────────────────────────────────
# QNMPredictor (enhanced + shift predictions)
# ──────────────────────────────────────────────
class TestQNMPredictorFull:
    """Tests for QNM predictions and serialization."""

    def test_default_events_loaded(self):
        pred = QNMPredictor()
        assert len(pred.events) == 4
        assert [e.name for e in pred.events] == [
            "GW150914",
            "GW170104",
            "GW170814",
            "GW190521",
        ]

    def test_qnm_correction_value(self):
        pred = QNMPredictor()
        delta_eff = (np.pi / 7) ** 5 / 22
        assert pred.qnm_correction == pytest.approx(delta_eff / np.pi**2)
        assert pred.qnm_factor == pytest.approx(1 - delta_eff / np.pi**2)
        # README reference: factor ~ 0.999916
        assert pred.qnm_factor == pytest.approx(0.999916, abs=1e-6)

    def test_corrected_frequency_reduces_value(self):
        pred = QNMPredictor()
        assert pred.corrected_frequency(251.0) < 251.0
        assert pred.corrected_frequency(251.0) == pytest.approx(
            251.0 * pred.qnm_factor, abs=1e-9
        )

    def test_predict_shift_formula(self):
        pred = QNMPredictor()
        res = pred.predict_shift(DEFAULT_EVENTS[0], scaling=14.0)
        ev = DEFAULT_EVENTS[0]
        assert res["delta_f"] == pytest.approx(ev.f_qnm / 14.0 * ev.spin**2)
        assert res["snr"] == pytest.approx(res["delta_f"] / ev.sigma)

    def test_predict_all_count(self):
        pred = QNMPredictor()
        assert len(pred.predict_all()) == 4

    def test_detectability_structure(self):
        pred = QNMPredictor()
        rows = pred.detectability("GW150914")
        assert len(rows) == len(pred.detectors)
        for row, det in zip(rows, pred.detectors, strict=True):
            assert row["detector"] == det["name"]
            snr = (251.0 / 14.0 * 0.67**2) / det["sigma_hz"]
            assert row["snr"] == pytest.approx(snr)
            assert row["detectable"] == (snr >= 1.0)

    def test_detectability_unknown_event_falls_back(self):
        pred = QNMPredictor()
        rows = pred.detectability("UNKNOWN_EVENT")
        assert len(rows) == len(pred.detectors)

    def test_as_dict_roundtrip(self):
        pred = QNMPredictor()
        d = pred.as_dict()
        assert d["n_events"] == 4
        assert d["events"][0]["name"] == "GW150914"
        assert d["events"][0]["M"] == 62.0

    def test_custom_event(self):
        ev = BHEvent("TEST", 10.0, 0.5, 100.0, 1.0)
        pred = QNMPredictor(events=[ev], detectors=[{"name": "D", "sigma_hz": 0.5}])
        res = pred.predict_shift(ev)
        assert res["delta_f"] == pytest.approx(100.0 / 14.0 * 0.25)


# ──────────────────────────────────────────────
# Spinor structure enumeration
# ──────────────────────────────────────────────
class TestSpinorEnumeration:
    """Tests for the 64 spinor structure enumeration."""

    def test_enumerate_count(self):
        sp = SpinorPhases()
        structs = sp.enumerate_structures(lambda_D2_triv=3.338)
        assert len(structs) == 64

    def test_trivial_structure_is_baseline(self):
        sp = SpinorPhases()
        structs = sp.enumerate_structures(lambda_D2_triv=3.338)
        trivial = [s for s in structs if s.n_active == 0]
        assert len(trivial) == 1
        assert trivial[0].Delta == pytest.approx(3.338)

    def test_deviation_sorting_ascending(self):
        sp = SpinorPhases()
        structs = sp.enumerate_structures(lambda_D2_triv=3.338)
        devs = [s.deviation for s in structs]
        assert devs == sorted(devs)

    def test_distribution_counts_sum_to_64(self):
        sp = SpinorPhases()
        structs = sp.enumerate_structures(lambda_D2_triv=3.338)
        dist = sp.distribution(structs)
        total = sum(v["count"] for v in dist.values())
        assert total == 64
        # C(6, n) binomial counts
        assert dist[0]["count"] == 1
        assert dist[1]["count"] == 6
        assert dist[6]["count"] == 1

    def test_distribution_avg_delta(self):
        sp = SpinorPhases()
        structs = sp.enumerate_structures(lambda_D2_triv=3.338)
        dist = sp.distribution(structs)
        dC = np.pi / 7
        assert dist[1]["avg_Delta"] == pytest.approx(3.338 + dC**2 / 2)
        assert dist[2]["avg_Delta"] == pytest.approx(3.338 + dC**2)

    def test_as_dict(self):
        sp = SpinorPhases()
        d = sp.as_dict()
        assert d["delta_A"] == pytest.approx(np.pi / 2)
        assert d["delta_B"] == pytest.approx(np.pi / 3)
        assert d["delta_C"] == pytest.approx(np.pi / 7)

    def test_custom_phases(self):
        sp = SpinorPhases(delta_A=1.0, delta_B=2.0, delta_C=3.0)
        assert sp.delta_A == 1.0
        assert sp.delta_B == 2.0
        assert sp.delta_C == 3.0


# ──────────────────────────────────────────────
# Klein curve generators
# ──────────────────────────────────────────────
class TestKleinGenerators:
    """Tests for the Gamma(2,3,7) generators in SL(2,R)."""

    def test_generator_orders(self):
        kc = KleinCurve()
        A, B, C = kc.generators()
        nI = -np.eye(2)
        assert np.allclose(A @ A, nI), "A^2 = -I"
        assert np.allclose(np.linalg.matrix_power(B, 3), nI), "B^3 = -I"
        assert np.allclose(np.linalg.matrix_power(C, 7), np.eye(2)), "C^7 = I"

    def test_verify_relations_flags(self):
        kc = KleinCurve()
        A, B, C = kc.generators()
        res = kc.verify_relations(A, B, C)
        assert res["A_sq_eq_negI"] is True
        assert res["B_cub_eq_negI"] is True
        assert res["C_sev_eq_I"] is True
        for key in ("A_sq_norm", "B_cub_norm", "C_sev_norm"):
            assert res[key] < 1e-9

    def test_gauss_bonnet_area(self):
        kc = KleinCurve()
        assert kc.area == pytest.approx(8 * np.pi)
        assert pytest.approx(-2.0) == kc.R

    def test_as_dict(self):
        kc = KleinCurve()
        d = kc.as_dict()
        assert d["genus"] == 3
        assert d["psl_order"] == 168
        assert d["sl_order"] == 336


# ──────────────────────────────────────────────
# HypothesisTester
# ──────────────────────────────────────────────
class TestHypothesisTester:
    """Tests for the custom hypothesis framework."""

    def test_default_configuration_passes(self):
        tester = HypothesisTester()
        result = tester.test_hypothesis(HypothesisConfig(name="canon"))
        assert result.delta_C == pytest.approx(np.pi / 7)
        assert result.delta_bc == pytest.approx(3.438710, abs=1e-5)
        assert result.delta_ch_base == pytest.approx(3.437883, abs=1e-5)
        assert result.delta_ch_full == pytest.approx(3.447040, abs=1e-5)
        assert result.passed is True

    def test_custom_parameters_change_result(self):
        tester = HypothesisTester()
        result = tester.test_hypothesis(
            HypothesisConfig(name="custom", custom_delta_C=0.5, custom_k_struct=10)
        )
        assert result.delta_C == pytest.approx(0.5)
        assert result.delta_bc != pytest.approx(3.438710, abs=1e-3)

    def test_tolerance_rejects_far_hypothesis(self):
        strict = HypothesisTester(tolerance=1e-9)
        result = strict.test_hypothesis(
            HypothesisConfig(name="far", custom_delta_C=0.1)
        )
        assert result.passed is False

    def test_custom_correction_fn(self):
        tester = HypothesisTester()
        dC_ref = np.pi / 7
        cfg = HypothesisConfig(
            name="plus1",
            custom_correction_fn=lambda dC, lam_D2, k: (
                lam_D2 + dC**2 / 2 - dC**5 / k + 0.125 * dC**4 + 0.5 * dC**6 + 1.0
            ),
        )
        result = tester.test_hypothesis(cfg)
        # Custom correction shifts the canonical full value by exactly 1
        assert result.delta_ch_full == pytest.approx(3.447040 + 1.0, abs=1e-5)
        assert result.delta_C == pytest.approx(dC_ref)


# ──────────────────────────────────────────────
# Surface specs
# ──────────────────────────────────────────────
class TestSurfaces:
    """Sanity tests for comparative surface specs."""

    def test_bolza_spec(self):
        assert isinstance(BOLZA, SurfaceSpec)
        assert BOLZA.genus == 2
        assert BOLZA.group_order == 48

    def test_predefined_surfaces(self):
        assert [s.name for s in (BOLZA, BRING, MACBEATH)] == [
            "Bolza",
            "Bring",
            "Macbeath",
        ]

    def test_compute_choptyuk_values(self):
        # lambda_D2 = 3.838 - 0.5 = 3.338 for the Klein-like parameters
        spec = SurfaceSpec(
            name="Klein-like",
            lambda_1=3.838,
            delta_max=np.pi / 7,
            group_name="PSL(2,7)",
            group_order=168,
            R=-2.0,
            genus=3,
        )
        res = spec.compute()
        assert res["lambda_D2"] == pytest.approx(3.338)
        assert res["delta_bc"] == pytest.approx(3.438710, abs=1e-5)
        assert res["delta_ch"] == pytest.approx(3.437883, abs=1e-5)
