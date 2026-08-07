"""Full verification suite for all monograph results.

Orchestrates the complete verification chain:
  Part I:   Klein curve + spinor phases + group relations
  Part I.4: Dirac operator + Lichnerowicz formula
  Part I.6: b-C correction
  Part II:  a-C correction (braking)
  Part III: Unified Choptyuk formula
  Part III.3: Choptyuk constant b_Ch
  Part IV.1: 64 spinor structures
  Part IV.3: Bolza, Bring, Macbeath surfaces
  Part IV.4: LIGO/Virgo QNM predictions
"""

from __future__ import annotations

import logging
import time
from typing import Any

from ..core.choptyuk_formula import ChoptyukFormula
from ..core.dirac_operator import DiracOperator
from ..core.klein_curve import KleinCurve
from ..core.qnm import QNMPredictor
from ..core.spinor_phases import SpinorPhases
from ..core.surfaces import DEFAULT_SURFACES, SurfaceSpec

logger = logging.getLogger(__name__)


class VerificationSuite:
    """Orchestrates the full verification of all monograph results.

    All parameters are customizable. The suite records timing and
    produces a complete results dictionary.
    """

    def __init__(self,
                 genus: int = 3, K: float = -1.0,
                 psl_order: int = 168, lambda_1: float = 3.838,
                 delta_A: float | None = None,
                 delta_B: float | None = None,
                 delta_C: float | None = None,
                 k_struct: int = 22,
                 c4: float = 0.125, c6: float = 0.5,
                 delta_obs: float = 3.443,
                 b_ch_obs: float = 0.377,
                 surfaces: list[SurfaceSpec] | None = None,
                 qnm_events: list | None = None):
        self.curve = KleinCurve(genus, K, psl_order, lambda_1)
        self.phases = SpinorPhases(delta_A, delta_B, delta_C)
        self.dirac = DiracOperator(lambda_1, self.curve.R)
        self.formula = ChoptyukFormula(
            self.dirac.lambda_D2_triv, self.phases.delta_C,
            k_struct, c4, c6, delta_obs, b_ch_obs
        )
        self.surfaces = surfaces or DEFAULT_SURFACES
        self.qnm = QNMPredictor(qnm_events)
        self.delta_obs = delta_obs
        self.results: dict[str, Any] = {}
        self.logs: list[str] = []
        self._start_time = 0.0

    def run(self, include_structures: bool = True,
            include_surfaces: bool = True,
            include_qnm: bool = True) -> dict:
        """Run the full verification suite.

        Returns:
            Complete results dictionary.
        """
        self._start_time = time.time()
        self._log("=" * 60)
        self._log("FULL VERIFICATION SUITE")
        self._log("=" * 60)

        # Part I: Klein curve
        self._log("\n--- Part I: Klein Curve ---")
        self.results["curve"] = self.curve.as_dict()
        A, B, C = self.curve.generators()
        rel = self.curve.verify_relations(A, B, C)
        self.results["relations"] = rel
        self._log(f"A²=-I: {rel['A_sq_eq_negI']}, B³=-I: {rel['B_cub_eq_negI']}, (AB)⁷=I: {rel['C_sev_eq_I']}")

        # Spinor phases
        self._log("\n--- Spinor Phases ---")
        self.results["phases"] = self.phases.as_dict()
        self._log(f"δ_A={self.phases.delta_A:.6f}, δ_B={self.phases.delta_B:.6f}, δ_C={self.phases.delta_C:.6f}")

        # Dirac operator
        self._log("\n--- Dirac Operator (Lichnerowicz) ---")
        self.results["dirac"] = self.dirac.as_dict()
        self._log(f"λ₁(D²_σ₀) = {self.dirac.lambda_D2_triv}")

        # Choptyuk formula
        self._log("\n--- Choptyuk Formula ---")
        ch_result = self.formula.compute()
        self.results["choptyuk"] = {
            "delta_bc": ch_result.delta_bc,
            "gamma": ch_result.gamma,
            "delta_eff": ch_result.delta_eff,
            "delta_ch_base": ch_result.delta_ch_base,
            "delta_ch_full": ch_result.delta_ch_full,
            "b_ch": ch_result.b_ch,
            "deviation_bc_pct": ch_result.deviation_bc,
            "deviation_ch_pct": ch_result.deviation_ch,
            "deviation_full_pct": ch_result.deviation_full,
            "deviation_b_ch_pct": ch_result.deviation_b_ch,
        }
        self._log(f"Δ_bC = {ch_result.delta_bc:.6f} (dev {ch_result.deviation_bc:.3f}%)")
        self._log(f"Δ_Ch(base) = {ch_result.delta_ch_base:.6f} (dev {ch_result.deviation_ch:.3f}%)")
        self._log(f"Δ_Ch(full) = {ch_result.delta_ch_full:.6f} (dev {ch_result.deviation_full:.3f}%)")
        self._log(f"b_Ch = {ch_result.b_ch:.6f} (dev {ch_result.deviation_b_ch:.3f}%)")

        # 64 spinor structures
        if include_structures:
            self._log("\n--- 64 Spinor Structures ---")
            structs = self.phases.enumerate_structures(
                self.dirac.lambda_D2_triv, self.delta_obs
            )
            self.results["structures"] = [
                {"id": s.id, "n_active": s.n_active,
                 "Delta": s.Delta, "deviation": s.deviation}
                for s in structs
            ]
            self.results["structure_distribution"] = self.phases.distribution(structs)
            best = structs[0]
            self._log(f"Best: ID={best.id}, Δ={best.Delta:.6f}, dev={best.deviation:.3f}%")

        # Surfaces
        if include_surfaces:
            self._log("\n--- Surfaces (Bolza, Bring, Macbeath) ---")
            self.results["surfaces"] = [s.compute(self.formula.k_struct) for s in self.surfaces]

        # QNM
        if include_qnm:
            self._log("\n--- LIGO/Virgo QNM ---")
            self.results["qnm_predictions"] = self.qnm.predict_all()
            self.results["qnm_detectability"] = self.qnm.detectability()

        elapsed = time.time() - self._start_time
        self.results["timing"] = {"elapsed_seconds": round(elapsed, 4)}
        self._log(f"\nVerification completed in {elapsed:.4f}s")

        return self.results

    def _log(self, msg: str) -> None:
        """Append a timestamped log message."""
        ts = time.strftime("%H:%M:%S")
        entry = f"[{ts}] {msg}"
        self.logs.append(entry)
        logger.info(msg)

    def get_logs(self) -> str:
        """Return all log messages as a single string."""
        return "\n".join(self.logs)
