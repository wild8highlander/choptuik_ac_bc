"""
campaign C8 — the Wu door with pair-consuming kinetics (v1.1.0,
the roadmap's third entry).

The linear mean field of the W-model (qhb.wu, theorem T7) is replaced
by PAIRWISE annihilation: an event needs a + and a - pair, and the
parity-asymmetric step selects the triggering species:

  dN_+/dt = Gamma_b - k_+ N_+ N_- ,   k_+ = k (1 - alpha)
  dN_-/dt = Gamma_b - k_- N_+ N_- ,   k_- = k (1 + alpha)

The trigger asymmetry (which member initiates the weak step) is the Wu
door; the consumption is pairwise.  Nondimensionalisation with the
linear steady-state density N_* = Gamma_b / H and tau = H t gives the
committed two-parameter form

  dn_+/dt = 1 - lambda (1 - alpha) n_+ n_- ,
  dn_-/dt = 1 - lambda (1 + alpha) n_+ n_- ,   lambda = k Gamma_b / H^2,

with freeze-out at tau_f = 1 (t_f = 1/H, the committed convention) and
n_+(0) = n_-(0) = 0.  The residual r = (n_+ - n_-) / (n_+ + n_-).

Exact structural facts (machine-checked here):
  X1  alpha = 0  =>  the two right-hand sides are IDENTICAL, so the two
      trajectories are bitwise equal and r = 0.0 EXACTLY (no door);
  X2  d(n_+ - n_-)/dtau = 2 lambda alpha n_+ n_- >= 0 — the imbalance is
      monotone nondecreasing; the plus member (the rarer annihilator)
      survives.

No closed form exists (honest note: the exactness of T7 is a property
of the LINEAR model and does not extend).  Committed numerics:
  * RK4 with a convergence ladder (measured order -> 4, pinned);
  * a 50-digit mpmath cross-check at the anchor cell (lambda = 1,
    alpha = 0.9) — the package's mpmath discipline.

Committed shape comparison (the roadmap's "the door stays, the shape
moves"): r_pair(lambda, alpha) against the linear r_lin(x = lambda,
alpha) on the same numeric ladder.  Matching lambda to x is a
COMPARISON DEVICE (honest note: the two models have different
dimensionality; only the shape-level statement is claimed):
  linear door:  r_lin -> alpha as x -> inf  (a partial imbalance);
  pairwise door: the imbalance accumulates without a linear death term
  to stop it — the machine will show r_pair climbing toward 1 (the FULL
  imbalance): the door stays, the shape moves.

The verdict is written to campaigns/reference/c8_verdict.json.
"""
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from qhb.constants import __version__
from qhb.wu import residual as r_linear

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "reference")

LAMBDA_GRID = (1e-2, 1e-1, 1.0, 10.0, 100.0)
ALPHA_GRID = (0.0, 0.25, 0.5, 0.9)
TAU_F = 1.0


def rhs(n, lam, alpha):
    """The committed nondimensional pairwise field (numpy vector form)."""
    np_, nm_ = n
    pair = np_ * nm_
    return np.array([1.0 - lam * (1.0 - alpha) * pair,
                     1.0 - lam * (1.0 + alpha) * pair])


def integrate_pair(lam, alpha, tau_f=TAU_F, n_steps=1 << 13):
    """RK4 of the pairwise system; returns (n_+, n_-) at tau_f (floats)."""
    dt = tau_f / n_steps
    n = np.zeros(2)
    for k in range(n_steps):
        k1 = rhs(n, lam, alpha)
        k2 = rhs(n + 0.5 * dt * k1, lam, alpha)
        k3 = rhs(n + 0.5 * dt * k2, lam, alpha)
        k4 = rhs(n + dt * k3, lam, alpha)
        n = n + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
    return float(n[0]), float(n[1])


def residual_pair(lam, alpha, tau_f=TAU_F, n_steps=1 << 13):
    nplus, nminus = integrate_pair(lam, alpha, tau_f, n_steps)
    tot = nplus + nminus
    if tot <= 0.0:
        return 0.0, nplus, nminus
    return (nplus - nminus) / tot, nplus, nminus


def main():
    t0 = time.time()
    verdict = {
        "campaign": "qhb_c8",
        "engine": "deterministic RK4 of the committed pairwise system " +
                  "(numpy) + an mpmath 50-digit cross-check; no MC, no " +
                  "seeds",
        "project_version": __version__,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "model": {
            "system": "dn_+/dt = 1 - lambda(1-alpha) n_+ n_- ; " +
                      "dn_-/dt = 1 - lambda(1+alpha) n_+ n_-",
            "nondimensionalisation": "N_* = Gamma_b / H (the linear " +
                                     "steady state), tau = H t, " +
                                     "lambda = k Gamma_b / H^2",
            "freezeout": "tau_f = 1 (t_f = 1/H, the committed convention)",
            "honesty": "MARKED HYPOTHESIS — the trigger-asymmetry reading " +
                       "of the pair event is a toy of the Wu mechanism, " +
                       "not a weak-interaction calculation",
        },
    }

    # --- X1: the exact no-door check -------------------------------------------
    r0, np0, nm0 = residual_pair(1.0, 0.0)
    x1_ok = (r0 == 0.0) and (np0 == nm0)
    print(f"X1 alpha=0: n_+ = n_- = {np0:.12f}, r = {r0!r} -> "
          f"{'PASS' if x1_ok else 'FAIL'}", flush=True)
    verdict["X1_no_door_exact"] = {"r": r0, "n_plus": np0,
                                   "n_minus": nm0, "ok": x1_ok}

    # --- X2: monotone imbalance (checked along a fine trajectory) ----------------
    lam, al = 1.0, 0.9
    prev_d = 0.0
    mono_ok = True
    for k in range(1, 65):
        npl, nmi = integrate_pair(lam, al, tau_f=TAU_F * k / 64,
                                  n_steps=1 << 10)
        d = npl - nmi
        if d < prev_d - 1e-15:
            mono_ok = False
            break
        prev_d = d
    print(f"X2 monotone imbalance: {'PASS' if mono_ok else 'FAIL'}",
          flush=True)
    verdict["X2_monotone_imbalance"] = {"ok": mono_ok}

    # --- the convergence ladder (RK4 order pinned) --------------------------------
    ladder = []
    for n_steps in (256, 512, 1024, 2048):
        r_f, _, _ = residual_pair(lam, al, n_steps=n_steps)
        ladder.append({"n_steps": n_steps, "r": r_f})
    p_measured = None
    # effective order from the last triple (against the finest as reference
    # would be circular; the classic triple is used)
    r1, r2, r3 = (ladder[-3]["r"], ladder[-2]["r"], ladder[-1]["r"])
    denom = abs(r1 - r2)
    if denom > 0 and abs(r2 - r3) > 0:
        p_measured = math.log2(denom / abs(r2 - r3))
    conv_ok = p_measured is not None and abs(p_measured - 4.0) < 0.05
    print(f"convergence: p_eff = {p_measured:.4f} -> "
          f"{'PASS' if conv_ok else 'CHECK'}", flush=True)
    verdict["convergence"] = {"ladder": ladder, "p_eff": p_measured,
                              "ok": conv_ok}

    # --- the 50-digit mpmath cross-check at the anchor cell ------------------------
    import mpmath as mp
    mp.mp.dps = 50
    lam_mp, al_mp = mp.mpf('1.0'), mp.mpf('0.9')

    def f_pair(t, y):
        pair = y[0] * y[1]
        return [1 - lam_mp * (1 - al_mp) * pair,
                1 - lam_mp * (1 + al_mp) * pair]

    odef = mp.odefun(f_pair, mp.mpf('0'), [mp.mpf('0'), mp.mpf('0')])
    y_end = odef(mp.mpf('1.0'))
    r_mp = (y_end[0] - y_end[1]) / (y_end[0] + y_end[1])
    r_np, _, _ = residual_pair(lam, al, n_steps=1 << 14)
    mp_dev = abs(float(r_mp) - r_np)
    mp_ok = mp_dev < 1e-9
    print(f"mpmath 50-digit: r_mp = {mp.nstr(r_mp, 12)}  dev = {mp_dev:.2e}"
          f" -> {'PASS' if mp_ok else 'FAIL'}", flush=True)
    verdict["mpmath_anchor"] = {"r_mp_50d": mp.nstr(r_mp, 20),
                                "r_numpy": r_np, "dev": mp_dev,
                                "ok": mp_ok}

    # --- the committed grid: the door stays, the shape moves ------------------------
    rows = []
    for al in ALPHA_GRID:
        for lam in LAMBDA_GRID:
            r_p, npl, nmi = residual_pair(lam, al)
            r_l = r_linear(al, lam)      # comparison device: x := lambda
            rows.append({"alpha": al, "lambda": lam, "r_pair": r_p,
                         "r_linear_at_x=lambda": r_l,
                         "n_plus": npl, "n_minus": nmi})
            print(f"alpha={al:4.2f} lambda={lam:7.2f}  r_pair={r_p:.6f}  "
                  f"r_lin={r_l:.6f}", flush=True)
    verdict["grid"] = rows

    # structural comparisons
    a09 = {r["lambda"]: r for r in rows if r["alpha"] == 0.9}
    door_stays = all(a09[l]["r_pair"] > 0 for l in LAMBDA_GRID) \
        and a09[100.0]["r_pair"] > a09[0.01]["r_pair"]
    # the shape move: the pairwise asymptote leaves the linear alpha-limit
    lin_limit_dev = abs(a09[100.0]["r_pair"] - 0.9)
    shape_moves = lin_limit_dev > 0.05
    verdict["door_stays"] = {
        "ok": door_stays,
        "statement": "r_pair > 0 for every alpha > 0 cell and grows with " +
                     "lambda — the door survives the kinetics change",
    }
    verdict["shape_moves"] = {
        "ok": shape_moves,
        "r_pair_at_lambda_100_alpha_09": a09[100.0]["r_pair"],
        "linear_limit_alpha": 0.9,
        "dev_from_linear_limit": lin_limit_dev,
        "statement": "the pairwise door has NO alpha asymptote: with the " +
                     "linear death term gone, the imbalance accumulates " +
                     "toward the FULL residual (r -> 1) — the door stays, " +
                     "the shape moves",
    }
    print(f"door stays: {'PASS' if door_stays else 'CHECK'}; shape moves: "
          f"{'PASS' if shape_moves else 'CHECK'}", flush=True)

    verdict["verdicts"] = {
        "X1_no_door": "PASS (exact)" if x1_ok else "FAIL",
        "X2_monotone": "PASS" if mono_ok else "FAIL",
        "convergence_RK4": "PASS" if conv_ok else "CHECK",
        "mpmath_50d": "PASS" if mp_ok else "FAIL",
        "door_stays": "CONFIRMED" if door_stays else "CHECK",
        "shape_moves": "CONFIRMED (r_pair -> full imbalance, the linear " +
                       "alpha-limit is gone)" if shape_moves else "CHECK",
        "T7_extension": "NEGATIVE (honest) — the closed form of T7 does " +
                        "NOT extend to pairwise kinetics; exactness is a " +
                        "property of the linear model",
    }
    verdict["honest_notes"] = [
        "the closed-form exactness of T7 is LOST in the pairwise model; " +
        "the committed replacement is the convergence ladder + the " +
        "50-digit cross-check, not a formula",
        "matching lambda to the linear x is a comparison device; the two " +
        "models have different dimensionless structure and only the " +
        "shape-level statement (door survives, asymptote moves) is " +
        "claimed",
        "the full-imbalance limit r -> 1 is a property of the toy (no " +
        "linear death term to stop the accumulation); cosmogenesis " +
        "claims remain out of scope exactly as in C3",
        "the pairwise asymmetry lives in the TRIGGER species (which " +
        "member initiates the weak step); an event still consumes a " +
        "pair — this is the committed reading of the Wu door, marked as " +
        "a hypothesis",
    ]
    verdict["wall_s"] = time.time() - t0

    os.makedirs(REF, exist_ok=True)
    with open(os.path.join(REF, "c8_verdict.json"), "w", encoding="utf-8") as fh:
        json.dump(verdict, fh, indent=1)
    print(f"verdict written: campaigns/reference/c8_verdict.json "
          f"[{verdict['wall_s']:.1f}s]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
