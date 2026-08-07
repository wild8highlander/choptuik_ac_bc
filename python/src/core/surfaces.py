"""Surface specifications for Bolza, Bring, and Macbeath surfaces.

Each surface is a genus-2 or genus-3 Riemann surface with a specific
automorphism group, first Laplacian eigenvalue, and maximal spinor phase.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class SurfaceSpec:
    """Specification of a Riemann surface for spectral computation.

    Attributes:
        name: Surface name.
        lambda_1: First Laplacian eigenvalue.
        delta_max: Maximal spinor phase.
        group_name: Automorphism group name.
        group_order: Automorphism group order.
        R: Scalar curvature.
        genus: Curve genus.
    """
    name: str
    lambda_1: float
    delta_max: float
    group_name: str
    group_order: int
    R: float = -2.0
    genus: int = 3

    def compute(self, k_struct: int = 22) -> dict:
        """Compute spectral invariants using the Choptyuk formula.

        Args:
            k_struct: Structural constant for a-C correction.

        Returns:
            Dict with all computed values.
        """
        lam_D2 = self.lambda_1 + self.R / 4
        delta_bc = lam_D2 + self.delta_max**2 / 2
        delta_ch = delta_bc - self.delta_max**5 / k_struct
        result = {
            "name": self.name,
            "lambda_1": self.lambda_1,
            "delta_max": self.delta_max,
            "group": self.group_name,
            "group_order": self.group_order,
            "genus": self.genus,
            "R": self.R,
            "lambda_D2": lam_D2,
            "delta_bc": delta_bc,
            "delta_ch": delta_ch,
        }
        logger.info(f"Surface {self.name}: Δ_bC={delta_bc:.4f}, Δ_Ch={delta_ch:.4f}")
        return result


# Predefined surfaces
BOLZA = SurfaceSpec(
    name="Bolza", lambda_1=3.34253, delta_max=np.pi/8,
    group_name="GL(2,3)=2S4", group_order=48, genus=2
)

BRING = SurfaceSpec(
    name="Bring", lambda_1=3.7, delta_max=np.pi/5,
    group_name="S5", group_order=120, genus=4
)

MACBEATH = SurfaceSpec(
    name="Macbeath", lambda_1=3.2, delta_max=np.pi/7,
    group_name="PSL(2,8)", group_order=504, genus=7
)

DEFAULT_SURFACES = [BOLZA, BRING, MACBEATH]
