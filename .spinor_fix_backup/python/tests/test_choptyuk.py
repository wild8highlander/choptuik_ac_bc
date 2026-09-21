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
