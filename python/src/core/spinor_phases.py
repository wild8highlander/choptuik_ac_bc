"""Spinor phases on the Klein quartic and enumeration of all 64 spinor structures.

For the (2,3,7) triangle group, the spinor phases are:
  delta_A = pi/2  (corresponding to element of order 2 in PSL)
  delta_B = pi/3  (corresponding to element of order 3 in PSL)
  delta_C = pi/7  (corresponding to element of order 7 in PSL)

There are 2^6 = 64 spinor structures on the Klein curve, parameterized by
the 6 generators of H_1(K, Z/2Z). Each structure is a choice of which
generators carry an active spinor phase delta_C.
"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class SpinorStructure:
    """A single spinor structure on the Klein curve.

    Attributes:
        id: Integer identifier 0..63.
        bits: Binary representation [b0, b1, b2, b3, b4, b5].
        n_active: Number of active generators (sum of bits).
        delta_C: Spinor phase for active generators.
        Delta: Computed spectral value.
        deviation: Percentage deviation from observed value.
    """
    id: int
    bits: List[int]
    n_active: int
    delta_C: float
    Delta: float
    deviation: float


class SpinorPhases:
    """Spinor phase computations and 64-structure enumeration.

    Attributes:
        delta_A: Phase on A = pi/2.
        delta_B: Phase on B = pi/3.
        delta_C: Phase on C = pi/7.
    """

    def __init__(self, delta_A: Optional[float] = None,
                 delta_B: Optional[float] = None,
                 delta_C: Optional[float] = None):
        self.delta_A = delta_A if delta_A is not None else np.pi / 2
        self.delta_B = delta_B if delta_B is not None else np.pi / 3
        self.delta_C = delta_C if delta_C is not None else np.pi / 7
        logger.info(
            f"Spinor phases: δ_A={self.delta_A:.6f}, "
            f"δ_B={self.delta_B:.6f}, δ_C={self.delta_C:.6f}"
        )

    def enumerate_structures(self, lambda_D2_triv: float,
                              delta_obs: float = 3.443,
                              n_structures: int = 64,
                              n_generators: int = 6) -> List[SpinorStructure]:
        """Enumerate all 2^n_generators spinor structures.

        For each structure, compute the spectral value:
          Delta = lambda_D2_triv + (1/2) * sum(delta_C^2 for active generators)

        Args:
            lambda_D2_triv: Trivial Dirac eigenvalue λ₁(D²_σ₀).
            delta_obs: Observed value for deviation computation.
            n_structures: Number of structures (default 64 = 2^6).
            n_generators: Number of generators (default 6).

        Returns:
            List of SpinorStructure objects sorted by deviation.
        """
        structures = []
        for i in range(n_structures):
            bits = [(i >> j) & 1 for j in range(n_generators)]
            n_active = sum(bits)
            sum_sq = sum(self.delta_C**2 for b in bits if b) / 2
            Delta = lambda_D2_triv + sum_sq
            deviation = abs(Delta - delta_obs) / delta_obs * 100
            structures.append(SpinorStructure(
                id=i, bits=bits, n_active=n_active,
                delta_C=self.delta_C, Delta=Delta, deviation=deviation
            ))

        structures.sort(key=lambda s: s.deviation)
        logger.info(f"Enumerated {len(structures)} spinor structures")
        best = structures[0]
        logger.info(
            f"Best structure: ID={best.id}, n_active={best.n_active}, "
            f"Δ={best.Delta:.6f}, deviation={best.deviation:.3f}%"
        )
        return structures

    def distribution(self, structures: List[SpinorStructure]) -> dict:
        """Compute distribution of structures by number of active generators.

        Returns:
            Dict mapping n_active -> count.
        """
        from collections import Counter
        counts = Counter(s.n_active for s in structures)
        result = {}
        for n in sorted(counts.keys()):
            subset = [s for s in structures if s.n_active == n]
            result[n] = {
                "count": counts[n],
                "avg_Delta": float(np.mean([s.Delta for s in subset])),
                "min_deviation": float(min(s.deviation for s in subset)),
            }
        logger.info(f"Distribution: { {k: v['count'] for k, v in result.items()} }")
        return result

    def as_dict(self) -> dict:
        """Serialize spinor phases."""
        return {
            "delta_A": self.delta_A,
            "delta_B": self.delta_B,
            "delta_C": self.delta_C,
        }
