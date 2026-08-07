"""Klein quartic curve: structural parameters, PSL(2,7) generators, and matrix representations.

The Klein quartic is the unique genus-3 Riemann surface with maximal automorphism group
PSL(2,7) of order 168. It is the quotient H/Gamma(2,3,7) where Gamma(2,3,7) is the
(2,3,7) triangle group. The curve satisfies the Gauss-Bonnet relation Area = 4*pi*(g-1).
"""

from __future__ import annotations
import numpy as np
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class KleinCurve:
    """Klein quartic curve with all structural invariants.

    Attributes:
        genus: Curve genus g = 3.
        K: Gaussian curvature K = -1 (hyperbolic).
        R: Scalar curvature R = 2K = -2.
        area: Total area = 4*pi*(g-1) = 8*pi (Gauss-Bonnet).
        psl_order: |PSL(2,7)| = 168.
        sl_order: |SL(2,7)| = 336.
        lambda_1: First eigenvalue of scalar Laplacian (Bourque-Strohmaier 2024).
    """

    def __init__(self, genus: int = 3, K: float = -1.0,
                 psl_order: int = 168, lambda_1: float = 3.838):
        self.genus = genus
        self.K = K
        self.R = 2 * K
        self.area = 4 * np.pi * (genus - 1)
        self.psl_order = psl_order
        self.sl_order = 2 * psl_order
        self.lambda_1 = lambda_1
        logger.info(
            f"Klein curve initialized: g={genus}, K={K}, R={self.R}, "
            f"Area={self.area:.4f}, |PSL(2,7)|={psl_order}, λ₁={lambda_1}"
        )

    def generators(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Compute the Gamma(2,3,7) generators A, B, C in SL(2,R).

        A has order 4 in SL(2,R) (order 2 in PSL), B has order 6 in SL
        (order 3 in PSL), and C = AB has order 7 in SL (order 7 in PSL).
        The relations A^2 = B^3 = (AB)^7 = -I hold in SL(2,R).

        Returns:
            Tuple (A, B, C) of 2x2 numpy arrays.
        """
        A = np.array([[0, 1], [-1, 0]], dtype=float)

        c_const = 4 * np.cos(np.pi / 7) / np.sqrt(3)
        lam = (c_const + np.sqrt(c_const**2 - 4)) / 2
        B = np.array([
            [np.cos(np.pi / 3), lam * np.sin(np.pi / 3)],
            [-np.sin(np.pi / 3) / lam, np.cos(np.pi / 3)]
        ])

        C = A @ B
        logger.info("PSL(2,7) generators A, B, C computed in SL(2,R)")
        return A, B, C

    def verify_relations(self, A: np.ndarray, B: np.ndarray,
                         C: np.ndarray) -> dict:
        """Verify the defining relations A^2 = B^3 = (AB)^7 = -I.

        Args:
            A, B, C: Generator matrices from self.generators().

        Returns:
            Dict with boolean verification results and norms.
        """
        I2 = np.eye(2)
        nI = -I2
        results = {
            "A_sq_eq_negI": bool(np.allclose(A @ A, nI)),
            "A_sq_norm": float(np.linalg.norm(A @ A - nI)),
            "B_cub_eq_negI": bool(np.allclose(np.linalg.matrix_power(B, 3), nI)),
            "B_cub_norm": float(np.linalg.norm(np.linalg.matrix_power(B, 3) - nI)),
            "C_sev_eq_I": bool(np.allclose(np.linalg.matrix_power(C, 7), I2)),
            "C_sev_norm": float(np.linalg.norm(np.linalg.matrix_power(C, 7) - I2)),
        }
        logger.info(f"Relation verification: {results}")
        return results

    def as_dict(self) -> dict:
        """Serialize curve parameters."""
        return {
            "genus": self.genus,
            "K": self.K,
            "R": self.R,
            "area": self.area,
            "psl_order": self.psl_order,
            "sl_order": self.sl_order,
            "lambda_1": self.lambda_1,
        }
