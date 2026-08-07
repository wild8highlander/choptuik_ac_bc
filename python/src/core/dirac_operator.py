"""Dirac operator on the Klein quartic and the Lichnerowicz formula.

The Lichnerowicz formula relates the square of the Dirac operator to the
Bochner Laplacian and scalar curvature:
  D^2 = nabla* nabla + R/4

For the first eigenvalue on the trivial spinor bundle:
  lambda_1(D^2_sigma_0) = lambda_1(Delta) + R/4
"""

from __future__ import annotations
import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DiracOperator:
    """Dirac operator computations via the Lichnerowicz formula.

    Attributes:
        lambda_1_laplacian: First eigenvalue of the scalar Laplacian.
        R: Scalar curvature of the Klein curve.
        lambda_D2_triv: First eigenvalue of D^2 on trivial spinor bundle.
    """

    def __init__(self, lambda_1: float = 3.838, R: float = -2.0):
        self.lambda_1_laplacian = lambda_1
        self.R = R
        self.lambda_D2_triv = lambda_1 + R / 4
        logger.info(
            f"Dirac operator: λ₁(Δ)={lambda_1}, R={R}, "
            f"λ₁(D²_σ₀)={self.lambda_D2_triv}"
        )

    def eigenvalue_D2(self, spinor_contribution: float = 0.0) -> float:
        """Compute D^2 eigenvalue with spinor contribution.

        Args:
            spinor_contribution: Additional contribution from nontrivial
                spinor structure (e.g., delta_C^2 / 2).

        Returns:
            Eigenvalue of D^2.
        """
        result = self.lambda_D2_triv + spinor_contribution
        logger.debug(f"D² eigenvalue: {self.lambda_D2_triv} + {spinor_contribution} = {result}")
        return result

    def gap(self) -> float:
        """Compute the spectral gap lambda_1(D^2) - 0."""
        return self.lambda_D2_triv

    def as_dict(self) -> dict:
        """Serialize Dirac operator data."""
        return {
            "lambda_1_laplacian": self.lambda_1_laplacian,
            "R": self.R,
            "lambda_D2_triv": self.lambda_D2_triv,
        }
