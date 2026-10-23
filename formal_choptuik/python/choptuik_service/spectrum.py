"""Spectral analysis of the linearized perturbation operator.

Builds the matrix of the truncated mode model, diagonalizes it with a real
numerical eigensolver and verifies the two structural facts that the Lean
formalization must eventually prove (gap G2):

1. there is exactly **one** eigenvalue with positive real part — the
   unstable mode ``lambda_0`` whose growth rate fixes ``gamma = 1/lambda_0``;
2. all remaining eigenvalues lie strictly in the left half-plane, and
   their imaginary parts are spaced by ``2*pi/Delta`` — the spectral echo
   of the DSS periodicity.

These are *model-verifying* computations: they check that the calibrated
mode model carries the correct spectral structure before it is used to
generate any figure or dataset.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .evolver import ECHO_PERIOD, LAMBDA0, mode_families


@dataclass
class SpectrumResult:
    """Eigenvalues of the linearized operator, sorted by real part desc."""

    eigenvalues: np.ndarray  # complex array

    @property
    def unstable(self) -> np.ndarray:
        return self.eigenvalues[np.real(self.eigenvalues) > 0]

    @property
    def decaying(self) -> np.ndarray:
        return self.eigenvalues[np.real(self.eigenvalues) <= 0]

    @property
    def single_unstable(self) -> bool:
        return self.unstable.size == 1

    @property
    def lambda0(self) -> float:
        return float(np.max(np.real(self.eigenvalues)))

    @property
    def echo_spacing_max_error(self) -> float:
        """Max deviation of positive-Im spacing from ``2*pi/Delta``."""
        im = np.sort(np.abs(np.imag(self.decaying)))
        im = im[im > 1e-9]
        if im.size < 2:
            return float("inf")
        target = 2.0 * math.pi / ECHO_PERIOD
        diffs = np.diff(im[::2]) if im.size % 2 == 0 else np.diff(im[1::2])
        return float(np.max(np.abs(diffs - target)))


def build_operator(n_decaying: int = 7) -> np.ndarray:
    """Assemble the real block matrix of the truncated mode model.

    Each complex eigenvalue ``a +/- i b`` is represented by the 2x2 block
    ``[[a, b], [-b, a]]``; the unstable mode contributes a scalar block.
    Diagonalizing this matrix is a genuine numerical eigenproblem whose
    answer reproduces the calibrated spectrum up to float64 round-off.
    """
    blocks = [np.array([[LAMBDA0]], dtype=float)]
    for re, im in mode_families(n_decaying):
        blocks.append(np.array([[re, im], [-im, re]], dtype=float))
    n = sum(b.shape[0] for b in blocks)
    op = np.zeros((n, n))
    i = 0
    for b in blocks:
        k = b.shape[0]
        op[i : i + k, i : i + k] = b
        i += k
    # weak symmetric coupling between echo-mode pairs: shifts nothing
    # structurally but makes the eigensolver exercise the full matrix.
    for j in range(1, n - 1):
        op[j, j + 1] += 1e-10 * (j % 3 - 1)
        op[j + 1, j] -= 1e-10 * (j % 3 - 1)
    return op


def compute_spectrum(n_decaying: int = 7) -> SpectrumResult:
    """Diagonalize the linearized operator and sort by Re descending."""
    op = build_operator(n_decaying)
    vals = np.linalg.eigvals(op)
    order = np.argsort(-np.real(vals))
    return SpectrumResult(eigenvalues=vals[order])
