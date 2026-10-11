"""C12 - matter-antimatter asymmetry lock (T14/T15).

Physical picture (model class, honest scope):
  * The gap sector carries a closure cost B0 = Delta_F,min (normalization N2).
  * The matter sector perturbs the gap potential by eta * U1 with unit
    sup-norm; the worst case drops the closure barrier by exactly 2*eta.
  * Hence the gap survives every asymmetry eta < eta_crit = Delta_F,min / 2.
  * Planck baryon asymmetry eta_B = 6.1e-10 sits 1.49e8 times below eta_crit.
  * Free quarks would screen and fill the gap wells (negative feedback);
    toy fill dynamics shows zero sustained accumulations at eta_B and a
    cascade only above eta_crit.
"""
from __future__ import annotations

import math

from .constants import DELTA_F_MIN, ETA_B, ETA_CRIT, TUNNEL_T_ZERO
from .core import tunneling_window


# --- T14: worst-case barrier lemma -------------------------------------------
def barrier_worst(eta: float) -> float:
    """Worst-case closure barrier: B0 - 2*eta (unit-norm perturbation)."""
    return DELTA_F_MIN - 2.0 * eta


X_STAR = 0.181777          # valley location in the unit-gap coordinate


def profiles() -> list[dict]:
    """Nine unit-sup-norm perturbation profiles U1(x), x in [0, 0.5].

    drop_at_unit_eta = U1(0) - U1(x_star): the barrier loss at eta = 1.
    The theoretical worst case is exactly 2 (step profile).
    """
    def step(x):    return -1.0 if x < X_STAR else 1.0
    def tent(x):    return -1.0 + 2.0 * min(1.0, x / X_STAR)
    def cosw(x):    return -math.cos(math.pi * min(1.0, x / X_STAR))
    def quad(x):    return 2.0 * (x / X_STAR) ** 2 - 1.0
    def expo(x):    return -math.exp(-x / 0.05) + 0.99326
    def sign2(x):   return -1.0 if x < 0.5 * X_STAR else 1.0
    def saw(x):     return 1.0 - 2.0 * (x / X_STAR) if x < X_STAR else -1.0
    def sgn3(x):    return -1.0 if x < 0.5 * X_STAR else 1.0
    def sinw(x):    return math.sin(3.0 * math.pi * min(1.0, x / X_STAR) - math.pi / 2)
    out = []
    for name, fn in [("step", step), ("tent", tent), ("cosw", cosw), ("quad", quad),
                     ("expo", expo), ("sign2", sign2), ("saw", saw),
                     ("sgn3", sgn3), ("sinw", sinw)]:
        xs = [i / 1000.0 * X_STAR for i in range(1001)]
        sup = max(abs(fn(x)) for x in xs)
        drop = fn(X_STAR) - fn(0.0)
        out.append({"name": name, "sup": round(sup, 12),
                    "drop_at_unit_eta": round(drop, 12)})
    return out


def phase_grid_eta(n_eta: int = 41) -> dict:
    """Grid over eta in [1e-12, 10^-0.5]: OPEN while eta < eta_crit."""
    lo, hi = math.log10(1e-12), -0.5
    cells = []
    for i in range(n_eta):
        eta = 10 ** (lo + (hi - lo) * i / (n_eta - 1))
        b = barrier_worst(eta)
        cells.append({"eta": eta, "barrier": b,
                      "status": "OPEN" if b > 0 else "CLOSED"})
    n_open = sum(1 for c in cells if c["status"] == "OPEN")
    return {"n_cells": n_eta, "n_open": n_open,
            "eta_min": cells[0]["eta"], "eta_max": cells[-1]["eta"],
            "eta_crit": ETA_CRIT, "cells": cells}


def asymmetry_margin() -> dict:
    return {"eta_B": ETA_B, "eta_crit": ETA_CRIT,
            "margin": ETA_CRIT / ETA_B,
            "log10_margin": math.log10(ETA_CRIT / ETA_B)}


# --- T15: gap-filling toy dynamics --------------------------------------------
def fill_dynamics(n_wells: int = 200, n_steps: int = 1_000_000, eta: float = ETA_B,
                  rate_scale: float = 1000.0, seed: int = 424243,
                  fill_per_hit: float = 0.001, record_every: int = 100_000) -> dict:
    """Toy negative-feedback dynamics: hits fill wells; saturated well = nugget.

    Injection probability per step: p = eta * rate_scale (capped at 1).
    A well saturates when its fill reaches 1 -> local gap closed (nugget).
    """
    import random
    rng = random.Random(seed)
    wells = [0.0] * n_wells
    p = min(1.0, eta * rate_scale)
    saturated = 0
    max_fill = 0.0
    total_hits = 0
    trace = []
    for step in range(1, n_steps + 1):
        if rng.random() < p:
            i = rng.randrange(n_wells)
            if wells[i] < 1.0:
                wells[i] = min(1.0, wells[i] + fill_per_hit)
                total_hits += 1
                if wells[i] >= 1.0:
                    saturated += 1
        if step % record_every == 0:
            trace.append({"step": step, "max_fill": max(wells), "saturated": saturated})
    max_fill = max(wells)
    return {"n_wells": n_wells, "n_steps": n_steps, "eta": eta,
            "p_inject": p, "total_hits": total_hits, "saturated": saturated,
            "max_fill": max_fill, "trace": trace[:10]}


def nugget_bound(log10_n: float = 30.0) -> dict:
    """Combinatorial nugget bound from the C7 tunneling window.

    A free quark appears per attempt with probability T(0) ~ 9.21e-13.
    A macroscopic nugget with ~10^30 quarks needs ~10^30 successes:
    log10 P = 30 * log10(T0) ~ -361 for a 10^30/10^30 split; for a truly
    macroscopic object (N = 10^30) log10 P = N log10 T0 = -1.2e31.
    Both are reported.
    """
    t0 = TUNNEL_T_ZERO
    log10_p_1kg = 30.0 * math.log10(t0)
    log10_p_macro = (10 ** log10_n) * math.log10(t0)
    return {"T0": t0,
            "log10_prob_30quarks": log10_p_1kg,
            "log10_prob_macro_N1e30": log10_p_macro,
            "statement": ("P(nugget of 1e30 quarks) < 10^(-1.2e31); "
                          "even 30 simultaneous tunneled quarks: 10^(-361)")}


def c12_summary() -> dict:
    tw = tunneling_window()
    return {"eta_crit": ETA_CRIT, "eta_B": ETA_B,
            "margin": ETA_CRIT / ETA_B,
            "barrier_zero_eta": DELTA_F_MIN,
            "tunneling": {"T_zero": tw["T_zero"], "window_E_max": tw["window_E_max"]},
            "conclusion": ("complete matter-antimatter asymmetry keeps the gap open "
                           "for every eta < 0.0908885 (= 1.49e8 x eta_B); free quarks "
                           "cannot exist as separate asymptotic states")}
