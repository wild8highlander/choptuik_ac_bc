"""Unified Choptyuk formula: b-C correction, a-C correction, and combined results.

The Choptyuk formula unifies two spinor corrections on the Klein quartic:

1. b-C correction (Berry phase, 1st order):
   Delta_bC = lambda_1(D²_sigma_0) + delta_C^2 / 2

2. a-C correction (braking, 2nd order):
   gamma = delta_C^4 / k,  k = b_2(K3) = 22
   delta_eff = delta_C * gamma = delta_C^5 / 22  (approximately 1/1200)

3. Unified formula (base):
   Delta_Ch = lambda_1(D²_sigma_0) + delta_C^2/2 - delta_C^5/22

4. With higher-order corrections:
   Delta_Ch = base + C4*delta_C^4 + C6*delta_C^6
   where C4 = 1/8, C6 = 1/2

5. Choptyuk constant:
   b_Ch = 1 - cos(2*pi/7) = 2*sin^2(pi/7) ≈ 0.377
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ChoptyukResult:
    """Complete results of the Choptyuk formula computation.

    Attributes:
        lambda_D2_triv: Trivial Dirac eigenvalue.
        delta_C: Spinor phase on C.
        delta_bc: b-C corrected value.
        gamma: Braking coefficient.
        delta_eff: Effective phase (a-C correction).
        delta_ch_base: Base Choptyuk value.
        delta_ch_full: Full Choptyuk value with higher orders.
        b_ch: Choptyuk constant.
        deviation_bc: Deviation of b-C from observed (%).
        deviation_ch: Deviation of base from observed (%).
        deviation_full: Deviation of full from observed (%).
        deviation_b_ch: Deviation of b_Ch from observed (%).
    """
    lambda_D2_triv: float
    delta_C: float
    delta_bc: float
    gamma: float
    delta_eff: float
    delta_ch_base: float
    delta_ch_full: float
    b_ch: float
    deviation_bc: float
    deviation_ch: float
    deviation_full: float
    deviation_b_ch: float


class ChoptyukFormula:
    """Unified Choptyuk formula with b-C and a-C corrections.

    All parameters are customizable for hypothesis testing.
    """

    def __init__(self, lambda_D2_triv: float = 3.338,
                 delta_C: float | None = None,
                 k_struct: int = 22,
                 c4: float = 0.125,
                 c6: float = 0.5,
                 delta_obs: float = 3.443,
                 b_ch_obs: float = 0.377):
        self.lambda_D2_triv = lambda_D2_triv
        self.delta_C = delta_C if delta_C is not None else np.pi / 7
        self.k_struct = k_struct
        self.c4 = c4
        self.c6 = c6
        self.delta_obs = delta_obs
        self.b_ch_obs = b_ch_obs
        logger.info(
            f"Choptyuk formula: λ₁(D²_σ₀)={lambda_D2_triv}, δ_C={self.delta_C:.6f}, "
            f"k={k_struct}, C4={c4}, C6={c6}"
        )

    def compute(self) -> ChoptyukResult:
        """Compute all Choptyuk formula values.

        Returns:
            ChoptyukResult with all computed constants and deviations.
        """
        dC = self.delta_C

        # b-C correction (1st order)
        delta_bc = self.lambda_D2_triv + dC**2 / 2
        logger.info(f"Δ_bC = {self.lambda_D2_triv} + {dC**2/2:.6f} = {delta_bc:.6f}")

        # a-C correction (2nd order, braking)
        gamma = dC**4 / self.k_struct
        delta_eff = dC * gamma  # = dC^5 / k
        logger.info(f"γ = δ_C⁴/k = {gamma:.8f}, δ_eff = {delta_eff:.8f}")
        logger.info(f"δ_eff ≈ 1/1200 = {1/1200:.8f}, deviation = {abs(delta_eff - 1/1200)/(1/1200)*100:.3f}%")

        # Base Choptyuk formula
        delta_ch_base = delta_bc - delta_eff
        logger.info(f"Δ_Ch(base) = {delta_ch_base:.6f}")

        # With higher orders
        delta_ch_full = delta_ch_base + self.c4 * dC**4 + self.c6 * dC**6
        logger.info(f"Δ_Ch(full) = {delta_ch_full:.6f}")

        # Choptyuk constant
        b_ch = 1 - np.cos(2 * np.pi / 7)
        logger.info(f"b_Ch = 1 - cos(2π/7) = {b_ch:.6f}")

        # Deviations from observed
        deviation_bc = abs(delta_bc - self.delta_obs) / self.delta_obs * 100
        deviation_ch = abs(delta_ch_base - self.delta_obs) / self.delta_obs * 100
        deviation_full = abs(delta_ch_full - self.delta_obs) / self.delta_obs * 100
        deviation_b_ch = abs(b_ch - self.b_ch_obs) / self.b_ch_obs * 100

        result = ChoptyukResult(
            lambda_D2_triv=self.lambda_D2_triv,
            delta_C=dC,
            delta_bc=delta_bc,
            gamma=gamma,
            delta_eff=delta_eff,
            delta_ch_base=delta_ch_base,
            delta_ch_full=delta_ch_full,
            b_ch=b_ch,
            deviation_bc=deviation_bc,
            deviation_ch=deviation_ch,
            deviation_full=deviation_full,
            deviation_b_ch=deviation_b_ch,
        )
        logger.info(
            f"Deviations: b-C={deviation_bc:.3f}%, Ch(base)={deviation_ch:.3f}%, "
            f"Ch(full)={deviation_full:.3f}%, b_Ch={deviation_b_ch:.3f}%"
        )
        return result

    def as_dict(self) -> dict:
        """Serialize formula parameters."""
        return {
            "lambda_D2_triv": self.lambda_D2_triv,
            "delta_C": self.delta_C,
            "k_struct": self.k_struct,
            "c4": self.c4,
            "c6": self.c6,
            "delta_obs": self.delta_obs,
            "b_ch_obs": self.b_ch_obs,
        }
