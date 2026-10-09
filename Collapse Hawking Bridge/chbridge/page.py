# -*- coding: utf-8 -*-
"""
page.py — Page curves for the ensemble of critical-collapse-born holes.

Unitary entropy-flux model.  For each input-mass scale and each ensemble
member (near_floor / mid / saturated) the model gives:

    S_BH(t)  = S0 (1 - t/t_evap)^{2/3}      coarse-grained, decreasing
    S_rad(t) = S_BH(t)        t < t_Page    young hole: entanglement entropy
    S_rad(t) = S0 - S_BH(t)   t > t_Page    old hole: isometry wins
    t_Page   = (1 - 2^{-3/2}) t_evap         PAGE_FRACTION = 0.6464466...

plus the exact Haar-averaged Page formula (Page 1993 / Sen 1996) checked
against Haar-random Monte-Carlo sampling:

    S_avg(m, n) = ( sum_{k=n+1}^{m n} 1/k - (m-1)/(2 n) ) / ln 2

where m, n are the DIMENSIONS of the two Hilbert factors (m <= n).
"""
import csv
import math
import os

import numpy as np

from .constants import BRIDGE_SCALES, k_B
from .hawking import S_BH, T_H, t_evap, t_page, PAGE_FRACTION

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N_T = 240


def member_f_tilde():
    """Dimensionless member profile (same values as bridge.ensemble_members)."""
    return {"near_floor": 0.287708, "mid": 0.268393, "saturated": 1.0}


def curves(M0, n=N_T):
    """Normalized Page curves for initial mass M0 (SI kg)."""
    S0 = S_BH(M0) / k_B
    u = np.linspace(1.0, 0.0, n)              # M/M0
    tau = 1.0 - u**3                          # t/t_evap
    S_bh = S0 * u**2
    t_page = PAGE_FRACTION
    S_rad = np.where(tau < t_page, S_bh, S0 - S_bh)
    return tau, S_bh, S_rad, S0


def haar_avg_entropy(m, n):
    """Page averaging formula (exact; returns bits) for dims m <= n."""
    k = np.arange(n + 1, m * n + 1)
    S_nats = float(np.sum(1.0 / k) - (m - 1) / (2.0 * n))
    return S_nats / math.log(2.0)


def write_outputs(out_dir, seed=20260101):
    """Write page_curve_grid.csv, page_members.csv, page_haar_check.csv."""
    os.makedirs(out_dir, exist_ok=True)
    ftil = member_f_tilde()
    scale_name, M_in = BRIDGE_SCALES[2]       # CMB input scale fully sampled

    with open(os.path.join(out_dir, "page_curve_grid.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["input_scale", "member", "f_tilde", "t_over_t_evap",
                    "S_BH_over_kB_norm", "S_rad_over_kB_norm",
                    "S_BH_over_kB", "S_rad_over_kB"])
        for tag, ft in ftil.items():
            M0 = M_in * ft
            tau, S_bh, S_rad, S0 = curves(M0)
            for i in range(N_T):
                w.writerow([scale_name, tag, f"{ft:.6g}", f"{tau[i]:.6f}",
                            f"{S_bh[i]/S0:.6f}", f"{S_rad[i]/S0:.6f}",
                            f"{S_bh[i]:.6e}", f"{S_rad[i]:.6e}"])

    with open(os.path.join(out_dir, "page_members.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["input_scale", "M_in_kg", "member", "f_tilde", "M_BH_kg",
                    "S0_over_kB", "T_H_K", "t_evap_s", "t_Page_s",
                    "t_Page_over_t_evap"])
        for scale_name, M_in in BRIDGE_SCALES:
            for tag, ft in ftil.items():
                M0 = M_in * ft
                w.writerow([scale_name, f"{M_in:.6e}", tag, f"{ft:.6g}",
                            f"{M0:.6e}", f"{S_BH(M0)/k_B:.6e}", f"{T_H(M0):.6e}",
                            f"{t_evap(M0):.6e}", f"{t_page(M0):.6e}",
                            f"{PAGE_FRACTION:.6f}"])

    # --- Haar check: exact formula vs Haar-random Monte-Carlo ---------------
    rng = np.random.default_rng(seed)
    rows = []
    for Ntot in (4, 5, 6, 7):
        for Nbh in range(1, Ntot):
            Nrad = Ntot - Nbh
            dim_bh, dim_rad = 2**Nbh, 2**Nrad
            lo, hi = min(dim_bh, dim_rad), max(dim_bh, dim_rad)
            S_exact = haar_avg_entropy(lo, hi)
            n_mc = 3000 if Ntot <= 6 else 1200
            S_samples = []
            for _ in range(n_mc):
                psi = rng.normal(size=2**Ntot) + 1j * rng.normal(size=2**Ntot)
                psi /= np.linalg.norm(psi)
                psi_m = psi.reshape(dim_bh, dim_rad)
                rho_bh = psi_m @ psi_m.conj().T
                evals = np.linalg.eigvalsh(rho_bh)
                evals = evals[evals > 1e-12]
                S_samples.append(-float(np.sum(evals * np.log(evals))) / math.log(2))
            S_mc = float(np.mean(S_samples))
            rows.append({"N_total": Ntot, "N_bh": Nbh, "N_rad": Nrad,
                         "S_page_formula_bits": round(S_exact, 6),
                         "S_monte_carlo_bits": round(S_mc, 6),
                         "abs_diff_bits": round(abs(S_exact - S_mc), 6),
                         "n_mc": n_mc})
    with open(os.path.join(out_dir, "page_haar_check.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    max_dev = max(r["abs_diff_bits"] for r in rows)
    return {"grid_points": N_T * len(ftil), "haar_partitions": len(rows),
            "max_dev_bits": max_dev}
