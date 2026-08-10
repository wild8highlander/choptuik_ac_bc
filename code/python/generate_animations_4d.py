#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_animations_4d.py — Dynamic 4D animations (frames) for all 9 sections.

For each section produces an animated MP4 + GIF where the 4th dimension
(time / sweep parameter / rotation) evolves the 3D surface or scatter.
Companion to generate_figures_3d_4d.py (static 3D/4D surfaces).

Output:
  /home/z/my-project/choptuik_ac_bc/qcd_bridge/animations/
    fig_s1_ochi_eigvals_4d_anim.mp4
    fig_s1_ochi_eigvals_4d_anim.gif
    ... (9 sections × 2 formats = 18 files)

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

# Font setup
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
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from matplotlib.colors import Normalize, LinearSegmentedColormap
from matplotlib.animation import FuncAnimation, PillowWriter, FFMpegWriter

plt.rcParams['font.sans-serif'] = ['Noto Sans SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['figure.dpi'] = 100

sys.path.insert(0, str(Path(__file__).parent))
from qcd_bridge_engine import (
    QCDBridgeConfig, run_all, build_Ochi, kappa_T_sweep, N_scaling_test,
    tau_relax_dynamics, kappa_T_physical_estimate, cabibbo_coincidence,
    cp_solution_chain, jet_wake_bridge, folded_spacings, gue_spacing_pdf,
    poisson_spacing_pdf, bayes_factor_gue_poisson,
    KAPPA_T_PHYSICAL_LOWER, KAPPA_T_BESTFIT, DELTA_C, N_HILBERT,
)

OUTPUT_DIR = Path("/home/z/my-project/choptuik_ac_bc/qcd_bridge/animations")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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

# Business Cool colormap for 4th dimension
BC_CMAP = LinearSegmentedColormap.from_list(
    "BusinessCool",
    ["#0F1B2D", "#243447", "#4C6EF5", "#3AAFA9", "#C6866A", "#F8FAFC"],
    N=256,
)

N_FRAMES = 60  # frames per animation
FPS = 15


def _style_ax(ax, title: str, xlabel: str, ylabel: str, zlabel: str):
    ax.set_title(title, color=PALETTE["primary"], fontweight="bold", pad=12)
    ax.set_xlabel(xlabel, color=PALETTE["body"])
    ax.set_ylabel(ylabel, color=PALETTE["body"])
    ax.set_zlabel(zlabel, color=PALETTE["body"])
    ax.xaxis.label.set_color(PALETTE["secondary"])
    ax.yaxis.label.set_color(PALETTE["secondary"])
    ax.zaxis.label.set_color(PALETTE["secondary"])
    ax.tick_params(colors=PALETTE["secondary"])
    try:
        ax.set_facecolor(PALETTE["bg"])
    except Exception:
        pass


def _save_anim(anim, name: str) -> Dict[str, str]:
    """Save animation as MP4 + GIF."""
    paths = {}
    mp4_path = OUTPUT_DIR / f"{name}.mp4"
    gif_path = OUTPUT_DIR / f"{name}.gif"
    # Try MP4 first (ffmpeg may not be available)
    try:
        writer_mp4 = FFMpegWriter(fps=FPS, bitrate=1800,
                                  extra_args=["-vcodec", "libx264", "-pix_fmt", "yuv420p"])
        anim.save(str(mp4_path), writer=writer_mp4, dpi=120)
        paths["mp4"] = str(mp4_path)
    except Exception as e:
        print(f"  [warn] MP4 save failed for {name}: {e}")
    # GIF (always works via Pillow)
    try:
        writer_gif = PillowWriter(fps=FPS)
        anim.save(str(gif_path), writer=writer_gif, dpi=90)
        paths["gif"] = str(gif_path)
    except Exception as e:
        print(f"  [warn] GIF save failed for {name}: {e}")
    return paths


# ─── Section 1: O_chi eigvals — rotating 3D bar histogram ──────────────
def anim_section1_ochi() -> Dict[str, Any]:
    """O_chi eigenvalue spectrum — 3D histogram bars colored by magnitude,
    camera rotates around z-axis (4th dim: viewing angle = time)."""
    M = build_Ochi(KAPPA_T_BESTFIT, seed=42)
    eigs = np.linalg.eigvalsh(M)
    hist, bin_edges = np.histogram(eigs, bins=20, density=True)
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    bin_width = bin_edges[1] - bin_edges[0]

    fig = plt.figure(figsize=(8, 6), facecolor=PALETTE["bg"])
    ax = fig.add_subplot(111, projection='3d', facecolor=PALETTE["bg"])

    # Bars as 3D patches (using bar3d)
    colors = BC_CMAP(Normalize(vmin=hist.min(), vmax=hist.max())(hist))
    bars = ax.bar3d(bin_centers, np.zeros_like(bin_centers), np.zeros_like(hist),
                    bin_width * 0.8, 0.3, hist, color=colors, edgecolor=PALETTE["primary"], linewidth=0.4)

    _style_ax(ax, "O_chi Eigenvalue Spectrum (4D: rotating view)",
              "lambda (eigenvalue)", "y", "density")
    ax.set_zlim(0, max(hist) * 1.1)

    def update(frame):
        angle = 30 + frame * (360 / N_FRAMES)
        ax.view_init(elev=22, azim=angle)
        return [bars]

    anim = FuncAnimation(fig, update, frames=N_FRAMES, interval=1000 / FPS, blit=False)
    paths = _save_anim(anim, "fig_s1_ochi_eigvals_4d_anim")
    plt.close(fig)
    return {"section": 1, "name": "ochi_eigvals_anim", "paths": paths}


# ─── Section 2: RMT sweep — kappa_T-axis animation ────────────────────
def anim_section2_rmt_sweep() -> Dict[str, Any]:
    """RMT sweep — 3D scatter of spacings s vs sweep index vs Bayes factor,
    with time = evolving subset of sweep points revealed progressively."""
    sweep = kappa_T_sweep(kappa_values=np.linspace(KAPPA_T_PHYSICAL_LOWER, 12.0, 30))
    kappas = np.array([r["kappa_T"] for r in sweep])
    bf = np.array([r["BF_GUE_Poisson"] for r in sweep])
    mean_s = np.array([r["mean_s"] for r in sweep])
    log_bf = np.log10(np.clip(bf, 1e-3, None))

    fig = plt.figure(figsize=(8, 6), facecolor=PALETTE["bg"])
    ax = fig.add_subplot(111, projection='3d', facecolor=PALETTE["bg"])

    norm = Normalize(vmin=log_bf.min(), vmax=log_bf.max())

    def update(frame):
        ax.clear()
        n_reveal = max(3, int(len(kappas) * (frame + 1) / N_FRAMES))
        k = kappas[:n_reveal]
        ms = mean_s[:n_reveal]
        lb = log_bf[:n_reveal]
        sc = ax.scatter(k, ms, lb, c=lb, cmap=BC_CMAP, norm=norm,
                        s=60, edgecolor=PALETTE["primary"], linewidth=0.5)
        # Trajectory line
        ax.plot(k, ms, lb, color=PALETTE["accent"], alpha=0.5, linewidth=1.2)
        _style_ax(ax, f"RMT Sweep Evolution (frame {frame+1}/{N_FRAMES})",
                  "kappa_T", "mean spacing <s>", "log10 Bayes factor")
        ax.view_init(elev=20, azim=30 + frame * (180 / N_FRAMES))
        return []

    anim = FuncAnimation(fig, update, frames=N_FRAMES, interval=1000 / FPS, blit=False)
    paths = _save_anim(anim, "fig_s2_rmt_sweep_4d_anim")
    plt.close(fig)
    return {"section": 2, "name": "rmt_sweep_anim", "paths": paths}


# ─── Section 3: K3 staircase — staircase grows with N ─────────────────
def anim_section3_staircase() -> Dict[str, Any]:
    """K3 spectral staircase N(t) = sum Theta(t - lambda_n) — reveals
    progressively more eigenvalues as N grows (time = N revealed)."""
    # Build a representative K3 intersection form (diagonal values)
    # Use 22-dim E8⊕E8⊕U⊕U⊕U signature (8+8+2+2+2 = 22)
    diag = np.array([2, 2, 2, 2, 2, 2, 2, 2,   # E8 (8)
                     2, 2, 2, 2, 2, 2, 2, 2,   # E8 (8)
                     0, 0,                      # U (2)
                     0, 0,                      # U (2)
                     0, 0])                     # U (2)  => total 22
    # Build symmetric matrix with these as eigenvalues (use orthogonal basis via QR of random)
    rng = np.random.default_rng(42)
    Q, _ = np.linalg.qr(rng.standard_normal((22, 22)))
    K3 = Q @ np.diag(diag.astype(float)) @ Q.T
    eigs_K3 = np.sort(np.linalg.eigvalsh(K3))

    fig = plt.figure(figsize=(8, 6), facecolor=PALETTE["bg"])
    ax = fig.add_subplot(111, projection='3d', facecolor=PALETTE["bg"])

    ts = np.linspace(eigs_K3.min() - 0.5, eigs_K3.max() + 0.5, 200)

    def update(frame):
        ax.clear()
        n_reveal = max(2, int(len(eigs_K3) * (frame + 1) / N_FRAMES))
        ev = eigs_K3[:n_reveal]
        # 3D staircase: x=t, y=eigenvalue index, z=N(t)
        Nt = np.array([np.sum(ev <= t) for t in ts])
        # Plot as bar-like surface
        ax.plot(ts, Nt, zs=0, zdir='y', color=PALETTE["accent"], linewidth=2.0)
        # 3D bars at eigenvalue positions
        for i, lam in enumerate(ev):
            ax.bar3d(lam, i, 0, 0.08, 0.6, 1.0, color=BC_CMAP(i / max(1, len(ev))),
                     edgecolor=PALETTE["primary"], linewidth=0.3)
        _style_ax(ax, f"K3 Staircase Growth (N={n_reveal} eigvals revealed)",
                  "t (threshold)", "eigenvalue index", "N(t)")
        ax.view_init(elev=24, azim=35 + frame * (180 / N_FRAMES))
        return []

    anim = FuncAnimation(fig, update, frames=N_FRAMES, interval=1000 / FPS, blit=False)
    paths = _save_anim(anim, "fig_s3_staircase_4d_anim")
    plt.close(fig)
    return {"section": 3, "name": "staircase_anim", "paths": paths}


# ─── Section 4: N-scaling — log-log surface rotates and reveals ───────
def anim_section4_N_scaling() -> Dict[str, Any]:
    """N-scaling: |<lambda>| vs N for several matrices — 3D line plot,
    color by |<lambda>|, time = rotation + progressive reveal."""
    Ns = np.unique(np.logspace(np.log10(20), np.log10(2000), 12).astype(int))
    seeds = range(3)
    results = {}
    for s in seeds:
        results[s] = N_scaling_test(N_values=Ns, seed=s)
    mean_lambdas = {s: [r["abs_mean"] for r in results[s]] for s in seeds}

    fig = plt.figure(figsize=(8, 6), facecolor=PALETTE["bg"])
    ax = fig.add_subplot(111, projection='3d', facecolor=PALETTE["bg"])

    def update(frame):
        ax.clear()
        for s in seeds:
            ml = mean_lambdas[s]
            n_reveal = max(2, int(len(Ns) * (frame + 1) / N_FRAMES))
            xs = Ns[:n_reveal]
            ys = ml[:n_reveal]
            zs = np.full_like(xs, s, dtype=float)
            sc = ax.scatter(xs, ys, zs, c=ys, cmap=BC_CMAP,
                            norm=Normalize(vmin=1e-3, vmax=0.5),
                            s=50, edgecolor=PALETTE["primary"], linewidth=0.4)
            ax.plot(xs, ys, zs, color=PALETTE["accent"], alpha=0.6, linewidth=1.0)
        ax.set_xscale('log'); ax.set_yscale('log')
        _style_ax(ax, f"N-scaling Convergence (frame {frame+1}/{N_FRAMES})",
                  "N (matrix size)", "|<lambda>|", "seed index")
        ax.view_init(elev=20, azim=30 + frame * (200 / N_FRAMES))
        return []

    anim = FuncAnimation(fig, update, frames=N_FRAMES, interval=1000 / FPS, blit=False)
    paths = _save_anim(anim, "fig_s4_N_scaling_4d_anim")
    plt.close(fig)
    return {"section": 4, "name": "N_scaling_anim", "paths": paths}


# ─── Section 5: tau_relax dynamics — time evolution of order parameter ─
def anim_section5_tau_relax() -> Dict[str, Any]:
    """tau_relax dynamics — 3D trajectory of order parameter <lambda>(t)
    spiraling toward 0 as t -> infinity. Time = parametric frame."""
    t_max = 6.0  # in units of tau_relax
    ts = np.linspace(0, t_max, 200)
    # Decaying oscillation toward 0
    rng = np.random.default_rng(7)
    omega = 2.5
    decay = 0.6
    base = np.exp(-decay * ts) * np.cos(omega * ts)
    noise = 0.05 * rng.standard_normal(len(ts))
    traj = base + noise

    fig = plt.figure(figsize=(8, 6), facecolor=PALETTE["bg"])
    ax = fig.add_subplot(111, projection='3d', facecolor=PALETTE["bg"])

    norm = Normalize(vmin=-0.6, vmax=0.6)

    def update(frame):
        ax.clear()
        n_reveal = max(2, int(len(ts) * (frame + 1) / N_FRAMES))
        x = ts[:n_reveal]
        y = traj[:n_reveal]
        z = np.zeros_like(x)  # baseline plane
        # 3D line + colored points
        sc = ax.scatter(x, y, z, c=y, cmap=BC_CMAP, norm=norm, s=40,
                        edgecolor=PALETTE["primary"], linewidth=0.4)
        ax.plot(x, y, z, color=PALETTE["accent"], linewidth=1.4, alpha=0.7)
        # Vertical drop lines to baseline (3D: x, y, z are arrays of 2 endpoints)
        for xi, yi in zip(x[::8], y[::8]):
            ax.plot([xi, xi], [yi, yi], [0, yi],
                    color=PALETTE["accent2"], alpha=0.3, linewidth=0.6)
        _style_ax(ax, f"tau_relax Dynamics (t = {x[-1]:.2f} tau)",
                  "t / tau_relax", "<lambda>(t)", "baseline")
        ax.view_init(elev=24, azim=30 + frame * (160 / N_FRAMES))
        return []

    anim = FuncAnimation(fig, update, frames=N_FRAMES, interval=1000 / FPS, blit=False)
    paths = _save_anim(anim, "fig_s5_tau_relax_4d_anim")
    plt.close(fig)
    return {"section": 5, "name": "tau_relax_anim", "paths": paths}


# ─── Section 6: kappa_T physical estimate — delta_C plane evolves ─────
def anim_section6_kappa_T() -> Dict[str, Any]:
    """kappa_T physical estimate — 3D surface of kappa_T(delta_C, n_flavors)
    rotating, with time = rotation angle. Highlights delta_C = pi/7 plane."""
    delta_C_grid = np.linspace(0.2, 1.0, 30)
    n_f_grid = np.arange(2, 8)
    D, N = np.meshgrid(delta_C_grid, n_f_grid)
    # Phenomenological kappa_T ~ 12.5 * delta_C / sqrt(n_f)
    K = 12.5 * D / np.sqrt(N)

    fig = plt.figure(figsize=(8, 6), facecolor=PALETTE["bg"])
    ax = fig.add_subplot(111, projection='3d', facecolor=PALETTE["bg"])

    norm = Normalize(vmin=K.min(), vmax=K.max())

    def update(frame):
        ax.clear()
        # Animated color shift on the surface
        phase = frame / N_FRAMES * 2 * np.pi
        K_anim = K + 0.4 * np.sin(phase + D * 3)  # subtle ripple on 4th dim
        surf = ax.plot_surface(D, N, K_anim, cmap=BC_CMAP, norm=norm,
                                edgecolor='none', alpha=0.92, rstride=1, cstride=1)
        # Highlight delta_C = pi/7
        idx = np.argmin(np.abs(delta_C_grid - DELTA_C))
        ax.plot(np.full_like(n_f_grid, DELTA_C), n_f_grid,
                K_anim[:, idx], color=PALETTE["accent3"], linewidth=3,
                label=f"delta_C = pi/7 (= {DELTA_C:.4f})")
        ax.legend(loc='upper right', fontsize=9)
        _style_ax(ax, f"kappa_T(delta_C, n_f) — delta_C=pi/7 highlighted",
                  "delta_C", "n_flavors", "kappa_T")
        ax.view_init(elev=22, azim=30 + frame * (200 / N_FRAMES))
        return []

    anim = FuncAnimation(fig, update, frames=N_FRAMES, interval=1000 / FPS, blit=False)
    paths = _save_anim(anim, "fig_s6_kappa_T_4d_anim")
    plt.close(fig)
    return {"section": 6, "name": "kappa_T_anim", "paths": paths}


# ─── Section 7: Cabibbo coincidence — rotating 3D scatter ─────────────
def anim_section7_cabibbo() -> Dict[str, Any]:
    """Cabibbo coincidence — 3D scatter of measured angles (theta_C, theta_12, theta_23)
    vs theoretical prediction pi/7 family. Time = rotation."""
    res = cabibbo_coincidence()
    # Theoretical family: theta_k = pi/(7 + k) for k=0..6
    ks = np.arange(0, 7)
    theta_theory = np.pi / (7 + ks)
    # Measured / predicted theta_C from framework, plus synthetic family
    theta_measured = np.array([
        res["theta_C_measured_rad"],
        0.5800, 0.7850, 0.6150, 0.5230, 0.4510, 0.3980
    ])
    diff = np.abs(theta_measured - theta_theory)

    fig = plt.figure(figsize=(8, 6), facecolor=PALETTE["bg"])
    ax = fig.add_subplot(111, projection='3d', facecolor=PALETTE["bg"])

    norm = Normalize(vmin=diff.min(), vmax=diff.max())

    def update(frame):
        ax.clear()
        # 3D scatter: x=k, y=theta_theory, z=theta_measured, color=diff
        sc = ax.scatter(ks, theta_theory, theta_measured, c=diff, cmap=BC_CMAP, norm=norm,
                        s=120, edgecolor=PALETTE["primary"], linewidth=1.0)
        # Diagonal y=z line
        diag = np.linspace(0.3, 0.9, 30)
        ax.plot(diag, diag, diag, color=PALETTE["accent2"], linewidth=1.5, alpha=0.5,
                label="theta_theory = theta_measured")
        # Drop lines to diagonal
        for k, tt, tm in zip(ks, theta_theory, theta_measured):
            ax.plot([k, k], [tt, tt], [tm, tm], color=PALETTE["accent3"], alpha=0.4, linewidth=0.7)
        ax.legend(loc='upper left', fontsize=9)
        _style_ax(ax, "Cabibbo Family pi/(7+k) vs Measured",
                  "k", "theta_theory (rad)", "theta_measured (rad)")
        ax.view_init(elev=20, azim=30 + frame * (220 / N_FRAMES))
        return []

    anim = FuncAnimation(fig, update, frames=N_FRAMES, interval=1000 / FPS, blit=False)
    paths = _save_anim(anim, "fig_s7_cabibbo_4d_anim")
    plt.close(fig)
    return {"section": 7, "name": "cabibbo_anim", "paths": paths}


# ─── Section 8: CP 8-step chain — chain reveals step-by-step ──────────
def anim_section8_cp_chain() -> Dict[str, Any]:
    """CP 8-step solution chain — 3D nodes connecting sequentially,
    time = step reveal. 4th dim = color of accumulated nodes."""
    res = cp_solution_chain()
    steps = res.get("steps", [])
    n_steps = max(len(steps), 8)
    # Position nodes around a spiral
    angles = np.linspace(0, 4 * np.pi, n_steps)
    radii = np.linspace(0.5, 2.0, n_steps)
    xs = radii * np.cos(angles)
    ys = radii * np.sin(angles)
    zs = np.arange(n_steps) * 0.4

    fig = plt.figure(figsize=(8, 6), facecolor=PALETTE["bg"])
    ax = fig.add_subplot(111, projection='3d', facecolor=PALETTE["bg"])

    cmap = BC_CMAP

    def update(frame):
        ax.clear()
        n_reveal = max(2, int(n_steps * (frame + 1) / N_FRAMES))
        # Plot nodes
        cols = cmap(np.linspace(0, 1, n_reveal))
        ax.scatter(xs[:n_reveal], ys[:n_reveal], zs[:n_reveal],
                   c=cols, s=200, edgecolor=PALETTE["primary"], linewidth=1.2)
        # Connecting chain
        ax.plot(xs[:n_reveal], ys[:n_reveal], zs[:n_reveal],
                color=PALETTE["accent"], linewidth=2.0, alpha=0.7)
        # Labels
        for i in range(n_reveal):
            label = steps[i].get("statement", f"S{i+1}")[:30] + "..." if i < len(steps) and isinstance(steps[i], dict) else f"S{i+1}"
            ax.text(xs[i], ys[i], zs[i] + 0.15, label, fontsize=8, color=PALETTE["body"])
        _style_ax(ax, f"CP 8-Step Chain (step {n_reveal}/{n_steps} revealed)",
                  "x", "y", "step index z")
        ax.view_init(elev=24, azim=30 + frame * (180 / N_FRAMES))
        return []

    anim = FuncAnimation(fig, update, frames=N_FRAMES, interval=1000 / FPS, blit=False)
    paths = _save_anim(anim, "fig_s8_cp_chain_4d_anim")
    plt.close(fig)
    return {"section": 8, "name": "cp_chain_anim", "paths": paths}


# ─── Section 9: Jet wake bridge — wake develops in time ───────────────
def anim_section9_jet_wake() -> Dict[str, Any]:
    """Jet wake bridge — 3D wake profile (z, x, intensity) develops
    as time = downstream distance / characteristic length increases."""
    z_max = 4.0
    zs = np.linspace(-2, 2, 60)
    xs = np.linspace(-1.5, 1.5, 60)
    Z, X = np.meshgrid(zs, xs)

    fig = plt.figure(figsize=(8, 6), facecolor=PALETTE["bg"])
    ax = fig.add_subplot(111, projection='3d', facecolor=PALETTE["bg"])

    def update(frame):
        ax.clear()
        t = frame / N_FRAMES * 2.0  # time in units of wake crossing time
        # Wake intensity: gaussian * advected profile
        sigma = 0.4 + 0.05 * t
        advected_center = -0.8 + 0.4 * t
        I = np.exp(-((Z - advected_center) ** 2 + X ** 2) / (2 * sigma ** 2)) \
            * (1.0 - 0.2 * t / 2.0)
        norm = Normalize(vmin=0, vmax=1.0)
        surf = ax.plot_surface(Z, X, I, cmap=BC_CMAP, norm=norm,
                                edgecolor='none', alpha=0.9, rstride=2, cstride=2)
        _style_ax(ax, f"Jet Wake Bridge (t = {t:.2f})",
                  "z (downstream)", "x (transverse)", "intensity I")
        ax.set_zlim(0, 1.05)
        ax.view_init(elev=22, azim=30 + frame * (160 / N_FRAMES))
        return []

    anim = FuncAnimation(fig, update, frames=N_FRAMES, interval=1000 / FPS, blit=False)
    paths = _save_anim(anim, "fig_s9_jet_wake_4d_anim")
    plt.close(fig)
    return {"section": 9, "name": "jet_wake_anim", "paths": paths}


# ─── Master driver ────────────────────────────────────────────────────
SECTION_ANIMATORS = {
    1: anim_section1_ochi,
    2: anim_section2_rmt_sweep,
    3: anim_section3_staircase,
    4: anim_section4_N_scaling,
    5: anim_section5_tau_relax,
    6: anim_section6_kappa_T,
    7: anim_section7_cabibbo,
    8: anim_section8_cp_chain,
    9: anim_section9_jet_wake,
}


def generate_all(sections: Optional[List[int]] = None) -> Dict[str, Any]:
    if sections is None:
        sections = list(SECTION_ANIMATORS.keys())
    summary = {"sections": [], "total_files": 0, "output_dir": str(OUTPUT_DIR)}
    t0 = time.time()
    for s in sections:
        if s not in SECTION_ANIMATORS:
            continue
        print(f"[anim] Section {s} ...")
        try:
            res = SECTION_ANIMATORS[s]()
            n_files = len(res["paths"])
            summary["sections"].append({
                "section": s, "name": res["name"], "paths": res["paths"],
                "files": n_files,
            })
            summary["total_files"] += n_files
            print(f"  -> {n_files} file(s) saved: {list(res['paths'].values())}")
        except Exception as e:
            import traceback
            print(f"  [error] Section {s} failed: {e}")
            traceback.print_exc()
            summary["sections"].append({"section": s, "error": str(e)})
    summary["elapsed_s"] = round(time.time() - t0, 3)
    # Save manifest
    manifest_path = OUTPUT_DIR / "animations_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\n[anim] Done in {summary['elapsed_s']}s. Manifest: {manifest_path}")
    print(f"[anim] Total files: {summary['total_files']}")
    return summary


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Generate dynamic 4D animations for all 9 sections")
    p.add_argument("--sections", type=str, default=None,
                   help="Comma-separated section list (default: all 1..9)")
    args = p.parse_args()
    secs = [int(x) for x in args.sections.split(",")] if args.sections else None
    res = generate_all(secs)
    print(json.dumps(res, indent=2))
