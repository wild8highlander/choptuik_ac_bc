"""Calibrated linear-mode model of the Choptuik critical solution.

The model superposes decaying echo modes on a single unstable mode whose
growth rate is ``lambda_0 = 2.6745`` (so that ``gamma = 1/lambda_0 ~ 0.374``
matches the Choptuik scaling law), with imaginary parts spaced by
``2*pi/Delta`` where ``Delta = ln 2`` is the echoing period.  This is the
standard spectral signature of the discretely self-similar critical
solution reported in the critical-collapse literature.

Scope caveat: this module powers *visualization and workflow testing*;
it is not a solver of the full Einstein-scalar PDE system.  The full
system belongs to the Lean formalization roadmap (Phase 2).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

#: growth rate of the single unstable mode (dimensionless, in log-time tau)
LAMBDA0: float = 2.6745

#: echoing period of the DSS critical solution (Choptuik: Delta ~ ln 2)
ECHO_PERIOD: float = math.log(2.0)

#: critical exponent of the black-hole mass scaling law, gamma = 1/lambda_0
GAMMA: float = 1.0 / LAMBDA0

#: supercritical black-hole mass amplitude (calibration constant)
MASS_AMPLITUDE: float = 0.80

#: amplitude of the leading analytic correction to the scaling law
CORRECTION_B: float = -0.30

#: exponent of the leading analytic correction
CORRECTION_OMEGA: float = 2.0


def mode_families(n_decaying: int = 7) -> list[tuple[float, float]]:
    """Return the calibrated (Re, +Im) pairs of the decaying echo modes.

    The imaginary parts start near ``2*pi/Delta / 2`` and are spaced by
    exactly ``2*pi/Delta`` — the spectral echo of the DSS periodicity.
    Real parts move leftward roughly linearly in ``k``.
    """
    spacing = 2.0 * math.pi / ECHO_PERIOD
    return [(-(4.30 + 1.80 * k), 0.5 * spacing + spacing * k) for k in range(n_decaying)]


@dataclass
class ModeModel:
    """Superposition of exponential modes on a radial grid.

    Each mode ``k`` carries a spatial profile ``phi_k(r)`` (a localized
    Gaussian whose width shrinks with ``k``, echoing the scale contraction
    of the DSS solution) and an eigenvalue ``lambda_k``.
    """

    r_min: float = 0.0
    r_max: float = 10.0
    n_grid: int = 241
    n_decaying: int = 7
    seed: int = 1993  # the Choptuik year; deterministic by design

    _r: np.ndarray = field(init=False, repr=False)
    _modes: list[tuple[complex, np.ndarray]] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._r = np.linspace(self.r_min, self.r_max, self.n_grid)
        rng = np.random.default_rng(self.seed)
        eigenvalues = [complex(LAMBDA0, 0.0)]
        eigenvalues += [complex(re, im) for re, im in mode_families(self.n_decaying)]
        self._modes = []
        for k, ev in enumerate(eigenvalues):
            center = 1.2 + 0.9 * k
            width = 1.6 / (1.0 + 0.45 * k)
            profile = np.exp(-((self._r - center) ** 2) / (2.0 * width**2))
            profile *= np.cos(0.8 * self._r + 0.7 * k + 0.3 * rng.standard_normal())
            # normalize so that the unstable mode has unit central amplitude
            peak = np.max(np.abs(profile)) or 1.0
            self._modes.append((ev, profile / peak))

    # ------------------------------------------------------------------
    @property
    def grid(self) -> np.ndarray:
        """Radial grid ``r`` on which profiles are defined."""
        return self._r.copy()

    @property
    def eigenvalues(self) -> list[complex]:
        """Calibrated eigenvalues, unstable mode first."""
        return [ev for ev, _ in self._modes]

    def coefficients(self, tau: float) -> np.ndarray:
        """Modal amplitudes at log-time ``tau`` (unstable mode dominates)."""
        c = np.array([np.exp(ev * tau) for ev, _ in self._modes])
        c[1:] *= 0.22  # decaying echo modes start subdominant
        return c

    def profile(self, tau: float) -> np.ndarray:
        """Scalar-field profile ``phi(r, tau)`` of the critical evolution."""
        c = self.coefficients(tau)
        out = np.zeros_like(self._r)
        for ck, (_, phi) in zip(c, self._modes):
            out += (ck.real if abs(ck.imag) < 1e-14 else 2.0 * np.abs(ck)) * phi
        return out

    # ------------------------------------------------------------------
    def black_hole_mass(self, delta_p: float, noisy: bool = True) -> float:
        """Supercritical black-hole mass from the scaling ansatz.

        ``M(p) = M0 * d^gamma * (1 + B * d^omega + eps)``, ``d = |p - p*|``,
        where ``eps`` is a small seeded measurement noise (reproducible).
        """
        if delta_p <= 0:
            raise ValueError("delta_p must be positive (supercritical family)")
        d = float(delta_p)
        value = MASS_AMPLITUDE * d**GAMMA * (1.0 + CORRECTION_B * d**CORRECTION_OMEGA)
        if noisy:
            rng = np.random.default_rng(self.seed + int(round(-math.log10(d) * 1000)))
            value *= 1.0 + 0.002 * rng.standard_normal()
        return float(max(value, 1e-12))


def fit_scaling_exponent(delta_p: np.ndarray, mass: np.ndarray) -> tuple[float, float, float]:
    """Least-squares fit ``ln M = gamma * ln d + c`` for the scaling law.

    Returns ``(gamma_fit, log_intercept, rms_residual)``.
    """
    x = np.log(np.asarray(delta_p, dtype=float))
    y = np.log(np.asarray(mass, dtype=float))
    slope, intercept = np.polyfit(x, y, 1)
    resid = y - (slope * x + intercept)
    return float(slope), float(intercept), float(np.sqrt(np.mean(resid**2)))


def echo_period_from_profile(tau: np.ndarray, amplitude: np.ndarray) -> float:
    """Recover the echoing period from a central-amplitude time series.

    Uses the discrete autocorrelation of the *detrended log* amplitude;
    the first strong peak beyond the correlation drop gives ``Delta``.
    """
    x = np.log(np.asarray(amplitude, dtype=float))
    x = x - np.linspace(x[0], x[-1], x.size)  # remove linear envelope
    x = x - x.mean()
    ac = np.correlate(x, x, mode="full")[x.size - 1 :]
    dt = float(np.mean(np.diff(tau)))
    # search for the first local maximum after lag index 5
    for i in range(5, ac.size - 1):
        if ac[i] >= ac[i - 1] and ac[i] >= ac[i + 1] and ac[i] > 0.3 * ac[0]:
            return float(i * dt)
    raise RuntimeError("no echo peak found — profile does not echo")
