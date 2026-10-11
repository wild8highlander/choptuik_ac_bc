#!/usr/bin/env python3
"""
ivp_common.py — shared infrastructure of the IVP-15 independent
verification suite (Collapse-Hawking Bridge release audit).

INDEPENDENCE CONTRACT OF THE WHOLE SUITE (see PROTOCOL.md, §2)
--------------------------------------------------------------
1. No IVP script may read `campaigns/reference/*` (verdict JSON/CSV) or
   anything derived from them while MEASURING.  Committed machine
   outputs may be loaded only in the explicit COMPARISON ("unblind")
   phase at the very end of a script, exclusively through
   `read_committed_verdict()`, and only to be compared against values
   the script has already measured on its own.
2. Physical closed forms (r_s, T_H, S_BH, P_H, t_evap, Planck units)
   are re-implemented inside this suite and are never imported from
   `chbridge`; `chbridge` values enter only the comparison phase.
3. The initial-data family geometry (u0, v_p, sigma, grid box) is part
   of the model SPECIFICATION — an input, not a measured output.  It is
   re-declared here from the published family definition (Gaussian
   pulse on the ingoing characteristic u = u0) and documented as such.
4. Exact analytic solutions used by the numerical IVPs (Roberts-Oshiro)
   are re-implemented here from their published coordinate form, never
   taken from the engine's own copy.
5. Every script writes a machine-readable verdict JSON into
   `results/` with status PASS / FAIL / INCONCLUSIVE / PARTIAL, the
   pre-registered acceptance criteria, the measured values and the
   comparison block, so the audit trail is fully re-runnable.
"""
from __future__ import annotations

import json
import os
import sys
import time
import warnings

import numpy as np

IVP_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(IVP_DIR)
RESULTS_DIR = os.path.join(IVP_DIR, "results")
LOGS_DIR = os.path.join(RESULTS_DIR, "logs")
ENGINE_DIR = os.path.join(REPO_ROOT, "engine")

# ---------------------------------------------------------------------------
# Pre-registered model specification (INPUT, not output):
# Gaussian-pulse family of Choptuik-type initial data, engine baseline.
#   Phi(u0, v) = A exp(-(v - v_p)^2 / (2 sigma^2));  row v = v0 flat.
# Geometry as documented in docs/methods.md (family definition).
# ---------------------------------------------------------------------------
GEO = {
    "u0": -1.0, "v0": 0.0, "v_p": 0.5, "sigma": 0.1,
    "u1": 1.05, "v1": 1.0,
}

# statuses ordered from best to worst
_STATUS_ORDER = ["PASS", "PARTIAL", "INCONCLUSIVE", "FAIL"]


def worst_status(statuses):
    """Aggregate several check statuses into the overall (worst) one."""
    present = [s for s in statuses if s in _STATUS_ORDER]
    if not present:
        return "INCONCLUSIVE"
    return max(present, key=_STATUS_ORDER.index)


def log(msg=""):
    print(msg, flush=True)


def now_iso():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def environment():
    import platform
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "processor": platform.processor() or "unknown",
    }


def ensure_dirs():
    os.makedirs(LOGS_DIR, exist_ok=True)
    return RESULTS_DIR


def load_engine():
    """Import the engine solver module (the object under test)."""
    warnings.filterwarnings("ignore")  # engine masks NaN near singularity
    if ENGINE_DIR not in sys.path:
        sys.path.insert(0, ENGINE_DIR)
    import solver
    return solver


def save_result(ivp_id, payload):
    """Persist the machine verdict of one IVP."""
    ensure_dirs()
    payload = dict(payload)
    payload.setdefault("ivp", ivp_id)
    payload.setdefault("timestamp", now_iso())
    payload.setdefault("environment", environment())
    path = os.path.join(RESULTS_DIR, f"{ivp_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1, default=float)
    log(f"[{ivp_id}] verdict -> {os.path.relpath(path, REPO_ROOT)}")
    return path


def read_committed_verdict(name):
    """COMPARISON PHASE ONLY: load a committed campaign verdict.

    Per the independence contract this function must never be called
    before a script has finished its own blind measurement.
    """
    path = os.path.join(REPO_ROOT, "campaigns", "reference", name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_committed_csv(name):
    """COMPARISON PHASE ONLY: load a committed reference CSV."""
    import csv
    path = os.path.join(REPO_ROOT, "campaigns", "reference", name)
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def rel_diff(a, b):
    """Relative difference |a-b| / max(|b|, tiny)."""
    a, b = float(a), float(b)
    return abs(a - b) / max(abs(b), 1e-300)


def compare_rows(pairs):
    """Build a comparison table.

    pairs: iterable of (label, computed, claimed, tol_rel) — computed
    values are the suite's own measurements, claimed values come from
    committed artifacts loaded in the comparison phase only.
    """
    rows = []
    for label, computed, claimed, tol in pairs:
        if computed is None or claimed is None:
            ok = None
            rd = None
        else:
            rd = rel_diff(computed, claimed)
            ok = bool(rd <= tol)
        rows.append({
            "quantity": label,
            "ivp_measured": None if computed is None else float(computed),
            "committed": None if claimed is None else float(claimed),
            "rel_diff": None if rd is None else float(rd),
            "tol_rel": float(tol),
            "agree": ok,
        })
    return rows


# ---------------------------------------------------------------------------
# Independent initial-data classes.
#
# Both subclass the engine's dataclasses ONLY so that the engine's
# isinstance() dispatch accepts them; every method used by the engine is
# overridden with an independent implementation of the published formulas.
# ---------------------------------------------------------------------------

def make_independent_gaussian(solver_mod):
    """Independent Choptuik-family Gaussian pulse (own edge formulas)."""

    class _IndependentGaussianPulse(solver_mod.GaussianPulseData):
        def edge_phi(self, v):
            v = np.asarray(v, dtype=float)
            return self.A * np.exp(-((v - self.v_p) ** 2) / (2.0 * self.sigma ** 2))

        def edge_phi_v(self, v):
            v = np.asarray(v, dtype=float)
            return (-self.A * (v - self.v_p) / (self.sigma ** 2)
                    * np.exp(-((v - self.v_p) ** 2) / (2.0 * self.sigma ** 2)))

        def edge_r(self, v):
            v = np.asarray(v, dtype=float)
            return (v - self.u0) / 2.0

        def edge_r_v(self, v):
            return np.full_like(np.asarray(v, dtype=float), 0.5)

        def edge_r_vv(self, u_edge, v):
            return np.zeros_like(np.asarray(v, dtype=float))

    return _IndependentGaussianPulse


def make_independent_roberts(solver_mod):
    """Independent Roberts-Oshiro exact solution (own formulas).

    Published coordinate form (Burko 1996, eqs. (15)-(16)), sigma in
    (0, 1/2), metric alpha = 1:

        r^2 = 1/4 [ (1 - 4 sigma^2) v^2 - 2 u v + u^2 ]
        Phi = 1/2 ln | (1 - 2 sigma - u/v) / (1 + 2 sigma - u/v) |
    """

    class _IndependentRoberts(solver_mod.RobertsData):
        def fields(self, u, v):
            s = float(self.sigma)
            u = np.asarray(u, dtype=float)
            v = np.asarray(v, dtype=float)
            r2 = 0.25 * ((1.0 - 4.0 * s * s) * v * v - 2.0 * u * v + u * u)
            r = np.sqrt(np.maximum(r2, 1e-300))
            r_u = (u - v) / (4.0 * r)
            r_v = ((1.0 - 4.0 * s * s) * v - u) / (4.0 * r)
            a = 1.0 - 2.0 * s - u / v
            b = 1.0 + 2.0 * s - u / v
            Phi = 0.5 * np.log(np.abs(a / b))
            Phi_u = -(1.0 / (2.0 * v)) * (1.0 / a - 1.0 / b)
            Phi_v = (u / (2.0 * v * v)) * (1.0 / a - 1.0 / b)
            return r, Phi, r_u, r_v, Phi_u, Phi_v

        def edge_r_vv(self, u_edge, v):
            s = float(self.sigma)
            v = np.asarray(v, dtype=float)
            u_arr = np.full_like(v, float(u_edge))
            r, _, _, r_v, _, _ = self.fields(u_arr, v)
            r2_vv = (1.0 - 4.0 * s * s) / 2.0
            return r2_vv / (2.0 * r) - r_v ** 2 / r

    return _IndependentRoberts


def run_gaussian(A, n, monitor_every=100):
    """One engine run on the independent Gaussian pulse; returns (diag, sol)."""
    solver_mod = load_engine()
    IndepG = make_independent_gaussian(solver_mod)
    data = IndepG(A=A, v_p=GEO["v_p"], sigma=GEO["sigma"], u0=GEO["u0"], v0=GEO["v0"])
    cfg = solver_mod.SolverConfig(
        n_u=n, n_v=n, u_range=(GEO["u0"], GEO["u1"]), v_range=(GEO["v0"], GEO["v1"]),
        monitor_every=monitor_every)
    sol = solver_mod.DoubleNullSolver(cfg, data)
    diag = sol.run(verbose=False)
    return diag, sol


def classification(diag):
    """Blind super/subcritical classifier: an apparent horizon forms."""
    return bool(diag.ah_found) and bool(np.isfinite(diag.m_ah))
