# -*- coding: utf-8 -*-
"""
wu.py — Hawking pairs and the Wu (1957) parity-violation door.

The third link of the hypothesis (a marked HYPOTHESIS, see
docs/theory.md): Hawking pairs leave the horizon; the weak interaction
annihilation channel is parity-asymmetric (Wu et al. 1957 — the
"full asymmetry" of the weak probe); a residual fraction of matter
escapes annihilation and becomes the door through which bound triplets
enter the world.

Committed toy model (W-model, linear rates, docs/methods.md):

  two species +/- born at the same rate Gamma_b (Hawking flux);
  each species annihilates on the opposite one with its own rate
      Gamma_+ = Gamma*(1 - alpha),   Gamma_- = Gamma*(1 + alpha),
  where alpha in [0, 1] is the parity-asymmetry parameter of the
  annihilation channel (the Wu door width);

  dN_+/dt = Gamma_b - Gamma_+ N_+      (linear mean field)
  dN_-/dt = Gamma_b - Gamma_- N_-

Freeze-out at t_f = 1/H (H = expansion rate).  With x = Gamma/H the
closed-form residual imbalance is EXACT (theorem T7):

  f(u) = (1 - e^{-x u}) / u,
  r(alpha, x) = [ f(1-alpha) - f(1+alpha) ] / [ f(1-alpha) + f(1+alpha) ].

Limits (machine-checked, mpmath layer):
  x -> 0 (slow annihilation):  r -> 0        (nothing freezes imbalanced)
  x -> inf (fast annihilation): r -> alpha   (the Wu door fully open)
  alpha = 0: r = 0 for every x               (no door, no matter)

Honest scope (carried everywhere): with the literature baryon-to-photon
anchor eta = 6.1e-10 the committed toy numbers show the door OPENS but
does not by itself reproduce cosmogenesis; the model realizes the
Sakharov ingredients qualitatively, not quantitatively.
"""
import math

from .constants import A_WU_ANCHOR, eta_baryon


def f_u(x, u):
    """f(u) = (1 - exp(-x u))/u  with the exact u->0 limit f = x."""
    if abs(u) < 1e-300:
        return x
    return -math.expm1(-x * u) / u


def residual(alpha, x):
    """Closed-form residual imbalance r(alpha, x) — theorem T7 (exact)."""
    fp = f_u(x, 1.0 - alpha)      # species + (annihilation slowed by alpha)
    fm = f_u(x, 1.0 + alpha)      # species - (annihilation sped by alpha)
    return (fp - fm) / (fp + fm)


def freezeout_x(Gamma, H):
    """Committed freeze-out ratio x = Gamma/H."""
    return Gamma / H


def residual_anchor(x, alpha=None):
    """r at the Wu anchor asymmetry (approximate literature anchor)."""
    if alpha is None:
        alpha = A_WU_ANCHOR
    return residual(alpha, x)


def required_x_for_eta(alpha, eta=None, r_target=None):
    """Invert r(alpha, x) = r_target numerically (bisection, 200 iters).

    With r_target = eta_baryon this answers: how fast must annihilation
    freeze for the door to leave only eta?  Honest comparison only.
    """
    if r_target is None:
        r_target = eta_baryon
    lo, hi = 1e-12, 1e12
    for _ in range(200):
        mid = math.sqrt(lo * hi)
        if residual(alpha, mid) < r_target:
            lo = mid
        else:
            hi = mid
    return math.sqrt(lo * hi)
