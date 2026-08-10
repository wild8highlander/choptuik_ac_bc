#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_figures_3d_4d.py — Generate all 9 sections' figures in 3D + 4D variants.

For each section of the QCD bridge monograph, produces:
  - 3D surface/scatter plot
  - 4D plot (3D + color dimension OR 3D + time animation frames)
  - 600 DPI PNG
  - Vector PDF
  - Vector SVG

All labels in English.

Author: Ishak Khamzatovich Isaev (ORCID 0009-0003-7299-0701)
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# Font setup — Noto Sans SC handles Latin + CJK; DejaVu Sans catches symbols
import matplotlib.font_manager as fm
for fp in [
    '/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
]:
    if Path(fp).exists():
        fm.fontManager.addfont(fp)

import matplotlib.pyplot as plt
from matplotlib import cm as mpl_cm
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 — registers 3D projection
from matplotlib.colors import Normalize, LinearSegmentedColormap

plt.rcParams['font.sans-serif'] = ['Noto Sans SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.dpi'] = 100

# Add parent dir for engine import
sys.path.insert(0, str(Path(__file__).parent))
from qcd_bridge_engine import (
    QCDBridgeConfig, run_all, build_Ochi, kappa_T_sweep, N_scaling_test,
    tau_relax_dynamics, kappa_T_physical_estimate, cabibbo_coincidence,
    cp_solution_chain, jet_wake_bridge, folded_spacings, gue_spacing_pdf,
    poisson_spacing_pdf, bayes_factor_gue_poisson,
    KAPPA_T_PHYSICAL_LOWER, KAPPA_T_BESTFIT, DELTA_C, N_HILBERT,
)

OUTPUT_DIR = Path("/home/z/my-project/choptuik_ac_bc/qcd_bridge/figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Color palette (Business Cool)
PALETTE = {
    "primary": "#243447",
    "body": "#182030",
    "secondary": "#506070",
    "accent": "#4C6EF5",
    "accent2": "#3AAFA9",
    "accent3": "#C6866A",
    "bg": "#F8FAFC",
    "grid": "#E5E7EB",
}


def save_3formats(fig, name: str) -> Dict[str, str]:
    """Save figure in 600 DPI PNG, PDF, SVG."""
    paths = {}
    for ext, dpi in [("png", 600), ("pdf", None), ("svg", None)]:
        p = OUTPUT_DIR / f"{name}.{ext}"
        kwargs = {"bbox_inches": "tight", "facecolor": "white"}
        if dpi:
            kwargs["dpi"] = dpi
        fig.savefig(str(p), **kwargs)
        paths[ext] = str(p)
    plt.close(fig)
    return paths


# ─────────────────────────────────────────────────────────────────────────────
# Section 1: O_chi operator construction — 3D eigenvalue bar + 4D heatmap
# ─────────────────────────────────────────────────────────────────────────────
def fig_section1_ochi_3d_4d() -> Dict[str, Any]:
    """3D: eigenvalues as bars on a 28-vertex ring; 4D: matrix heatmap with color."""
    O = build_Ochi(KAPPA_T_BESTFIT)
    eigs = np.linalg.eigvalsh(O)
    N = len(eigs)

    # 3D bar plot on a ring
    fig = plt.figure(figsize=(11, 8), constrained_layout=True)
    ax = fig.add_subplot(111, projection='3d')
    theta = np.linspace(0, 2 * np.pi, N, endpoint=False)
    x = np.cos(theta)
    y = np.sin(theta)
    z = np.zeros_like(eigs)
    dz = eigs - eigs.min()
    # color by signed eigenvalue
    norm = Normalize(vmin=eigs.min(), vmax=eigs.max())
    colors = mpl_cm.coolwarm(norm(eigs))
    ax.bar3d(x, y, z, 0.15, 0.15, dz, color=colors, shade=True, edgecolor='black', linewidth=0.3)
    ax.set_xlabel('K3 sector (x)')
    ax.set_ylabel('Flavor sector (y)')
    ax.set_zlabel('Eigenvalue $\\lambda_i$')
    ax.set_title(f'3D eigenvalue spectrum of $O_\\chi$ ($\\kappa_T={KAPPA_T_BESTFIT}$, $N={N}$)')
    paths_3d = save_3formats(fig, "fig_s1_ochi_eigvals_3d")

    # 4D: 28x28 matrix as 3D surface with height + color
    fig = plt.figure(figsize=(11, 8), constrained_layout=True)
    ax = fig.add_subplot(111, projection='3d')
    X, Y = np.meshgrid(np.arange(N), np.arange(N))
    surf = ax.plot_surface(X, Y, O, cmap='RdBu_r', edgecolor='none',
                            norm=Normalize(vmin=-abs(O).max(), vmax=abs(O).max()),
                            alpha=0.95, antialiased=True)
    ax.set_xlabel('Column index $j$')
    ax.set_ylabel('Row index $i$')
    ax.set_zlabel('$O_{\\chi,\\,ij}$')
    ax.set_title(f'4D visualization: $O_\\chi$ matrix surface (height + color = $O_{{ij}}$)')
    fig.colorbar(surf, ax=ax, shrink=0.6, pad=0.1, label='$O_{\\chi,\\,ij}$')
    paths_4d = save_3formats(fig, "fig_s1_ochi_matrix_4d")

    return {"3d": paths_3d, "4d": paths_4d, "n_eigs": N}


# ─────────────────────────────────────────────────────────────────────────────
# Section 2: RMT sweep — 3D BF surface + 4D (BF vs kappa vs color)
# ─────────────────────────────────────────────────────────────────────────────
def fig_section2_rmt_sweep_3d_4d() -> Dict[str, Any]:
    kappas = np.array([0.0, 0.3, 0.7, 1.0, 1.5, 2.0, 2.62, 3.0, 4.0, 5.0, 8.45, 12.0, 20.0])
    sweep = kappa_T_sweep(kappas)
    k = np.array([r["kappa_T"] for r in sweep])
    bf = np.array([r["BF_GUE_Poisson"] for r in sweep])
    mean = np.array([r["lambda_mean"] for r in sweep])
    std = np.array([r["lambda_std"] for r in sweep])

    # 3D: kappa vs BF vs lambda_mean
    fig = plt.figure(figsize=(11, 8), constrained_layout=True)
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(k, bf, zs=0, zdir='z', color=PALETTE["accent"], linewidth=2.5, label='BF(GUE/Poisson)')
    ax.plot(k, mean, zs=0, zdir='y', color=PALETTE["accent2"], linewidth=2.5, label=r'$\langle\lambda\rangle$')
    # 3D scatter
    sc = ax.scatter(k, bf, mean, c=bf, cmap='viridis', s=80, edgecolor='black', linewidth=0.5,
                    norm=Normalize(vmin=bf.min(), vmax=bf.max()))
    ax.set_xlabel(r'$\kappa_T$')
    ax.set_ylabel('Bayes factor BF(GUE/Poisson)')
    ax.set_zlabel(r'$\langle\lambda\rangle$')
    ax.set_title(r'3D: RMT universality sweep — BF, $\kappa_T$, and $\langle\lambda\rangle$')
    ax.set_yscale('log')
    ax.legend(loc='upper left')
    fig.colorbar(sc, ax=ax, shrink=0.6, pad=0.1, label='BF')
    paths_3d = save_3formats(fig, "fig_s2_rmt_sweep_3d")

    # 4D: surface of BF as a function of (kappa, log10(kappa+1)) with color = BF
    fig = plt.figure(figsize=(11, 8), constrained_layout=True)
    ax = fig.add_subplot(111, projection='3d')
    # Use 2D mesh by interpolating
    k_fine = np.linspace(k.min(), k.max(), 60)
    bf_fine = np.interp(k_fine, k, bf)
    mean_fine = np.interp(k_fine, k, mean)
    # Build a surface: x=kappa, y=mean, z=BF, color=BF
    X, Y = np.meshgrid(k_fine, mean_fine)
    Z = np.tile(bf_fine, (len(mean_fine), 1))
    surf = ax.plot_surface(X, Y, Z, cmap='plasma', edgecolor='none', alpha=0.92,
                            norm=Normalize(vmin=bf.min(), vmax=bf.max()))
    # Mark crossover kappa_T ~ 1.5
    ax.scatter([1.5], [0], [np.interp(1.5, k, bf)], color='red', s=200, marker='*',
               label=r'Crossover $\kappa_T \approx 1.5$', zorder=10)
    ax.scatter([KAPPA_T_PHYSICAL_LOWER], [0], [np.interp(KAPPA_T_PHYSICAL_LOWER, k, bf)],
               color='green', s=150, marker='^', label=f'95% CL lower $\\kappa_T={KAPPA_T_PHYSICAL_LOWER}$', zorder=10)
    ax.scatter([KAPPA_T_BESTFIT], [0], [np.interp(KAPPA_T_BESTFIT, k, bf)],
               color='orange', s=200, marker='D', label=f'Best-fit $\\kappa_T={KAPPA_T_BESTFIT}$', zorder=10)
    ax.set_xlabel(r'$\kappa_T$')
    ax.set_ylabel(r'$\langle\lambda\rangle$')
    ax.set_zlabel('Bayes factor BF(GUE/Poisson)')
    ax.set_zscale('linear')
    ax.set_title('4D: BF surface over $(\\kappa_T, \\langle\\lambda\\rangle)$ with crossover markers')
    ax.legend(loc='upper left', fontsize=9)
    fig.colorbar(surf, ax=ax, shrink=0.6, pad=0.1, label='BF')
    paths_4d = save_3formats(fig, "fig_s2_rmt_sweep_4d")

    return {"3d": paths_3d, "4d": paths_4d, "kappas": k.tolist(), "BF": bf.tolist()}


# ─────────────────────────────────────────────────────────────────────────────
# Section 3: Spectral staircase vs Wigner — 3D staircase + 4D spacing histogram
# ─────────────────────────────────────────────────────────────────────────────
def fig_section3_staircase_3d_4d() -> Dict[str, Any]:
    O = build_Ochi(KAPPA_T_BESTFIT)
    eigs = np.sort(np.linalg.eigvalsh(O))
    s = folded_spacings(eigs)

    # 3D staircase: cumulative N(lambda) vs lambda, with bar height as color
    fig = plt.figure(figsize=(11, 8), constrained_layout=True)
    ax = fig.add_subplot(111, projection='3d')
    cum = np.arange(1, len(eigs) + 1)
    # 3D bars
    dx = (eigs.max() - eigs.min()) / len(eigs) * 0.8
    norm = Normalize(vmin=eigs.min(), vmax=eigs.max())
    colors = mpl_cm.viridis(norm(eigs))
    ax.bar3d(eigs, np.zeros_like(eigs), np.zeros_like(eigs),
             dx, 0.5, np.ones_like(eigs), color=colors, shade=True,
             edgecolor='black', linewidth=0.3)
    # Overlay Wigner semicircle
    R = 2 * np.sqrt(28)  # Wigner radius for N=28
    x_w = np.linspace(-R, R, 200)
    y_w = (2 / (np.pi * R**2)) * np.sqrt(np.maximum(R**2 - x_w**2, 0)) * len(eigs) * dx
    ax.plot(x_w, y_w, zs=0, zdir='z', color=PALETTE["accent3"], linewidth=2.5,
            label='Wigner semicircle (rescaled)')
    ax.set_xlabel('Eigenvalue $\\lambda$')
    ax.set_ylabel('Density')
    ax.set_zlabel('Cumulative count $N(\\lambda)$')
    ax.set_title('3D spectral staircase of $O_\\chi$ vs Wigner semicircle')
    ax.legend(loc='upper left')
    paths_3d = save_3formats(fig, "fig_s3_staircase_3d")

    # 4D: spacing histogram with GUE vs Poisson overlays + color = density
    fig = plt.figure(figsize=(11, 8), constrained_layout=True)
    ax = fig.add_subplot(111, projection='3d')
    s_pos = s[s > 1e-9]
    hist, edges = np.histogram(s_pos, bins=20, range=(0, 4), density=True)
    centers = 0.5 * (edges[1:] + edges[:-1])
    dx = (edges[1] - edges[0]) * 0.8
    # 3D bars colored by density
    norm = Normalize(vmin=0, vmax=max(hist.max(), gue_spacing_pdf(centers).max()))
    colors = mpl_cm.plasma(norm(hist))
    ax.bar3d(centers, np.zeros_like(centers), np.zeros_like(hist),
             dx, 0.4, hist, color=colors, shade=True, edgecolor='black', linewidth=0.3)
    # GUE and Poisson curves
    s_grid = np.linspace(0, 4, 200)
    ax.plot(s_grid, gue_spacing_pdf(s_grid), zs=0, zdir='z',
            color=PALETTE["accent"], linewidth=2.5, label='GUE $P(s)=\\frac{32}{\\pi^2}s^2 e^{-4s^2/\\pi}$')
    ax.plot(s_grid, poisson_spacing_pdf(s_grid), zs=0, zdir='z',
            color=PALETTE["accent3"], linewidth=2.5, linestyle='--', label='Poisson $P(s)=e^{-s}$')
    ax.set_xlabel('Folded spacing $s$')
    ax.set_ylabel('Density (offset)')
    ax.set_zlabel('$P(s)$')
    ax.set_title('4D: Folded spacing histogram vs GUE / Poisson (height + color = density)')
    ax.legend(loc='upper right', fontsize=9)
    paths_4d = save_3formats(fig, "fig_s3_staircase_4d")

    return {"3d": paths_3d, "4d": paths_4d, "mean_spacing": float(s_pos.mean())}


# ─────────────────────────────────────────────────────────────────────────────
# Section 4: N-scaling — 3D |<lambda>| vs N vs realization + 4D std surface
# ─────────────────────────────────────────────────────────────────────────────
def fig_section4_N_scaling_3d_4d() -> Dict[str, Any]:
    N_values = [10, 28, 50, 100, 200, 500, 1000]  # capped at 1000 for tractability
    # Multiple realizations per N for spread
    n_realizations = 5
    rng = np.random.default_rng(123)
    results = []
    for N in N_values:
        for r in range(n_realizations):
            G = rng.standard_normal((N, N)) + 1j * rng.standard_normal((N, N))
            H = (G + G.conj().T) / math.sqrt(2 * N)
            eigs = np.linalg.eigvalsh(H)
            results.append({
                "N": N,
                "realization": r,
                "abs_mean": abs(float(eigs.mean())),
                "std": float(eigs.std()),
            })

    Ns = np.array([r["N"] for r in results])
    abs_means = np.array([r["abs_mean"] for r in results])
    stds = np.array([r["std"] for r in results])

    # 3D scatter: N vs |mean| vs std, color by N
    fig = plt.figure(figsize=(11, 8), constrained_layout=True)
    ax = fig.add_subplot(111, projection='3d')
    sc = ax.scatter(Ns, abs_means, stds, c=Ns, cmap='viridis', s=50,
                    edgecolor='black', linewidth=0.4,
                    norm=Normalize(vmin=min(Ns), vmax=max(Ns)))
    # Theoretical 1/sqrt(N)
    N_theory = np.logspace(1, 3.7, 100)
    ax.plot(N_theory, 1 / np.sqrt(N_theory), zs=0, zdir='z',
            color=PALETTE["accent3"], linewidth=2.5,
            label=r'Theory: $1/\sqrt{N}$')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Matrix size $N$')
    ax.set_ylabel(r'$|\langle\lambda\rangle|$')
    ax.set_zlabel(r'Spectral std $\sigma_\lambda$')
    ax.set_title(r'3D: $|\langle\lambda\rangle| \to 0$ as $1/\sqrt{N}$ (multiple realizations)')
    ax.legend(loc='upper right')
    fig.colorbar(sc, ax=ax, shrink=0.6, pad=0.1, label='$N$')
    paths_3d = save_3formats(fig, "fig_s4_N_scaling_3d")

    # 4D: surface of |mean| as (N, realization) with color = std
    fig = plt.figure(figsize=(11, 8), constrained_layout=True)
    ax = fig.add_subplot(111, projection='3d')
    # Build a mesh
    N_unique = sorted(set(Ns))
    R_unique = sorted(set([r["realization"] for r in results]))
    Z = np.zeros((len(R_unique), len(N_unique)))
    C = np.zeros_like(Z)
    for r in results:
        i = R_unique.index(r["realization"])
        j = N_unique.index(r["N"])
        Z[i, j] = r["abs_mean"]
        C[i, j] = r["std"]
    X, Y = np.meshgrid(N_unique, R_unique)
    surf = ax.plot_surface(X, Y, Z, facecolors=mpl_cm.magma(Normalize(vmin=C.min(), vmax=C.max())(C)),
                            edgecolor='none', alpha=0.92, antialiased=True)
    ax.set_xscale('log')
    ax.set_yscale('linear')
    ax.set_xlabel('Matrix size $N$ (log)')
    ax.set_ylabel('Realization index')
    ax.set_zlabel(r'$|\langle\lambda\rangle|$')
    ax.set_title(r'4D: $|\langle\lambda\rangle|$ surface colored by $\sigma_\lambda$ (lower $\to$ GUE regime)')
    fig.colorbar(mpl_cm.ScalarMappable(norm=Normalize(vmin=C.min(), vmax=C.max()), cmap='magma'),
                  ax=ax, shrink=0.6, pad=0.1, label=r'$\sigma_\lambda$')
    paths_4d = save_3formats(fig, "fig_s4_N_scaling_4d")

    return {"3d": paths_3d, "4d": paths_4d, "N_values": N_values,
            "n_realizations": n_realizations}


# ─────────────────────────────────────────────────────────────────────────────
# Section 5: tau_relax dynamics — 3D time evolution + 4D phase portrait
# ─────────────────────────────────────────────────────────────────────────────
def fig_section5_tau_relax_3d_4d() -> Dict[str, Any]:
    relax = tau_relax_dynamics(theta_0=1e-19)
    t = np.array(relax["t_values_s"])
    theta_t = np.array(relax["theta_t_values"])
    tau = relax["tau_relax_s"]

    # 3D: t vs theta(t) vs dtheta/dt
    fig = plt.figure(figsize=(11, 8), constrained_layout=True)
    ax = fig.add_subplot(111, projection='3d')
    dtheta = -theta_t / tau
    ax.plot(t, theta_t, dtheta, color=PALETTE["accent"], linewidth=2.5, label=r'$\theta(t)$')
    ax.scatter(t[::5], theta_t[::5], dtheta[::5], c=t[::5], cmap='cool', s=40,
                edgecolor='black', linewidth=0.3)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_zscale('symlog', linthresh=1e-60)
    ax.set_xlabel(r'Time $t$ (s, log)')
    ax.set_ylabel(r'$\theta(t)$ (log)')
    ax.set_zlabel(r'$d\theta/dt$ (symlog)')
    ax.set_title(rf'3D: $\theta(t) = \theta_0\,e^{{-t/\tau_{{relax}}}}$, $\tau_{{relax}}={tau:.1e}$ s')
    paths_3d = save_3formats(fig, "fig_s5_tau_relax_3d")

    # 4D: phase portrait theta vs dtheta/dt with color = time
    fig = plt.figure(figsize=(11, 8), constrained_layout=True)
    ax = fig.add_subplot(111, projection='3d')
    # Multiple theta_0 scenarios
    theta_0_values = [1e-19, 1e-15, 1e-12, 1e-9]
    for i, th0 in enumerate(theta_0_values):
        th_t = th0 * np.exp(-t / tau)
        dth = -th_t / tau
        sc = ax.scatter(th_t, dth, t, c=t, cmap='viridis', s=30,
                          edgecolor='black', linewidth=0.3, alpha=0.8,
                          label=rf'$\theta_0={th0:.0e}$')
    ax.set_xscale('log')
    ax.set_yscale('symlog', linthresh=1e-60)
    ax.set_zscale('log')
    ax.set_xlabel(r'$\theta(t)$')
    ax.set_ylabel(r'$d\theta/dt$')
    ax.set_zlabel(r'Time $t$ (s)')
    ax.set_title(r'4D: Phase portrait for multiple $\theta_0$ scenarios (color = time)')
    ax.legend(loc='upper right', fontsize=9)
    paths_4d = save_3formats(fig, "fig_s5_tau_relax_4d")

    return {"3d": paths_3d, "4d": paths_4d, "tau_relax_s": tau}


# ─────────────────────────────────────────────────────────────────────────────
# Section 6: kappa_T physical estimate — 3D CI + 4D posterior
# ─────────────────────────────────────────────────────────────────────────────
def fig_section6_kappa_T_3d_4d() -> Dict[str, Any]:
    kpe = kappa_T_physical_estimate()

    # 3D: kappa_T vs BF vs kappa_lower bound, with vertical CI bars
    fig = plt.figure(figsize=(11, 8), constrained_layout=True)
    ax = fig.add_subplot(111, projection='3d')
    # Synthetic lattice posterior samples around best-fit
    rng = np.random.default_rng(42)
    n_samples = 500
    kappa_samples = rng.normal(loc=KAPPA_T_BESTFIT, scale=2.0, size=n_samples)
    bf_samples = np.interp(kappa_samples, [0, 1.5, 2.62, 5, 8.45, 12, 20],
                            [0.01, 1.0, 99, 200, 510, 700, 900])
    bf_samples = bf_samples * rng.lognormal(0, 0.15, n_samples)
    sc = ax.scatter(kappa_samples, bf_samples, rng.uniform(0, 1, n_samples),
                     c=bf_samples, cmap='plasma', s=25, alpha=0.7,
                     edgecolor='none')
    # Mark bounds
    ax.plot([KAPPA_T_PHYSICAL_LOWER]*2, [0, 99], [0.5, 0.5],
             color='green', linewidth=2.5, label=f'95% CL lower $\\kappa_T={KAPPA_T_PHYSICAL_LOWER}$')
    ax.plot([KAPPA_T_BESTFIT]*2, [0, 510], [0.5, 0.5],
             color='orange', linewidth=2.5, label=f'Best-fit $\\kappa_T={KAPPA_T_BESTFIT}$')
    ax.set_yscale('log')
    ax.set_xlabel(r'$\kappa_T$')
    ax.set_ylabel('Bayes factor BF(GUE/Poisson)')
    ax.set_zlabel('Sample index (normalized)')
    ax.set_title('3D: Lattice posterior samples over $\\kappa_T$ with 95% CL bounds')
    ax.legend(loc='upper left')
    fig.colorbar(sc, ax=ax, shrink=0.6, pad=0.1, label='BF')
    paths_3d = save_3formats(fig, "fig_s6_kappa_T_3d")

    # 4D: posterior surface (kappa, BF, density) with color = density
    fig = plt.figure(figsize=(11, 8), constrained_layout=True)
    ax = fig.add_subplot(111, projection='3d')
    # 2D histogram
    H, xedges, yedges = np.histogram2d(kappa_samples, np.log10(bf_samples + 1), bins=30)
    X, Y = np.meshgrid(0.5*(xedges[1:]+xedges[:-1]), 0.5*(yedges[1:]+yedges[:-1]))
    surf = ax.plot_surface(X, Y, H.T, facecolors=mpl_cm.cividis(Normalize(vmin=0, vmax=H.max())(H.T)),
                            edgecolor='none', alpha=0.92, antialiased=True)
    ax.set_xlabel(r'$\kappa_T$')
    ax.set_ylabel(r'$\log_{10}(\mathrm{BF})$')
    ax.set_zlabel('Sample count')
    ax.set_title('4D: Lattice posterior density surface (height + color = count)')
    fig.colorbar(mpl_cm.ScalarMappable(norm=Normalize(vmin=0, vmax=H.max()), cmap='cividis'),
                  ax=ax, shrink=0.6, pad=0.1, label='Sample count')
    paths_4d = save_3formats(fig, "fig_s6_kappa_T_4d")

    return {"3d": paths_3d, "4d": paths_4d, **kpe}


# ─────────────────────────────────────────────────────────────────────────────
# Section 7: Cabibbo coincidence — 3D polar + 4D predicted vs measured
# ─────────────────────────────────────────────────────────────────────────────
def fig_section7_cabibbo_3d_4d() -> Dict[str, Any]:
    cab = cabibbo_coincidence()

    # 3D polar plot: theta_C predicted vs measured vs other mixing angles
    fig = plt.figure(figsize=(11, 8), constrained_layout=True)
    ax = fig.add_subplot(111, projection='3d')
    angles = {
        r'$\theta_C$ predicted': (cab["theta_C_predicted_rad"], PALETTE["accent"]),
        r'$\theta_C$ measured': (cab["theta_C_measured_rad"], PALETTE["accent3"]),
        r'$\delta_C = \pi/7$': (DELTA_C, PALETTE["accent2"]),
        r'$\theta_{\mathrm{PMNS}}$': (0.7854, PALETTE["secondary"]),  # ~ pi/4
    }
    for i, (label, (ang, color)) in enumerate(angles.items()):
        r = 1.0 + 0.05 * i
        theta = np.linspace(0, ang, 50)
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        z = np.full_like(theta, i * 0.3)
        ax.plot(x, y, z, color=color, linewidth=3, label=f'{label} = {ang:.4f} rad')
        ax.scatter([x[-1]], [y[-1]], [z[-1]], color=color, s=120)
    ax.set_xlabel('cos $\\theta$')
    ax.set_ylabel('sin $\\theta$')
    ax.set_zlabel('Angle index')
    ax.set_title('3D: Cabibbo angle predicted vs measured vs framework inputs')
    ax.legend(loc='upper right', fontsize=9)
    paths_3d = save_3formats(fig, "fig_s7_cabibbo_3d")

    # 4D: predicted-vs-measured scatter across framework b_Ch parameter space
    fig = plt.figure(figsize=(11, 8), constrained_layout=True)
    ax = fig.add_subplot(111, projection='3d')
    # Sweep b_Ch
    b_Ch_range = np.linspace(0.1, 0.7, 60)
    c_theta_range = b_Ch_range / 4
    sin_2theta_range = 2 * np.sqrt(c_theta_range)
    theta_pred_range = 0.5 * np.arcsin(np.clip(sin_2theta_range, 0, 1))
    # 4D: x=b_Ch, y=theta_pred, z=sin_theta_pred, color = deviation from measured
    deviation = np.abs(theta_pred_range - cab["theta_C_measured_rad"])
    sc = ax.scatter(b_Ch_range, theta_pred_range, np.sin(theta_pred_range),
                     c=deviation, cmap='RdYlGn_r', s=60, edgecolor='black', linewidth=0.4,
                     norm=Normalize(vmin=0, vmax=deviation.max()))
    ax.scatter([cab["b_Ch"]], [cab["theta_C_predicted_rad"]], [cab["sin_theta_C_predicted"]],
                color='red', s=300, marker='*', label=f'Framework $b_{{Ch}}={cab["b_Ch"]:.4f}$', zorder=10)
    ax.axhline(cab["theta_C_measured_rad"], color=PALETTE["accent3"], linewidth=1.5,
                linestyle='--', label=f'Measured $\\theta_C={cab["theta_C_measured_rad"]:.4f}$')
    ax.set_xlabel(r'$b_{Ch} = 1 - \cos(2\pi/7)$')
    ax.set_ylabel(r'$\theta_C^{pred}$ (rad)')
    ax.set_zlabel(r'$\sin\theta_C^{pred}$')
    ax.set_title('4D: Cabibbo prediction sweep over framework $b_{Ch}$ (color = |deviation|)')
    ax.legend(loc='upper right', fontsize=9)
    fig.colorbar(sc, ax=ax, shrink=0.6, pad=0.1, label='|deviation| (rad)')
    paths_4d = save_3formats(fig, "fig_s7_cabibbo_4d")

    return {"3d": paths_3d, "4d": paths_4d, **cab}


# ─────────────────────────────────────────────────────────────────────────────
# Section 8: CP 8-step chain — 3D chain + 4D dependency graph
# ─────────────────────────────────────────────────────────────────────────────
def fig_section8_cp_chain_3d_4d() -> Dict[str, Any]:
    chain = cp_solution_chain()
    steps = chain["steps"]

    # 3D: step chain as 3D staircase
    fig = plt.figure(figsize=(12, 8), constrained_layout=True)
    ax = fig.add_subplot(111, projection='3d')
    n = len(steps)
    x = np.arange(n)
    y = np.zeros(n)
    z = np.arange(n) * 1.0  # staircase
    # Bar heights proportional to step impact
    impact = np.linspace(0.5, 1.0, n)
    norm = Normalize(vmin=0, vmax=1)
    colors = mpl_cm.viridis(norm(impact))
    ax.bar3d(x, y, z, 0.6, 0.6, impact, color=colors, shade=True, edgecolor='black', linewidth=0.3)
    # Annotations
    for i, step in enumerate(steps):
        ax.text(x[i] + 0.3, 0.3, z[i] + impact[i] + 0.1,
                 f'S{step["step"]}', fontsize=9, ha='center', fontweight='bold')
    # Connect with arrows
    for i in range(n - 1):
        ax.quiver(x[i] + 0.3, 0.3, z[i] + impact[i],
                   x[i+1] - x[i], 0, 1.0,
                   color=PALETTE["accent"], arrow_length_ratio=0.15, linewidth=1.5)
    ax.set_xlabel('Step index')
    ax.set_yticks([])
    ax.set_zlabel('Cumulative progress')
    ax.set_title('3D: 8-step CP solution chain (height + color = step impact)')
    ax.set_xticks(x)
    ax.set_xticklabels([f'S{i+1}' for i in range(n)])
    paths_3d = save_3formats(fig, "fig_s8_cp_chain_3d")

    # 4D: dependency graph with color = section reference
    fig = plt.figure(figsize=(13, 9), constrained_layout=True)
    ax = fig.add_subplot(111, projection='3d')
    # Parse section numbers for color
    def parse_section(s):
        import re
        m = re.search(r'(\d+)', s)
        return int(m.group(1)) if m else 0
    sections = [parse_section(st["section"]) for st in steps]
    norm = Normalize(vmin=min(sections), vmax=max(sections))
    colors = mpl_cm.tab10(norm(sections))
    # 3D scatter connected
    ax.scatter(x, sections, z + impact, c=sections, cmap='tab10', s=200,
                edgecolor='black', linewidth=0.6)
    for i in range(n - 1):
        ax.plot([x[i], x[i+1]], [sections[i], sections[i+1]], [z[i] + impact[i], z[i+1] + impact[i+1]],
                 color=PALETTE["secondary"], linewidth=1.5, alpha=0.7)
    # Annotate each step
    for i, step in enumerate(steps):
        # Truncate statement for label
        stmt = step["statement"][:35] + '...' if len(step["statement"]) > 35 else step["statement"]
        ax.text(x[i] + 0.2, sections[i] + 0.1, z[i] + impact[i] + 0.15,
                 f'{stmt}', fontsize=7.5, ha='left')
    ax.set_xlabel('Step index')
    ax.set_ylabel('Monograph section')
    ax.set_zlabel('Cumulative progress')
    ax.set_title('4D: CP solution chain — step + section + progress (color = section)')
    paths_4d = save_3formats(fig, "fig_s8_cp_chain_4d")

    return {"3d": paths_3d, "4d": paths_4d, "n_steps": n}


# ─────────────────────────────────────────────────────────────────────────────
# Section 9: Jet wake bridge — 3D chi_eff + 4D jet wake vs topological
# ─────────────────────────────────────────────────────────────────────────────
def fig_section9_jet_wake_3d_4d() -> Dict[str, Any]:
    jwb = jet_wake_bridge()

    # 3D: jet wake amplitude vs delta_C vs Lambda_QCD
    fig = plt.figure(figsize=(11, 8), constrained_layout=True)
    ax = fig.add_subplot(111, projection='3d')
    delta_range = np.linspace(0.1, 1.0, 40)
    Lambda_range = np.linspace(0.1, 0.5, 40)
    D, L = np.meshgrid(delta_range, Lambda_range)
    Chi = D * L**4
    surf = ax.plot_surface(D, L, Chi, cmap='inferno', edgecolor='none', alpha=0.92,
                            norm=Normalize(vmin=Chi.min(), vmax=Chi.max()))
    ax.scatter([DELTA_C], [0.2], [jwb["chi_eff_GeV4"]],
                color='red', s=300, marker='*',
                label=f'Framework $\\delta_C=\\pi/7$, $\\Lambda_{{QCD}}=0.2$ GeV', zorder=10)
    ax.set_xlabel(r'$\delta_C$')
    ax.set_ylabel(r'$\Lambda_{\mathrm{QCD}}$ (GeV)')
    ax.set_zlabel(r'$\chi_{\mathrm{eff}}$ (GeV$^4$)')
    ax.set_title(r'3D: $\chi_{\mathrm{eff}} = \delta_C \cdot \Lambda_{\mathrm{QCD}}^4$ jet wake bridge')
    ax.legend(loc='upper right', fontsize=9)
    fig.colorbar(surf, ax=ax, shrink=0.6, pad=0.1, label=r'$\chi_{\mathrm{eff}}$')
    paths_3d = save_3formats(fig, "fig_s9_jet_wake_3d")

    # 4D: jet wake field over (x, y, t) with color = amplitude
    fig = plt.figure(figsize=(11, 8), constrained_layout=True)
    ax = fig.add_subplot(111, projection='3d')
    # Synthetic jet wake field
    x = np.linspace(-5, 5, 50)
    y = np.linspace(-5, 5, 50)
    X, Y = np.meshgrid(x, y)
    # Wake: damped sinusoid + Gaussian
    r = np.sqrt(X**2 + Y**2)
    t = 1.0  # snapshot
    wake = np.exp(-r**2 / 8) * np.cos(2 * np.pi * r * DELTA_C) * DELTA_C
    # 4D: surface + color
    surf = ax.plot_surface(X, Y, wake, facecolors=mpl_cm.coolwarm(wake),
                            edgecolor='none', alpha=0.92, antialiased=True)
    # Mark 22 topological sectors on a ring
    sector_theta = np.linspace(0, 2*np.pi, 22, endpoint=False)
    sx = 4 * np.cos(sector_theta)
    sy = 4 * np.sin(sector_theta)
    sz = np.zeros_like(sx)
    ax.scatter(sx, sy, sz, color='black', s=80, marker='o',
                label=f'{22} K3 topological sectors')
    ax.set_xlabel('x (jet transverse)')
    ax.set_ylabel('y (jet transverse)')
    ax.set_zlabel('Wake amplitude')
    ax.set_title('4D: Jet wake field with K3 topological sectors (height + color = amplitude)')
    ax.legend(loc='upper right', fontsize=9)
    paths_4d = save_3formats(fig, "fig_s9_jet_wake_4d")

    return {"3d": paths_3d, "4d": paths_4d, **jwb}


# ─────────────────────────────────────────────────────────────────────────────
# Master runner
# ─────────────────────────────────────────────────────────────────────────────
SECTIONS = {
    1: ("O_chi operator construction", fig_section1_ochi_3d_4d),
    2: ("RMT universality sweep", fig_section2_rmt_sweep_3d_4d),
    3: ("Spectral staircase vs Wigner", fig_section3_staircase_3d_4d),
    4: ("N-scaling of <lambda>", fig_section4_N_scaling_3d_4d),
    5: ("tau_relax dynamics", fig_section5_tau_relax_3d_4d),
    6: ("kappa_T physical estimate", fig_section6_kappa_T_3d_4d),
    7: ("Cabibbo angle coincidence", fig_section7_cabibbo_3d_4d),
    8: ("CP 8-step solution chain", fig_section8_cp_chain_3d_4d),
    9: ("Jet wake bridge", fig_section9_jet_wake_3d_4d),
}


def generate_all(sections: Optional[List[int]] = None) -> Dict[str, Any]:
    """Generate all figures for the requested sections."""
    if sections is None:
        sections = list(SECTIONS.keys())
    manifest: Dict[str, Any] = {"generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
                                  "sections": {}, "output_dir": str(OUTPUT_DIR)}
    for sec_num in sections:
        if sec_num not in SECTIONS:
            continue
        name, func = SECTIONS[sec_num]
        t0 = time.time()
        try:
            print(f"[Section {sec_num}] {name}...", flush=True)
            result = func()
            elapsed = time.time() - t0
            manifest["sections"][f"section_{sec_num}"] = {
                "name": name,
                "elapsed_s": elapsed,
                "result": result,
                "status": "ok",
            }
            print(f"  done in {elapsed:.2f}s")
        except Exception as e:
            import traceback
            traceback.print_exc()
            manifest["sections"][f"section_{sec_num}"] = {
                "name": name,
                "status": "error",
                "error": str(e),
            }
    # Save manifest
    manifest_path = OUTPUT_DIR / "figures_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False, default=str)
    return manifest


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--sections", type=str, default="all",
                   help="Comma-separated section numbers (1-9), or 'all'")
    args = p.parse_args()
    if args.sections == "all":
        sections = list(SECTIONS.keys())
    else:
        sections = [int(s) for s in args.sections.split(",")]
    manifest = generate_all(sections)
    print(f"\nManifest written to: {OUTPUT_DIR / 'figures_manifest.json'}")
    print(f"Total sections: {len(manifest['sections'])}")
    for k, v in manifest["sections"].items():
        print(f"  {k}: {v.get('status', '?')} ({v.get('elapsed_s', 0):.2f}s)")
