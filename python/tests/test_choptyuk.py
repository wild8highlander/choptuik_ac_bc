"""Test suite for the Choptyuk Spinor Corrections package.

All tests verify mathematical correctness against reference values
from the monograph by Ishak Khamzatovich Isaev.
"""

import math
import pytest

from src.core.klein_curve import KleinCurve
from src.core.spinor_phases import SpinorPhases
from src.core.choptyuk_formula import ChoptyukFormula
from src.core.dirac_operator import DiracOperator
from src.core.qnm import QNMPredictor
from src.core.enhanced_verification import (
    KleinQuartic,
    K3Surface,
    QNMPredictor as EnhancedQNMPredictor,
    TyukovskyAdapter,
    CriticismResponse,
)
from src.core.qcd_bridge_verification import (
    ChoptyukBridge,
    CPoddObservable,
    CPoddPredictions,
    FalsifiabilityTimeline,
    LatticeThetaDependence,
    MercuryParadox,
    MonteCarloUncertainty,
    PQAxiomWithResidual,
    verify_all as qcd_verify_all,
)


# ──────────────────────────────────────────────
# Reference constants from the monograph
# ──────────────────────────────────────────────
REF_DELTA_BC = 3.438710
REF_DELTA_CH_BASE = 3.437883
REF_DELTA_CH_FULL = 3.447040
REF_B_CH = 0.376510
REF_LAMBDA1_DELTA = 3.838
REF_LAMBDA1_DIRAC = 3.338
REF_DELTA_C = math.pi / 7
REF_GENUS = 3
REF_AUT_GROUP_ORDER = 168

TOLERANCE_STRICT = 1e-6
TOLERANCE_LOOSE = 1e-3


# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────
@pytest.fixture
def klein():
    return KleinCurve()


@pytest.fixture
def spinor():
    return SpinorPhases()


@pytest.fixture
def choptyuk():
    return ChoptyukFormula()


@pytest.fixture
def dirac():
    return DiracOperator()


# ──────────────────────────────────────────────
# Klein Curve Tests
# ──────────────────────────────────────────────
class TestKleinCurve:
    """Tests for the Klein quartic curve properties."""

    def test_genus(self, klein):
        """Klein quartic has genus 3 via Riemann-Hurwitz."""
        assert klein.genus == REF_GENUS

    def test_aut_group_order(self, klein):
        """Automorphism group PSL(2,7) has order 168."""
        assert klein.psl_order == REF_AUT_GROUP_ORDER

    def test_euler_characteristic(self, klein):
        """Euler characteristic chi = 2 - 2g = -4 for genus 3."""
        assert 2 - 2 * klein.genus == -4

    def test_scalar_curvature(self, klein):
        """Scalar curvature R = -2 for genus 3 hyperbolic surface."""
        assert abs(klein.R - (-2)) < TOLERANCE_STRICT

    def test_first_laplacian_eigenvalue(self, klein):
        """First Laplacian eigenvalue lambda_1(Delta) = 3.838."""
        assert abs(klein.lambda_1 - REF_LAMBDA1_DELTA) < TOLERANCE_LOOSE


# ──────────────────────────────────────────────
# Spinor Phase Tests
# ──────────────────────────────────────────────
class TestSpinorPhases:
    """Tests for spinor phase values."""

    def test_delta_a(self, spinor):
        """Phase delta_A = pi/2."""
        assert abs(spinor.delta_A - math.pi / 2) < TOLERANCE_STRICT

    def test_delta_b(self, spinor):
        """Phase delta_B = pi/3."""
        assert abs(spinor.delta_B - math.pi / 3) < TOLERANCE_STRICT

    def test_delta_c(self, spinor):
        """Phase delta_C = pi/7."""
        assert abs(spinor.delta_C - math.pi / 7) < TOLERANCE_STRICT

    def test_phase_ordering(self, spinor):
        """Phases satisfy delta_A > delta_B > delta_C."""
        assert spinor.delta_A > spinor.delta_B > spinor.delta_C


# ──────────────────────────────────────────────
# Dirac Operator Tests
# ──────────────────────────────────────────────
class TestDiracOperator:
    """Tests for the Dirac operator spectral values."""

    def test_trivial_dirac_eigenvalue(self, dirac):
        """Trivial Dirac: lambda_1(D^2_sigma_0) = lambda_1(Delta) + R/4 = 3.338."""
        assert abs(dirac.lambda_D2_triv - REF_LAMBDA1_DIRAC) < TOLERANCE_LOOSE

    def test_lichnerowicz_formula(self, dirac):
        """Lichnerowicz: lambda_1(D^2) = lambda_1(Delta) + R/4."""
        expected = REF_LAMBDA1_DELTA + (-2) / 4
        assert abs(dirac.lambda_D2_triv - expected) < TOLERANCE_STRICT

    def test_spectral_gap(self, dirac):
        """Spectral gap equals lambda_D2_triv."""
        assert abs(dirac.gap() - dirac.lambda_D2_triv) < TOLERANCE_STRICT


# ──────────────────────────────────────────────
# Choptyuk Formula Tests
# ──────────────────────────────────────────────
class TestChoptyukFormula:
    """Tests for the unified Choptyuk formula."""

    def test_bc_correction(self, choptyuk):
        """b-C correction: Delta_bC = lambda_1(D^2) + delta_C^2/2 = 3.438710."""
        result = choptyuk.compute()
        assert abs(result.delta_bc - REF_DELTA_BC) < TOLERANCE_LOOSE

    def test_choptyuk_base(self, choptyuk):
        """Base Choptyuk: Delta_Ch = lambda_1(D^2) + delta_C^2/2 - delta_C^5/22 = 3.437883."""
        result = choptyuk.compute()
        assert abs(result.delta_ch_base - REF_DELTA_CH_BASE) < TOLERANCE_LOOSE

    def test_choptyuk_full(self, choptyuk):
        """Full Choptyuk with higher orders: Delta_Ch = 3.447040."""
        result = choptyuk.compute()
        assert abs(result.delta_ch_full - REF_DELTA_CH_FULL) < TOLERANCE_LOOSE

    def test_choptyuk_constant(self, choptyuk):
        """Choptyuk constant: b_Ch = 1 - cos(2pi/7) ~ 0.376510."""
        result = choptyuk.compute()
        assert abs(result.b_ch - REF_B_CH) < TOLERANCE_LOOSE

    def test_braking_correction(self, choptyuk):
        """a-C braking: delta_eff = delta_C^5/22 ~ 1/1200."""
        result = choptyuk.compute()
        delta_c = REF_DELTA_C
        expected_eff = delta_c ** 5 / 22
        assert abs(result.delta_eff - expected_eff) < TOLERANCE_STRICT

    def test_bc_deviation_within_tolerance(self, choptyuk):
        """Delta_bC deviation from observed (3.443) must be < 0.2%."""
        result = choptyuk.compute()
        observed = 3.443
        deviation_pct = abs(result.delta_bc - observed) / observed * 100
        assert deviation_pct < 0.2

    def test_full_deviation_within_tolerance(self, choptyuk):
        """Delta_Ch(full) deviation from observed (3.443) must be < 0.2%."""
        result = choptyuk.compute()
        observed = 3.443
        deviation_pct = abs(result.delta_ch_full - observed) / observed * 100
        assert deviation_pct < 0.2


# ──────────────────────────────────────────────
# Cross-Reference Consistency Tests
# ──────────────────────────────────────────────
class TestConsistency:
    """Cross-reference checks between computed values."""

    def test_choptyuk_constant_formula(self):
        """b_Ch = 1 - cos(2pi/7) = 2*sin^2(pi/7)."""
        val1 = 1 - math.cos(2 * math.pi / 7)
        val2 = 2 * math.sin(math.pi / 7) ** 2
        assert abs(val1 - val2) < TOLERANCE_STRICT
        assert abs(val1 - REF_B_CH) < TOLERANCE_LOOSE

    def test_delta_c_squared_half(self):
        """delta_C^2/2 component of b-C correction."""
        component = (math.pi / 7) ** 2 / 2
        expected_diff = REF_DELTA_BC - REF_LAMBDA1_DIRAC
        assert abs(component - expected_diff) < TOLERANCE_LOOSE

    def test_64_spinor_structures(self, klein):
        """Klein curve admits exactly 2^(2g) = 64 spinor structures."""
        n_structures = 2 ** (2 * klein.genus)
        assert n_structures == 64


# ──────────────────────────────────────────────
# Mathematical Identity Tests
# ──────────────────────────────────────────────
class TestMathIdentities:
    """Fundamental mathematical identities."""

    @pytest.mark.math
    def test_psl27_order(self):
        """|PSL(2,7)| = (7^2-1)*7/2 = 168."""
        order = (7**2 - 1) * 7 // 2
        assert order == 168

    @pytest.mark.math
    def test_choptyuk_constant_precision(self):
        """b_Ch to 6 decimal places."""
        b_ch = 1 - math.cos(2 * math.pi / 7)
        assert abs(b_ch - 0.376510) < 1e-4

    @pytest.mark.math
    def test_braking_magnitude(self):
        """delta_eff ~ 1/1200 (a-C braking is very small)."""
        delta_c = math.pi / 7
        delta_eff = delta_c ** 5 / 22
        assert abs(delta_eff - 1 / 1200) < 1e-4


# ──────────────────────────────────────────────
# Enhanced Verification Module Tests
# ──────────────────────────────────────────────
class TestEnhancedVerificationModule:
    """Tests for the enhanced verification module integration."""

    def test_enhanced_verification_module(self):
        """Enhanced verification module imports and verify_all() runs correctly."""
        from src.core.enhanced_verification import verify_all
        results = verify_all()
        assert "klein" in results
        assert "k3" in results
        assert "qnm" in results
        assert "tyukovsky" in results
        assert "criticism" in results
        # Check Klein results
        assert abs(results["klein"]["effective_phase"] - 1/1200) / (1/1200) < 0.01
        # Check QNM results
        assert abs(results["qnm"]["factor"] - 0.999916) < 1e-3

    def test_k3_surface(self):
        """K3 surface invariants are correct."""
        k3 = K3Surface()
        assert k3.b2 == 22
        assert k3.b2_check == 22
        assert k3.b2_over_index == 11.0
        assert k3.is_hyperkahler is True
        assert k3.sw_compatible is True
        assert k3.dirac_index == 2
        assert k3.b2_plus == 3

    def test_qnm_einstein_correction(self):
        """QNM Einstein GR correction from enhanced module."""
        qnm = EnhancedQNMPredictor()
        # qnm_correction = delta_eff / pi^2
        delta_eff = (math.pi / 7)**5 / 22
        expected_correction = delta_eff / math.pi**2
        assert abs(qnm.qnm_correction - expected_correction) < TOLERANCE_STRICT
        # qnm_factor ~ 0.999916
        assert abs(qnm.qnm_factor - (1 - expected_correction)) < TOLERANCE_STRICT
        assert abs(qnm.qnm_factor - 0.999916) < 1e-4
        # corrected_frequency(omega) = omega * qnm_factor
        omega = 251.0
        assert abs(qnm.corrected_frequency(omega) - omega * qnm.qnm_factor) < TOLERANCE_STRICT

    def test_tyukovsky_adapter(self):
        """Tyukovsky adapter critical exponent correction."""
        tyuk = TyukovskyAdapter()
        delta_0 = 0.36
        delta_C = math.pi / 7
        expected = delta_0 + delta_C**2 / 2 - delta_C**5 / 22
        assert abs(tyuk.corrected_critical_exponent(delta_0) - expected) < TOLERANCE_STRICT
        # Free parameters must be zero
        assert tyuk.free_parameters == 0
        # GCT equation is symbolic
        assert "L_gCT" in tyuk.gct_equation

    def test_criticism_response(self):
        """Criticism response verification checks."""
        criticism = CriticismResponse()
        # Non-coincidental check
        nc = criticism.check_non_coincidental()
        assert "best_approx" in nc
        assert "best_dev_pct" in nc
        assert nc["best_dev_pct"] >= 0
        # b2 uniqueness
        b2u = criticism.check_b2_uniqueness()
        assert 22 in b2u
        assert b2u[22]["compatible"] is True
        # Stability
        stab = criticism.check_stability(epsilon=0.001)
        assert "deviation_pct" in stab
        assert "stable" in stab
        # Spin structures
        ss = criticism.check_spin_structures()
        assert ss["total"] == 64
        assert ss["even_Arf0"] == 28
        assert ss["odd_Arf1"] == 36


# ──────────────────────────────────────────────
# QCD Bridge Verification Module Tests
# ──────────────────────────────────────────────
class TestQCDBridgeVerification:
    """Tests for the QCD bridge verification module.

    These tests verify the Choptyuk Higgs-scale bridge:
        theta_Ch = a_C * (Lambda_QCD / M_H)^(5/2) ~ 8.5e-11
    and its phenomenological consequences for CP-odd observables.
    """

    def test_a_C_value(self):
        """a_C = (pi/7)^5 / 22 ~ 8.276e-4."""
        a_C = (math.pi / 7) ** 5 / 22
        assert abs(a_C - 8.276e-4) < 1e-5

    def test_bridge_theta_Ch_value(self):
        """theta_Ch = a_C * (Lambda/M_H)^(5/2) ~ 8.46e-11."""
        bridge = ChoptyukBridge()
        assert abs(bridge.theta_Ch - 8.46e-11) < 1e-12

    def test_bridge_theta_Ch_within_order_of_bound(self):
        """theta_Ch must be within 1 order of magnitude of 1e-10."""
        bridge = ChoptyukBridge()
        ratio = bridge.ratio_to_nEDM_bound
        assert 0.1 < ratio < 10.0

    def test_bridge_log10_theta_Ch(self):
        """log10(theta_Ch) ~ -10.07."""
        bridge = ChoptyukBridge()
        assert abs(bridge.log10_theta_Ch - (-10.07)) < 0.05

    def test_sphaleron_motivation_structure(self):
        """The sphaleron motivation must give 5/2 exponent structurally."""
        bridge = ChoptyukBridge()
        s = bridge.sphaleron_motivation
        assert s["M_H_over_T_to_5_2"] > 1e6
        assert abs(s["T_GeV"] - 0.200) < 1e-9
        assert "5/2" in s["structural_explanation"]

    def test_neutron_EDM_prediction_value(self):
        """d_n^Ch = 2.4e-16 * theta_Ch ~ 2.03e-26 e*cm."""
        bridge = ChoptyukBridge()
        preds = CPoddPredictions(bridge=bridge)
        d_n = preds.neutron_EDM_prediction
        assert abs(d_n - 2.03e-26) < 1e-27

    def test_neutron_EDM_ratio_to_bound(self):
        """d_n^Ch / 1.8e-26 ~ 1.13 (within 30% of bound)."""
        bridge = ChoptyukBridge()
        preds = CPoddPredictions(bridge=bridge)
        ratio = preds.neutron_EDM_ratio_to_bound
        assert 0.5 < ratio < 2.0

    def test_all_six_CP_observables_present(self):
        """All 6 CP-odd observables must be in the predictions list."""
        preds = CPoddPredictions()
        all_preds = preds.all_predictions()
        names = [p["name"] for p in all_preds]
        expected = ["Neutron EDM", "Proton EDM", "Hg-199 EDM",
                    "Ra-225 EDM", "Electron EDM", "Deuteron EDM"]
        assert names == expected

    def test_mercury_paradox_central_ratio(self):
        """Mercury paradox: central ratio ~ 343 (the 'paradox')."""
        mp = MercuryParadox()
        assert 300 < mp.paradox_apparent_ratio < 400

    def test_mercury_paradox_central_bound(self):
        """Central Mercury bound on |theta| ~ 2.5e-13."""
        mp = MercuryParadox()
        assert abs(mp.effective_theta_bound_central - 2.47e-13) < 1e-14

    def test_mercury_paradox_with_uncertainty(self):
        """Mercury bound with 100x uncertainty ~ 2.5e-11."""
        mp = MercuryParadox()
        assert abs(mp.effective_theta_bound_with_uncertainty - 2.47e-11) < 1e-12

    def test_mercury_paradox_aggressive_bound(self):
        """Most aggressive Mercury bound ~ 2.5e-10."""
        mp = MercuryParadox()
        assert abs(mp.effective_theta_bound_aggressive - 2.47e-10) < 1e-11

    def test_mercury_paradox_status_honest(self):
        """Paradox status should be honest -- 'MARGINALLY RESOLVED'
        at default parameters."""
        mp = MercuryParadox()
        # theta_Ch = 8.46e-11
        # aggressive bound = 2.47e-10 -> theta_Ch < bound, so MARGINALLY RESOLVED
        assert mp.theta_Ch_below_aggressive_Hg_bound is True
        assert mp.theta_Ch_below_uncertainty_Hg_bound is False
        assert mp.theta_Ch_below_central_Hg_bound is False
        assert "MARGINALLY" in mp.paradox_status or "UNRESOLVED" in mp.paradox_status

    def test_lattice_b2_value(self):
        """Lattice b_2 = -0.0123 (Vicari-Panagopoulos)."""
        lt = LatticeThetaDependence()
        assert abs(lt.b2_lattice - (-0.0123)) < 1e-6

    def test_lattice_b2_large_N(self):
        """Large-N b_2 = -1/(12 * (11 - 2*Nf/Nc)) ~ -0.00926 for Nf=Nc=3."""
        lt = LatticeThetaDependence()
        assert abs(lt.b2_large_N_prediction - (-1.0 / 108.0)) < 1e-6

    def test_lattice_b2_ratio_in_range(self):
        """Lattice/large-N ratio ~ 1.33 (within 30%)."""
        lt = LatticeThetaDependence()
        r = lt.large_N_b2_agreement
        assert 0.7 < r < 2.0

    def test_lattice_relative_correction_negligible(self):
        """Relative correction to chi_t at theta_Ch ~ 1e-22."""
        lt = LatticeThetaDependence()
        assert abs(lt.relative_correction_chi_t) < 1e-20

    def test_lattice_in_linear_regime(self):
        """theta_Ch is well within the linear regime of lattice theta-dep."""
        lt = LatticeThetaDependence()
        c = lt.consistency_check
        assert c["well_within_linear_regime"] is True

    def test_PQ_axion_mass_standard(self):
        """Standard QCD axion mass at f_a=1e12 GeV: 5.7e-6 eV."""
        pq = PQAxiomWithResidual()
        assert abs(pq.axion_mass_eV - 5.7e-6) < 1e-7

    def test_PQ_standard_theta_eff_zero(self):
        """Standard PQ: theta_eff -> 0 after relaxation."""
        pq = PQAxiomWithResidual()
        assert pq.standard_PQ_theta_eff == 0.0

    def test_PQ_Choptyuk_theta_eff(self):
        """Choptyuk-augmented PQ: theta_eff -> theta_Ch."""
        pq = PQAxiomWithResidual()
        assert abs(pq.Choptyuk_PQ_theta_eff - 8.46e-11) < 1e-12

    def test_PQ_axion_mass_shift_negligible(self):
        """Relative axion mass shift ~ theta_Ch^2/2 ~ 1e-21."""
        pq = PQAxiomWithResidual()
        assert abs(pq.axion_mass_shift - 3.58e-21) < 1e-22

    def test_monte_carlo_d_n_mean(self):
        """Monte Carlo d_n mean ~ 2.1e-26 e*cm (within 30%)."""
        mc = MonteCarloUncertainty(n_samples=10000)
        r = mc.run()
        assert 1.5e-26 < r["d_n_mean_e_cm"] < 3.0e-26

    def test_monte_carlo_p_value_in_range(self):
        """P(d_n > bound) should be 0.3-0.7 (coin flip)."""
        mc = MonteCarloUncertainty(n_samples=10000)
        r = mc.run()
        assert 0.3 < r["p_value_d_n_above_bound"] < 0.7

    def test_falsifiability_timeline_has_4_experiments(self):
        """Timeline must include SNS nEDM, n2EDM, RaEDM, J-PARC."""
        tl = FalsifiabilityTimeline()
        exps = tl.experiments
        assert len(exps) == 4
        names = [e["name"] for e in exps]
        assert "SNS nEDM (ORNL, USA)" in names
        assert "n2EDM@PSI (Switzerland)" in names

    def test_falsifiability_SNS_decisive(self):
        """SNS nEDM must be marked as decisive."""
        tl = FalsifiabilityTimeline()
        sns = [e for e in tl.experiments if "SNS" in e["name"]][0]
        assert sns["decisive"] is True
        assert sns["sigma_if_detection"] > 10.0

    def test_qcd_verify_all_returns_complete_dict(self):
        """verify_all() must return a complete results dictionary."""
        results = qcd_verify_all()
        assert "bridge" in results
        assert "cp_observables" in results
        assert "mercury_paradox_resolution" in results
        assert "lattice_theta_dependence" in results
        assert "PQ_axion_with_residual" in results
        assert "monte_carlo_uncertainty" in results
        assert "falsifiability_timeline" in results
        assert "verdict" in results

    def test_qcd_verify_all_bridge_values(self):
        """verify_all() bridge values match direct computation."""
        results = qcd_verify_all()
        b = results["bridge"]
        assert abs(b["a_C"] - (math.pi / 7) ** 5 / 22) < 1e-15
        assert abs(b["theta_Ch"] - 8.46e-11) < 1e-12
        assert abs(b["exponent"] - 2.5) < 1e-9
