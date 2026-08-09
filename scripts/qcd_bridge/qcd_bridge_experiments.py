#!/usr/bin/env python3
"""
Numerical experiments for the a-C ↔ θ_QCD bridge hypothesis.

Tests five concrete questions:
  E1. Which SU(3)-analogues of δ_C = π/7 (Coxeter/Cartan/center angles)
       are candidates for the Choptyuk formula δ^5 / b = 10^-10?
  E2. What are the relevant Betti numbers of SU(N) instanton moduli spaces?
  E3. Scale-bridge: a_C × (Λ_QCD / M_X)^p = 10^-10 — for which M_X, p?
  E4. Power-law expansions of θ — which (δ, b, n) yield 10^-10?
  E5. Broad (δ, b) sweep — visualization of the surface log10(δ^5 / b).

All results are written to:
  /home/z/my-project/download/qcd_bridge_results.json
  /home/z/my-project/download/qcd_bridge_<figure>.png
"""

import json
import math
import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple

import numpy as np
import matplotlib.font_manager as fm

# Font setup for plots with CJK / Cyrillic fallback safety
for f in (
    '/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
):
    try:
        fm.fontManager.addfont(f)
    except (OSError, ValueError):
        pass

import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['font.sans-serif'] = ['Noto Sans SC', 'DejaVu Sans']
mpl.rcParams['axes.unicode_minus'] = False
mpl.rcParams['figure.dpi'] = 110
mpl.rcParams['savefig.dpi'] = 220

OUT_DIR = '/home/z/my-project/download'
os.makedirs(OUT_DIR, exist_ok=True)

THETA_TARGET = 1e-10           # experimental bound |θ_QCD| from nEDM
A_C_CHOPTYUK = (math.pi / 7) ** 5 / 22   # the Choptyuk a-C value
LAMBDA_QCD_MEV = 200.0         # Λ_QCD ≈ 200 MeV

# ---------------------------------------------------------------------------
# Reference physical mass scales (in GeV)
# ---------------------------------------------------------------------------
MASS_SCALES_GEV = {
    'Planck':    1.22e19,
    'GUT':       1.0e16,
    'SUSY':      1.0e3,
    'top':       173.0,
    'W':         80.4,
    'Higgs':     125.0,
    'QCD':       0.200,
}

# ---------------------------------------------------------------------------
# E1: SU(3)-analogues of δ_C = π/7
# ---------------------------------------------------------------------------
@dataclass
class DeltaCandidate:
    name: str
    formula: str
    value: float
    source: str

def candidates_for_delta_C() -> List[DeltaCandidate]:
    """All mathematically motivated candidates for the SU(3) holonomy angle."""
    pi = math.pi
    cands = [
        # Coxeter / dual Coxeter angles
        DeltaCandidate('pi/N (SU(3), N=3)',          r'$\pi/N$, $N=3$',          pi/3,  'Coxeter number of SU(N) is N'),
        DeltaCandidate('pi/h^∨ (SU(3))',              r'$\pi/h^\vee_{\mathrm{SU}(3)}$', pi/3, 'dual Coxeter h^∨=N for SU(N)'),
        DeltaCandidate('pi/2N (SU(3), 2N=6)',         r'$\pi/(2N)$',              pi/6,  'center Z_N smallest generator'),
        DeltaCandidate('2pi/N (center, SU(3))',       r'$2\pi/N$',                2*pi/3,'center Z_N element'),
        DeltaCandidate('pi/center_order (Z_3)',       r'$\pi/3$',                 pi/3,  'center order = N for SU(N)'),
        # Cartan angles for SU(3) — longest root angle = π/3 (60°), shortest = 2π/3 (120°)
        DeltaCandidate('Cartan long root (SU(3))',    r'$\pi/3$',                 pi/3,  'long-root Weyl reflection'),
        DeltaCandidate('Cartan short (SU(3))',        r'$2\pi/3$',                2*pi/3,'short-root (adjoint weight)'),
        # Original Choptyuk value (for reference)
        DeltaCandidate('pi/7 (Klein, Choptyuk)',      r'$\pi/7$',                 pi/7,  'Hurwitz Γ(2,3,7) order-7 generator'),
        # Pure gauge-group order
        DeltaCandidate('pi/order(PSL(2,7)) = pi/168', r'$\pi/168$',              pi/168,'order of PSL(2,7)'),
        # Dynkin-label angles (SU(3) adjoint has 8 states, weights)
        DeltaCandidate('pi/dim(SU(3)) = pi/8',        r'$\pi/8$',                 pi/8,  'dimension of adjoint rep'),
        # Affine Kac-Moody
        DeltaCandidate('pi/Coxeter_affine (SU(3)~)',  r'$\pi/(N+1)$',             pi/4,  'affine Coxeter number h=N+1'),
        # Instanton holonomies — θ-period 2π on π_3(SU(N))
        DeltaCandidate('pi/N^2 (SU(3), N=3)',         r'$\pi/N^2$',               pi/9,  'higher instanton winding'),
        DeltaCandidate('pi/N^3 (SU(3))',              r'$\pi/N^3$',               pi/27, 'third-order winding'),
        DeltaCandidate('pi/(N·h^∨) = pi/9',           r'$\pi/(N h^\vee)$',        pi/9,  'rank × Coxeter'),
        # Smaller candidates, closer to 10^-10 target
        DeltaCandidate('pi/100',                      r'$\pi/100$',               pi/100,'ad-hoc scale-suppressed'),
        DeltaCandidate('pi/200',                      r'$\pi/200$',               pi/200,'(Λ_QCD/E_Planck)^{-1/2} ∼ 1/200'),
    ]
    return cands

def experiment_E1() -> Dict:
    """Compute δ^5/b for all candidates and a range of b values; report best matches."""
    cands = candidates_for_delta_C()
    # Plausible b_2 candidates for the denominator:
    b_candidates = [
        ('b2=22 (K3)',                22),
        ('b2=2 (Â(K3) Dirac index)',   2),
        ('b2=k=1 (SU(N) instanton)',   1),
        ('b2=k=2 (SU(2), charge 2)',   2),
        ('b2=k=3 (SU(2), charge 3)',   3),
        ('b2=dim(SU(3))=8',            8),
        ('b2=22·8=176 (K3×SU(3)?)',   176),
        ('b2=24 (Leech lattice dim.)', 24),
        ('b2=12 (charge-1 SU(3) dim.)', 12),
    ]
    results = []
    for c in cands:
        for name_b, b in b_candidates:
            val = c.value ** 5 / b
            log_val = math.log10(val) if val > 0 else -100
            # Distance from -10 (the θ_QCD bound log)
            dist = abs(log_val - (-10))
            results.append({
                'candidate': c.name,
                'formula': c.formula,
                'source': c.source,
                'delta': c.value,
                'b_name': name_b,
                'b_value': b,
                'delta5_over_b': val,
                'log10_value': log_val,
                'distance_from_-10': dist,
            })
    # Sort by distance
    results.sort(key=lambda r: r['distance_from_-10'])
    top = results[:15]
    return {
        'all_candidates_count': len(results),
        'top_15_closest_to_1e-10': top,
        'best_match': top[0],
        'full_table': results,
    }

# ---------------------------------------------------------------------------
# E2: Betti numbers of SU(N) instanton moduli spaces
# ---------------------------------------------------------------------------
def experiment_E2() -> Dict:
    """
    Betti numbers of SU(N) instanton moduli spaces M_{k,N}.

    Known results (Atiyah-Hitchin, Donaldson, Kronheimer-Nakajima):
      - Real dimension of framed M_{k,N} on R^4: 4Nk
      - For SU(2), k=1: M ≅ R^4/Z_2 (small resolution) → b_0=1, b_2=1, b_4=1
      - For SU(2), k=2: b_0=1, b_2=2, b_4=3, b_6=2, b_8=1 (with middle corrections)
      - For SU(N), general k: b_2(M_{k,N}) = k  (one for each U(1) factor in the
        ADHM construction that survives the hyperkähler quotient)
      - Euler characteristic: χ(M_{k,N}) = ((N+k-1)! ) / ((N-1)! k!) · ... (Vafa-Witten)
    """
    # Hand-coded known small examples from the ADHM literature
    # (Cf. Nakajima "Instantons on ALE spaces", Kronheimer-Nakajima 1990)
    betti_table = []
    for N in [2, 3, 4, 5]:
        for k in [1, 2, 3, 4, 5]:
            # Real dimension (framed moduli on R^4):
            dim_real = 4 * N * k
            # b_2 — universally equal to k for SU(N) instanton moduli (k U(1)'s from ADHM)
            b2 = k
            # Euler char (Vafa-Witten for SU(N) on K3 with charge k):
            # χ_k = binomial(N+k-1, k) ... a simplified approximation; full formula is more complex
            try:
                chi = math.comb(N + k - 1, k)
            except Exception:
                chi = None
            betti_table.append({
                'group': f'SU({N})',
                'charge_k': k,
                'dim_real': dim_real,
                'b_2': b2,
                'euler_chi_approx': chi,
            })
    # Special: K3 itself (the canonical hyperkähler 4-manifold, used by Choptyuk)
    k3_data = {
        'group': 'K3 (no gauge group)',
        'charge_k': None,
        'dim_real': 4,
        'b_2': 22,
        'euler_chi': 24,
        'hodge_11': 20,
        'hodge_20': 1,
        'holonomy': 'Sp(1) ≅ SU(2)',
    }
    # The Hilbert scheme of k points on K3 has b_2 = 23 (k=1) — adds 1 to K3's b_2
    # Göttsche formula gives Betti numbers; b_2 of Hilb^k(K3) = 23 for k ≥ 1
    hilbert_k3 = []
    for k in [1, 2, 3, 4, 5]:
        hilbert_k3.append({
            'space': f'Hilb^k(K3)',
            'dim_real': 4 * k,
            'b_2': 23,  # universally 23 for Hilb^k(K3) (Beauville)
            'euler_chi': int(math.comb(23 + k - 1, k)),  # Göttsche
        })
    return {
        'instanton_moduli_betti': betti_table,
        'k3_surface': k3_data,
        'hilb_k3_betti': hilbert_k3,
        'summary': {
            'b2_for_SU2_k1': 1,
            'b2_for_SU3_k1': 1,
            'b2_for_SUN_general_k': 'b_2 = k (universal, from ADHM U(1)^k)',
            'b2_for_Hilb_k_K3': 23,
        },
    }

# ---------------------------------------------------------------------------
# E3: Scale-bridge — a_C × (Λ_QCD / M_X)^p = 10^-10
# ---------------------------------------------------------------------------
def experiment_E3() -> Dict:
    """
    Test user's hypothesis: a_C acts at particle/QNM scale, must be rescaled to
    QCD scale. Find p such that a_C × (Λ_QCD / M_X)^p = θ_target.
    """
    a_C = A_C_CHOPTYUK
    ratio = THETA_TARGET / a_C  # ≈ 1.2e-7
    log10_ratio = math.log10(ratio)
    results = []
    for name, M_gev in MASS_SCALES_GEV.items():
        if name == 'QCD':
            continue
        M_mev = M_gev * 1000
        r = LAMBDA_QCD_MEV / M_mev  # = Λ_QCD / M_X
        if r <= 0 or r >= 1:
            continue
        log10_r = math.log10(r)
        if log10_r == 0:
            continue
        p = log10_ratio / log10_r  # exponent that matches target
        # Sanity check: nice rational exponents?
        nice_p = None
        for q in [1, 2, 3, 4, 5, 6, 7, 8, 10]:
            for n in range(1, 12):
                if abs(p - n / q) < 0.02:
                    nice_p = f'{n}/{q}'
                    break
            if nice_p:
                break
        # Compute the actual value at that p
        value = a_C * r ** p
        results.append({
            'scale': name,
            'M_gev': M_gev,
            'ratio_LambdaQCD_over_M': r,
            'log10_ratio': log10_r,
            'exponent_p_needed': p,
            'nearest_nice_rational': nice_p,
            'predicted_theta_at_p': value,
            'log10_predicted': math.log10(value),
            'distance_from_target_log10': abs(math.log10(value) - math.log10(THETA_TARGET)),
        })
    # Also try integer powers p = 1/3, 1/2, 2/3, 1, 2, 3 for each scale
    fixed_powers = [1/3, 1/2, 2/3, 1, 4/3, 3/2, 2, 5/2, 3, 4, 5]
    fixed_results = []
    for p in fixed_powers:
        for name, M_gev in MASS_SCALES_GEV.items():
            if name == 'QCD':
                continue
            r = (LAMBDA_QCD_MEV) / (M_gev * 1000)
            if r <= 0 or r >= 1:
                continue
            val = a_C * r ** p
            fixed_results.append({
                'scale': name,
                'power_p': p,
                'predicted_theta': val,
                'log10_value': math.log10(val) if val > 0 else -100,
                'distance_from_-10': abs(math.log10(val) + 10) if val > 0 else 100,
            })
    fixed_results.sort(key=lambda r: r['distance_from_-10'])
    return {
        'a_C_value': a_C,
        'target_theta': THETA_TARGET,
        'ratio_target_over_aC': ratio,
        'log10_ratio': log10_ratio,
        'per_scale_p': results,
        'best_fixed_power_matches': fixed_results[:10],
    }

# ---------------------------------------------------------------------------
# E4: θ power-law decompositions — what (δ, b, n) gives 10^-10?
# ---------------------------------------------------------------------------
def experiment_E4() -> Dict:
    """
    Given a generalized Choptyuk-type formula δ^n / b = 10^-10,
    find which (n, b, δ) tuples are consistent.
    """
    target = THETA_TARGET
    log10_target = math.log10(target)
    # For fixed n in {2, 3, 4, 5, 6, 7, 8, 10, 12}, compute required δ
    rows = []
    for n in [2, 3, 4, 5, 6, 7, 8, 10, 12]:
        for b in [1, 2, 8, 12, 22, 23, 24, 176]:
            # δ^n = target * b  =>  δ = (target * b)^(1/n)
            inside = target * b
            delta_required = inside ** (1.0 / n)
            # Identify candidate natural angle
            pi_over = math.pi / delta_required if delta_required > 0 else float('inf')
            log10_delta = math.log10(delta_required) if delta_required > 0 else -100
            rows.append({
                'power_n': n,
                'b': b,
                'delta_required_for_1e-10': delta_required,
                'log10_delta': log10_delta,
                'pi_over_N_equivalent': pi_over,
                'comment': 'pi/N' if abs(pi_over - round(pi_over)) < 0.05 and pi_over > 1 else '',
            })
    # Find rows where pi_over_N_equivalent is close to an integer (natural N)
    natural_matches = [r for r in rows if r['pi_over_N_equivalent'] > 1
                       and abs(r['pi_over_N_equivalent'] - round(r['pi_over_N_equivalent'])) < 0.1]
    # Also: which n gives "delta = π/7" exactly the right answer (if any)?
    pi_over_7 = math.pi / 7
    matches_for_pi7 = []
    for n in range(2, 30):
        for b in [1, 2, 8, 12, 22, 23, 24, 176]:
            val = pi_over_7 ** n / b
            log_v = math.log10(val) if val > 0 else -100
            if abs(log_v + 10) < 1.5:  # within 1.5 orders of magnitude
                matches_for_pi7.append({
                    'power_n': n,
                    'b': b,
                    'value': val,
                    'log10_value': log_v,
                    'distance_from_-10': abs(log_v + 10),
                })
    matches_for_pi7.sort(key=lambda r: r['distance_from_-10'])
    return {
        'delta_required_table': rows,
        'natural_pi_over_N_matches': natural_matches[:15],
        'matches_for_pi_over_7': matches_for_pi7[:10],
    }

# ---------------------------------------------------------------------------
# E5: Broad (δ, b) sweep — visualization
# ---------------------------------------------------------------------------
def experiment_E5() -> Dict:
    """
    Sweep log10(δ^5 / b) over δ ∈ (0.001, 1), b ∈ (1, 200).
    Identify the contour at log10 = -10 (the θ_QCD target).
    """
    delta_grid = np.logspace(-3, 0, 400)
    b_grid = np.linspace(1, 200, 400)
    D, B = np.meshgrid(delta_grid, b_grid)
    Z = np.log10(D ** 5 / B)
    # Plot
    fig, ax = plt.subplots(figsize=(10, 7), constrained_layout=True)
    levels = np.arange(-15, 1.5, 0.5)
    cs = ax.contourf(D, B, Z, levels=levels, cmap='viridis_r', extend='both')
    cbar = fig.colorbar(cs, ax=ax, label=r'$\log_{10}(\delta^5 / b)$')
    # Mark target contour log10 = -10
    cs2 = ax.contour(D, B, Z, levels=[-10], colors='red', linewidths=2.5)
    ax.clabel(cs2, fmt=r'$\log_{10}=-10$ ($\theta_{\mathrm{QCD}}$)', fontsize=10, colors='red')
    # Mark a_C point
    delta_C = math.pi / 7
    ax.plot(delta_C, 22, 'o', color='#FF6B35', markersize=14,
            markeredgecolor='white', markeredgewidth=2,
            label=r'$a_C$ Choptyuk: $\delta=\pi/7,\; b_2=22$')
    ax.annotate(f'$a_C$ = {A_C_CHOPTYUK:.2e}\n'
                r'$\log_{10}=-3.08$',
                xy=(delta_C, 22), xytext=(delta_C * 4, 50),
                fontsize=10, color='#FF6B35',
                arrowprops=dict(arrowstyle='->', color='#FF6B35', lw=1.5))
    # Mark a few SU(3) candidates
    su3_points = [
        (math.pi / 3, 1, r'$\pi/3$, $b=k=1$'),
        (math.pi / 6, 1, r'$\pi/6$, $b=1$'),
        (math.pi / 9, 1, r'$\pi/9$, $b=1$'),
        (math.pi / 27, 1, r'$\pi/27$, $b=1$'),
    ]
    for d, b, lab in su3_points:
        ax.plot(d, b, 's', color='#00C2A8', markersize=10,
                markeredgecolor='white', markeredgewidth=1.5)
        ax.annotate(lab, xy=(d, b), xytext=(d * 1.4, b + 12),
                    fontsize=9, color='#006B6B')
    ax.set_xscale('log')
    ax.set_xlabel(r'$\delta$ (spinorial holonomy angle)', fontsize=12)
    ax.set_ylabel(r'$b$ (Betti-like denominator)', fontsize=12)
    ax.set_title(r'Choptyuk surface $\log_{10}(\delta^5/b)$ — '
                 r'red contour = $\theta_{\mathrm{QCD}}$ target $10^{-10}$',
                 fontsize=12)
    ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
    out_path = os.path.join(OUT_DIR, 'qcd_bridge_E5_sweep.png')
    fig.savefig(out_path, bbox_inches='tight')
    plt.close(fig)
    return {
        'figure': out_path,
        'delta_range': [float(delta_grid.min()), float(delta_grid.max())],
        'b_range': [float(b_grid.min()), float(b_grid.max())],
        'a_C_value': A_C_CHOPTYUK,
        'log10_a_C': math.log10(A_C_CHOPTYUK),
        'theta_target_log10': -10,
        'comment': 'a_C lives at log10 = -3.08, far above the θ=10^-10 contour.',
    }

# ---------------------------------------------------------------------------
# Visualizations: log-scale δ_eff vs (δ, b₂) heatmap (also separate)
# ---------------------------------------------------------------------------
def make_log_scale_curve_figure() -> str:
    """
    One-dimensional slice: log10(δ_eff) vs δ for several b values.
    Shows where the curve crosses -10.
    """
    delta = np.linspace(0.001, 1.0, 800)
    fig, ax = plt.subplots(figsize=(10, 6.5), constrained_layout=True)
    b_values = [1, 2, 8, 12, 22, 23, 24, 176]
    colors = plt.cm.viridis(np.linspace(0, 0.9, len(b_values)))
    for b, c in zip(b_values, colors):
        log_v = np.log10(delta ** 5 / b)
        ax.plot(delta, log_v, label=f'b = {b}', color=c, lw=2)
    ax.axhline(-10, color='red', ls='--', lw=2,
               label=r'$\theta_{\mathrm{QCD}} = 10^{-10}$ bound')
    ax.axvline(math.pi / 7, color='#FF6B35', ls=':', lw=2,
               label=r'$\delta = \pi/7$ (Choptyuk)')
    ax.set_xlabel(r'$\delta$ (holonomy angle)', fontsize=12)
    ax.set_ylabel(r'$\log_{10}(\delta^5 / b)$', fontsize=12)
    ax.set_title(r'Where does the Choptyuk formula reach $\theta_{\mathrm{QCD}}=10^{-10}$?',
                 fontsize=12)
    ax.set_xlim(0, 1)
    ax.set_ylim(-15, 2)
    ax.grid(alpha=0.3)
    ax.legend(loc='lower left', fontsize=10, ncol=2)
    out = os.path.join(OUT_DIR, 'qcd_bridge_log_curve.png')
    fig.savefig(out, bbox_inches='tight')
    plt.close(fig)
    return out

# ---------------------------------------------------------------------------
# Visualization: scale ladder — LIGO ↔ particle ↔ QCD
# ---------------------------------------------------------------------------
def make_scale_ladder_figure() -> str:
    """
    Horizontal log-scale ladder from QCD (~10^-15 m) to LIGO/QNM (~10^5 m).
    Marks a_C and shows the ~20 orders-of-magnitude gap.
    """
    fig, ax = plt.subplots(figsize=(12, 5), constrained_layout=True)
    # Length scales in meters (log10)
    points = [
        (-15, r'QCD / nucleon', r'$\sim 10^{-15}$ m', '#1f77b4'),
        (-18, r'electroweak (W,Z)', r'$\sim 10^{-18}$ m', '#2ca02c'),
        (-22, r'Planck length', r'$\sim 10^{-35}$ m → rescale', '#d62728'),
        (-10, r'atom', r'$\sim 10^{-10}$ m', '#9467bd'),
        (-7,  r'particle exp.', r'$\sim 10^{-7}$ m', '#8c564b'),
        (0,   r'human', r'$\sim 1$ m', '#7f7f7f'),
        (5,   r'LIGO / QNM BH', r'$\sim 10^{5}$ m (10^2 km)', '#FF6B35'),
    ]
    for x, lab, sub, color in points:
        ax.plot(x, 0, 'o', markersize=22, color=color, zorder=3,
                markeredgecolor='white', markeredgewidth=2)
        ax.annotate(f'{lab}\n{sub}', xy=(x, 0), xytext=(x, 0.6),
                    ha='center', va='bottom', fontsize=10,
                    arrowprops=dict(arrowstyle='-', color=color, lw=1.2))
    # Arrow showing the "scale bridge"
    ax.annotate('', xy=(-15, -0.4), xytext=(5, -0.4),
                arrowprops=dict(arrowstyle='<->', color='#FF6B35', lw=2.5))
    ax.text(-5, -0.55,
            r'$\sim 20$ orders of magnitude: '
            r'if $a_C$ is "particle/QNM-scale", what rescaling reaches $\theta_{\mathrm{QCD}}$?',
            ha='center', fontsize=11, color='#FF6B35', fontweight='bold')
    ax.set_xlim(-30, 12)
    ax.set_ylim(-1.2, 1.2)
    ax.set_yticks([])
    ax.set_xlabel(r'$\log_{10}(\mathrm{length} / \mathrm{m})$', fontsize=12)
    ax.set_title('Scale ladder — from QCD to LIGO/QNM gravitational waves',
                 fontsize=13)
    # Hide top/right spines
    for s in ['top', 'right', 'left']:
        ax.spines[s].set_visible(False)
    out = os.path.join(OUT_DIR, 'qcd_bridge_scale_ladder.png')
    fig.savefig(out, bbox_inches='tight')
    plt.close(fig)
    return out

# ---------------------------------------------------------------------------
# Visualization: analogy diagram (Choptyuk ↔ QCD)
# ---------------------------------------------------------------------------
def make_analogy_diagram_figure() -> str:
    """
    Two-column comparison: Choptyuk side vs QCD side, with green arrows for
    parallels and red arrows for divergences.
    """
    fig, ax = plt.subplots(figsize=(13, 8.5), constrained_layout=True)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Two background panels
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    left = FancyBboxPatch((0.3, 0.5), 5.2, 9.0, boxstyle='round,pad=0.15',
                          facecolor='#EAF2FB', edgecolor='#1F77B4', lw=2)
    right = FancyBboxPatch((6.5, 0.5), 5.2, 9.0, boxstyle='round,pad=0.15',
                           facecolor='#FDECEC', edgecolor='#D62728', lw=2)
    ax.add_patch(left); ax.add_patch(right)

    ax.text(2.9, 9.4, 'CHOPTYUK  a-C',  ha='center', fontsize=14, fontweight='bold', color='#1F77B4')
    ax.text(9.1, 9.4, 'QCD  θ-term',   ha='center', fontsize=14, fontweight='bold', color='#D62728')

    rows = [
        ('Geometry',        r'Klein quartic $\Gamma(2,3,7)$',              r'$SU(3)$ gauge theory'),
        ('Holonomy angle',  r'$\delta_C = \pi/7$',                         r'$\theta$ (vacuum angle)'),
        ('Topological charge', r'genus $g=3$, $b_2(K3)=22$',               r'$Q = (8\pi^2)^{-1}\int \mathrm{tr}(F\wedge\tilde F) \in Z$'),
        ('Origin of smallness', r'$(\pi/7)^5/22 \approx 1/1208$',          r'NO natural suppression'),
        ('CP violation?',   r'NO — real correction',                       r'YES — CP-odd'),
        ('Operator',        r'$\lambda_1(D^2_{\sigma_0})$ shift',          r'$i\theta\, Q$ in action'),
        ('Symmetry',        r'PSL(2,7) (geometric)',                       r'PQ (approx. global U(1))'),
        ('Magnitudes',      r'$a_C \sim 10^{-3}$, $a_C/\pi^2 \sim 10^{-4}$', r'$|\theta| < 10^{-10}$'),
        ('Solution mechanism', r'geometry fixed; no tuning',               r'axion relaxation (PQ)'),
    ]

    y = 8.8
    for label, l_text, r_text in rows:
        ax.text(2.9, y, l_text, ha='center', fontsize=10, color='#0B3D6E')
        ax.text(9.1, y, r_text, ha='center', fontsize=10, color='#7A1212')
        ax.text(0.45, y, label, ha='left', fontsize=9, color='#444', style='italic')
        # Connection line: green for parallel, red for divergence
        color = '#2CA02C' if label in ('Geometry', 'Topological charge', 'Holonomy angle') else '#D62728'
        ls = '-' if color == '#2CA02C' else '--'
        ax.plot([5.5, 6.5], [y, y], color=color, lw=1.5, ls=ls)
        y -= 0.85

    # Header band
    ax.text(6, 0.15, 'green = structural parallel     red dashed = conceptual divergence',
            ha='center', fontsize=10, color='#444', style='italic')
    out = os.path.join(OUT_DIR, 'qcd_bridge_analogy.png')
    fig.savefig(out, bbox_inches='tight', dpi=220)
    plt.close(fig)
    return out

# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def main():
    print('=' * 78)
    print('NUMERICAL EXPERIMENTS — a-C ↔ θ_QCD bridge hypothesis')
    print('=' * 78)

    print('\n[E1] SU(3)-analogues of δ_C = π/7 ...')
    E1 = experiment_E1()
    print(f'   Best match: {E1["best_match"]["candidate"]} with b={E1["best_match"]["b_value"]}, '
          f'log10 = {E1["best_match"]["log10_value"]:.3f}, '
          f'distance from -10 = {E1["best_match"]["distance_from_-10"]:.3f}')

    print('\n[E2] Betti numbers of SU(N) instanton moduli spaces ...')
    E2 = experiment_E2()
    for r in E2['instanton_moduli_betti'][:6]:
        print(f'   {r["group"]}, k={r["charge_k"]}: dim={r["dim_real"]}, b_2={r["b_2"]}')

    print('\n[E3] Scale-bridge: a_C × (Λ_QCD/M_X)^p = 10^-10 ...')
    E3 = experiment_E3()
    for r in E3['per_scale_p']:
        nice = r['nearest_nice_rational'] or '—'
        print(f'   M_X={r["scale"]:>8s}: p_needed = {r["exponent_p_needed"]:.4f} '
              f'(nice {nice}); predicted θ = {r["predicted_theta_at_p"]:.3e}')

    print('\n[E4] Power-law decompositions ...')
    E4 = experiment_E4()
    print(f'   Natural π/N matches found: {len(E4["natural_pi_over_N_matches"])}')
    print(f'   Best π/7 matches (varying n):')
    for r in E4['matches_for_pi_over_7'][:5]:
        print(f'     n={r["power_n"]}, b={r["b"]}: log10 = {r["log10_value"]:.3f} '
              f'(distance {r["distance_from_-10"]:.3f})')

    print('\n[E5] Broad (δ, b) sweep + visualization ...')
    E5 = experiment_E5()
    print(f'   Figure: {E5["figure"]}')
    print(f'   a_C log10 = {E5["log10_a_C"]:.3f} vs target -10.000')

    # Additional visualizations
    print('\n[FIG] Log-scale curve ...')
    log_fig = make_log_scale_curve_figure()
    print(f'   {log_fig}')

    print('\n[FIG] Scale ladder ...')
    ladder_fig = make_scale_ladder_figure()
    print(f'   {ladder_fig}')

    print('\n[FIG] Analogy diagram ...')
    analogy_fig = make_analogy_diagram_figure()
    print(f'   {analogy_fig}')

    # Save consolidated results
    results = {
        'metadata': {
            'target_theta_QCD': THETA_TARGET,
            'a_C_choptyuk':     A_C_CHOPTYUK,
            'log10_a_C':        math.log10(A_C_CHOPTYUK),
            'log10_target':     math.log10(THETA_TARGET),
            'orders_of_magnitude_gap': math.log10(A_C_CHOPTYUK) - math.log10(THETA_TARGET),
            'lambda_QCD_MeV':   LAMBDA_QCD_MEV,
        },
        'E1_delta_candidates': E1,
        'E2_instanton_betti':  E2,
        'E3_scale_bridge':     E3,
        'E4_theta_expansions': E4,
        'E5_sweep':            E5,
        'figures': {
            'log_curve':       log_fig,
            'scale_ladder':    ladder_fig,
            'analogy_diagram': analogy_fig,
            'sweep_heatmap':   E5['figure'],
        },
    }
    out_json = os.path.join(OUT_DIR, 'qcd_bridge_results.json')
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str, ensure_ascii=False)
    print(f'\n✓ All results saved to: {out_json}')
    print(f'✓ Figures saved to: {OUT_DIR}/qcd_bridge_*.png')
    print('\n' + '=' * 78)
    print('VERDICT PREVIEW')
    print('=' * 78)
    print(f'a_C magnitude:        {A_C_CHOPTYUK:.3e}  (log10 = {math.log10(A_C_CHOPTYUK):+.3f})')
    print(f'θ_QCD target:         {THETA_TARGET:.0e}  (log10 = {math.log10(THETA_TARGET):+.3f})')
    print(f'Orders of magnitude:  {math.log10(A_C_CHOPTYUK) - math.log10(THETA_TARGET):.2f}')
    best = E3['best_fixed_power_matches'][0]
    print(f'Best scale-bridge:    a_C × (Λ_QCD/M_{best["scale"]})^{best["power_p"]:.4f} '
          f'= {best["predicted_theta"]:.3e}')
    print(f'                       distance from target = {best["distance_from_-10"]:.3f} log10 units')

if __name__ == '__main__':
    main()
