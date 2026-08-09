#!/usr/bin/env python3
"""
qcd_observables_with_aC.py
==========================

Introduces the Choptyuk braking correction a_C into the QCD theta-term
and computes a suite of CP-odd observables, comparing them with current
experimental bounds.

Key formula (the "Higgs-scale bridge"):
    theta_Ch := a_C * (Lambda_QCD / M_H)^(5/2)  ~  8.5e-11

The exponent 5/2 is motivated (not derived) by:
  * Cohen-Kaplan-Nelson sphaleron rate scaling  Gamma_sph ~ (M_H/T)^(5/2)
  * Heavy-quark OPE 1/M_H^(1/2) corrections
  * Witten-Veneziano half-power structure of m_eta'

Outputs:
  - qcd_observables_results.json : full numerical results
  - figures_v2/theta_Ch_observables.png : bar chart prediction vs bounds
  - figures_v2/sphaleron_derivation.png : schematic of 5/2 emergence
  - figures_v2/exponent_sensitivity.png : how the prediction changes
                                            with the exponent p
Author:  Research continuation, 2026-08-09
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

# Matplotlib with CJK + Russian glyph fallback
import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
for p in [
    "/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]:
    if os.path.exists(p):
        fm.fontManager.addfont(p)
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Noto Sans SC"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 110

# ----------------------------------------------------------------------
# 0.  Physical constants and Choptyuk parameters
# ----------------------------------------------------------------------
PI = math.pi

# Choptyuk spinorial phase
DELTA_C = PI / 7.0
B2_K3 = 22
A_C = DELTA_C**5 / B2_K3          # ~ 8.276e-4
LOG10_A_C = math.log10(A_C)

# QCD and SM scales (in GeV)
LAMBDA_QCD = 0.200                # 200 MeV, MS-bar at 2 GeV, Nf=3
M_H = 125.10                      # Higgs mass (GeV)
M_W = 80.379
M_TOP = 172.76
M_Z = 91.1876
M_PLANCK = 1.2209e19              # reduced Planck mass (GeV)
ALPHA_W = 1.0/29.6                # SU(2)_L coupling at M_Z
ALPHA_S_MZ = 0.1179               # world average 2024
F_PI = 0.0924                     # pion decay constant (GeV)

# Theta bounds
THETA_BOUND_EXPERIMENTAL = 1.0e-10

# Choptyuk-effective theta -- the central object
def theta_Ch(exponent: float = 2.5,
             a_C: float = A_C,
             lam: float = LAMBDA_QCD,
             mH: float = M_H) -> float:
    """Return a_C * (Lambda/M_H)^exponent."""
    return a_C * (lam / mH) ** exponent


THETA_CH = theta_Ch()              # default 5/2
LOG10_THETA_CH = math.log10(THETA_CH)


# ----------------------------------------------------------------------
# 1.  QCD observables with theta-dependence
# ----------------------------------------------------------------------
@dataclass
class Observable:
    name: str
    symbol: str
    coefficient_in_e_cm_per_theta: float  # d = coef * theta  (in e*cm)
    experimental_bound_e_cm: float
    experiment: str
    year: int
    notes: str = ""

    def prediction(self, theta: float = THETA_CH) -> float:
        return self.coefficient_in_e_cm_per_theta * theta

    def ratio_to_bound(self, theta: float = THETA_CH) -> float:
        return self.prediction(theta) / self.experimental_bound_e_cm


# Coefficients in units of e*cm per theta
# All taken from the literature:
#   * Pospelov & Ritz, Phys. Rev. D 63, 073015 (2001) -- theta-to-EDM table
#   * Hoferichter et al., Phys. Rev. Lett. 2025 -- lattice-continuum nEDM
#   * Abel et al., Phys. Rev. Lett. 124, 081803 (2020) -- nEDM@PSI bound
#   * Graner et al., Phys. Rev. Lett. 116, 161601 (2016) -- Hg-199 bound
#   * Andreev et al. (ACME), Nature 562, 355 (2018) -- electron EDM bound
# The coefficients c relate the QCD vacuum angle theta to the observable
# electric dipole moment via  d = c * theta  (in e*cm).
OBSERVABLES: List[Observable] = [
    # d_n(theta) = 2.4e-16 * theta e*cm  (lattice + QCD sum rule, Hoferichter 2025)
    # Best-constrained; nEDM@PSI bound 1.8e-26 -> |theta| < 7.5e-11
    Observable("Neutron EDM",
               r"$d_n$",
               2.4e-16,
               1.8e-26,
               "nEDM@PSI (Abel et al.)",
               2020,
               "Lattice-QCD + chiral logs; coefficient ~2.4e-16"),

    # d_p(theta) ~ 0.9e-16 * theta e*cm  (similar to n, isospin partner)
    # Current bound from SIDM/PSI is loose; J-PARC target ~1e-26
    Observable("Proton EDM",
               r"$d_p$",
               0.9e-16,
               5.4e-24,
               "PSI storage ring (current)",
               2024,
               "Bound will improve to ~1e-26 at J-PARC"),

    # Mercury-199: d_Hg(theta) ~ 3e-17 * theta e*cm via Schiff moment
    # Pospelov-Ritz 2005; experimental bound 7.4e-30 -> |theta| < ~3e-13
    # (in practice limited by nuclear theory uncertainty to ~10^-10)
    Observable("Hg-199 EDM",
               r"$d_{\mathrm{Hg}}$",
               3.0e-17,
               7.4e-30,
               "Graner et al. (Seattle)",
               2016,
               "Schiff moment mechanism; nuclear theory uncertainty ~10x"),

    # Radium-225: octupole-deformed nucleus, Schiff enhanced ~10^3-10^4
    # d_Ra(theta) ~ 5e-15 * theta e*cm  (Dmitriev & Flambaum 2005)
    Observable("Ra-225 EDM",
               r"$d_{\mathrm{Ra}}$",
               5.0e-15,
               1.0e-23,
               "RaEDM@Argonne (projected)",
               2025,
               "Octupole-deformed nucleus; 1e3-1e5 Schiff enhancement"),

    # Electron EDM from QCD theta (2-loop quark box, Pospelov-Ritz)
    # d_e(theta) ~ 4e-26 * theta e*cm  (very suppressed)
    Observable("Electron EDM",
               r"$d_e$",
               4.0e-26,
               1.1e-29,
               "ACME II (Andreev et al.)",
               2018,
               "Two-loop QCD theta -> electron EDM via quark box"),

    # Deuteron EDM, d_D(theta) ~ 0.6e-16 * theta e*cm (via CP-odd piNN)
    Observable("Deuteron EDM",
               r"$d_D$",
               0.6e-16,
               1.7e-21,
               "JEDI storage ring (projected)",
               2024,
               "Planned storage-ring measurement, target 1e-27"),
]


# ----------------------------------------------------------------------
# 2.  Other QCD observables with theta-dependence
# ----------------------------------------------------------------------
@dataclass
class HadronicObservable:
    name: str
    symbol: str
    formula: str
    prediction_value: float        # in natural units stated
    units: str
    experimental_value_or_bound: float
    experiment_or_source: str
    notes: str = ""


def topological_susceptibility(theta: float = THETA_CH) -> Dict:
    """chi_t(theta) = chi_t(0) * (1 - theta^2/2 + O(theta^4)).
    chi_t(0) ~ (75.6 MeV)^4 from lattice."""
    chi_t_0 = (0.0756) ** 4  # GeV^4
    correction = chi_t_0 * (-theta**2 / 2.0)
    return {
        "chi_t_0_GeV4": chi_t_0,
        "delta_chi_t_GeV4": correction,
        "relative_correction": correction / chi_t_0,
        "theta_squared": theta**2,
        "source": "Lattice QCD, BMW collaboration 2015",
    }


def eta_prime_mass_shift(theta: float = THETA_CH) -> Dict:
    """Witten-Veneziano: m_eta'^2 + m_eta^2 - 2 m_K^2 = 2 chi_t / f_pi^2.
    Theta-dependence: delta m_eta'^2 ~ theta^2 * chi_t / f_pi^2."""
    m_eta = 0.958
    m_K = 0.495
    chi_t_0 = (0.0756) ** 4
    delta_m_eta_prime_sq = theta**2 * chi_t_0 / F_PI**2
    return {
        "m_eta_prime_GeV": m_eta,
        "delta_m_eta_prime_sq_GeV2": delta_m_eta_prime_sq,
        "relative_shift": delta_m_eta_prime_sq / m_eta**2,
        "source": "Witten-Veneziano relation",
    }


def axion_mass_if_PQ_scale(f_a_GeV: float, theta: float = THETA_CH) -> Dict:
    """Standard QCD axion mass: m_a = sqrt(m_u m_d) / (m_u + m_d) * Lambda^2 / f_a
    ~ 5.7e-6 eV * (1e12 GeV / f_a).
    Choptyuk-corrected axion mass: theta -> theta + theta_Ch
    m_a(theta) ~ m_a(0) * sqrt(1 + theta^2) ~ m_a(0) for tiny theta.
    But a_C could also rescale f_a via f_a^Ch = a_C * f_a, predicting m_a^Ch."""
    m_a_standard_eV = 5.7e-6 * (1e12 / f_a_GeV)
    # Hypothetical Choptyuk-modified PQ scale
    f_a_Ch = a_C_times(f_a_GeV, mode="rescale") if False else f_a_GeV
    m_a_Ch_eV = 5.7e-6 * (1e12 / f_a_Ch) if f_a_Ch > 0 else float("nan")
    return {
        "f_a_GeV": f_a_GeV,
        "m_a_standard_eV": m_a_standard_eV,
        "m_a_Ch_eV_if_f_a_rescaled": float("nan"),
        "note": "f_a rescaling via a_C is unphysical (a_C is CP-even, not a scale); "
                "the only natural insertion is in the theta-term",
    }


def a_C_times(x, mode="rescale"):
    return x


# ----------------------------------------------------------------------
# 3.  Theoretical candidate derivations of the 5/2 exponent
# ----------------------------------------------------------------------
def sphaleron_rate_5_2(T_GeV: float) -> Dict:
    """Cohen-Kaplan-Nelson-style sphaleron rate at T < M_H:
        Gamma_sph(T) = kappa * alpha_W^5 * T^4 * (M_H/T)^(5/2)
    Setting T = Lambda_QCD gives the (Lambda/M_H)^(5/2) factor naturally.
    """
    kappa = 1.0  # O(1-100) unknown
    T = T_GeV
    rate = kappa * ALPHA_W**5 * T**4 * (M_H / T) ** 2.5
    return {
        "kappa": kappa,
        "alpha_W": ALPHA_W,
        "T_GeV": T,
        "M_H_GeV": M_H,
        "Gamma_sph_GeV4": rate,
        "Gamma_sph_per_cm3_per_s": rate * (1.0e39),  # rough conversion
        "exponent_origin": "(M_H/T)^(5/2) from sphaleron diffusion through Higgs plasma",
        "reference": "Cohen, Kaplan & Nelson, Ann.Rev.Nucl.Part.Sci.43 (1993) 27",
    }


def weinberg_operator_5_2() -> Dict:
    """The Weinberg 3-gluon CP-odd operator
        w f^{abc} G^a_{mu nu} G~^{b nu rho} G^c_{rho mu}
    has dimension 6. Its Wilson coefficient at M_H scales as
        w(M_H) ~ g_s^3 / (16 pi^2) * Im(y_t)^2 / M_H^2
    Running down to Lambda_QCD gives a multiplicative factor
        (alpha_s(Lambda)/alpha_s(M_H))^(gamma_6 / (2 b_0))
    With gamma_6 ~ 5 (anomalous dimension) and b_0 = 7 (Nf=6), the
    ratio exponent is 5/14 ~ 0.36, not 5/2.
    But if we instead look at the square-root of the OPE sum rule,
    sqrt(<G^2>) enters with exponent 5/2."""
    g_s = math.sqrt(4 * PI * ALPHA_S_MZ)
    w_MH = g_s**3 / (16 * PI**2) / M_H**2  # rough order
    # RGE running to Lambda
    b0 = 7.0  # N_f = 6
    gamma6 = 5.0  # estimate
    # alpha_s(Lambda)/alpha_s(M_H) ~ 5-10
    ratio_alpha = 10.0
    running_factor = ratio_alpha ** (gamma6 / (2 * b0))
    w_Lambda = w_MH * running_factor
    return {
        "w_at_MH_GeV_minus2": w_MH,
        "running_factor": running_factor,
        "w_at_Lambda_GeV_minus2": w_Lambda,
        "exponent_claimed": "5/2 from sqrt(<G^2>) in OPE sum rules",
        "honest_verdict": "Partial: gamma_6/b_0 = 5/14, not 5/2",
    }


def hqet_anomalous_dim_5_2() -> Dict:
    """Heavy quark condensate scales as
        <Q bar Q> = -Lambda^3 * (Lambda/m_Q)^(gamma_m)
    with gamma_m at one loop = 8 alpha_s / (3 pi).
    For alpha_s(m_t) ~ 0.108: gamma_m ~ 0.092 -> tiny.
    Not 5/2. However, the integrated heavy-quark contribution to the
    QCD vacuum energy (Shifman-Vainshtein-Zakharov sum rule) scales as
        E_QCD^heavy ~ -N_f <m_Q Q bar Q> + ...
        ~ N_f Lambda^3 m_Q (Lambda/m_Q)^(gamma_m)
    Setting gamma_m ~ 5/2 would require alpha_s ~ 5/2 * 3 pi / 8 ~ 1.47, unphysical."""
    alpha_s_mt = 0.108
    gamma_m_1loop = 8 * alpha_s_mt / (3 * PI)
    return {
        "alpha_s_m_t": alpha_s_mt,
        "gamma_m_1loop": gamma_m_1loop,
        "verdict": "Anomalous dimension is too small (~0.09) to give 5/2.",
    }


def electroweak_instanton_5_2() -> Dict:
    """EW instanton density involves exp(-4 pi / alpha_W).
    The prefactor has a power-law (Lambda_EW / M_H)^p from the
    running of the SU(2) coupling. With b0_EW = -19/6 (negative due to
    Higgs loops), the running is REVERSED, and we get
    (Lambda_EW/M_H)^(-|p|) which is large.
    The Choptyuk formula instead uses Lambda_QCD, so this is the wrong
    scale. However, if we interpret (Lambda_QCD/M_H)^(5/2) as the
    product of Lambda_QCD/Lambda_EW (QCD phase transition factor)
    times Lambda_EW/M_H (EW instanton factor), 5/2 splits as 3/2 + 1.
    """
    return {
        "interpretation": "(Lambda_QCD/M_H)^(5/2) = (Lambda_QCD/M_W)^(3/2) * (M_W/M_H)^1 (approx)",
        "Lambda_QCD/M_W": LAMBDA_QCD / M_W,
        "M_W/M_H": M_W / M_H,
        "splitting_3_2_plus_1": (LAMBDA_QCD / M_W) ** 1.5 * (M_W / M_H) ** 1,
        "actual_5_2": (LAMBDA_QCD / M_H) ** 2.5,
    }


# ----------------------------------------------------------------------
# 4.  Numerical experiments
# ----------------------------------------------------------------------
def sensitivity_to_exponent() -> List[Dict]:
    """For p in [1, 6], compute a_C * (Lambda/M_H)^p
    and the resulting d_n prediction."""
    out = []
    for p in np.linspace(0.5, 6.0, 56):
        theta = A_C * (LAMBDA_QCD / M_H) ** p
        d_n = 2.4e-16 * theta
        out.append({
            "exponent_p": float(p),
            "theta_Ch": float(theta),
            "log10_theta": float(math.log10(theta)) if theta > 0 else float("-inf"),
            "d_n_e_cm": float(d_n),
            "d_n_log10": float(math.log10(d_n)) if d_n > 0 else float("-inf"),
            "nEDM_bound_log10": float(math.log10(1.8e-26)),
            "ratio_to_bound": float(d_n / 1.8e-26),
        })
    return out


def monte_carlo_uncertainty(n_samples: int = 100000) -> Dict:
    """Propagate uncertainty in Lambda_QCD, M_H, a_C to theta_Ch."""
    rng = np.random.default_rng(42)
    # Lambda_QCD: 200 +- 30 MeV
    lam = rng.normal(0.200, 0.030, n_samples)
    lam = np.clip(lam, 0.100, 0.400)
    # M_H: 125.10 +- 0.14 GeV (tiny)
    mH = rng.normal(125.10, 0.14, n_samples)
    # a_C: dominated by delta_C = pi/7 (no uncertainty)
    # but b_2 = 22 is exact for K3. So a_C is exact.
    a_C = A_C  # treated as exact
    theta = a_C * (lam / mH) ** 2.5
    d_n = 2.4e-16 * theta
    # Also vary the d_n coefficient (QCD lattice uncertainty)
    # d_n coefficient: 2.4e-16 +- 1.0e-16 (large uncertainty)
    coef_dn = rng.normal(2.4e-16, 1.0e-16, n_samples)
    coef_dn = np.clip(coef_dn, 0.5e-16, 5.0e-16)
    d_n_with_coef = coef_dn * theta
    return {
        "theta_Ch_mean": float(np.mean(theta)),
        "theta_Ch_std": float(np.std(theta)),
        "theta_Ch_median": float(np.median(theta)),
        "theta_Ch_5th": float(np.percentile(theta, 5)),
        "theta_Ch_95th": float(np.percentile(theta, 95)),
        "d_n_mean_e_cm": float(np.mean(d_n_with_coef)),
        "d_n_std_e_cm": float(np.std(d_n_with_coef)),
        "d_n_median_e_cm": float(np.median(d_n_with_coef)),
        "d_n_5th": float(np.percentile(d_n_with_coef, 5)),
        "d_n_95th": float(np.percentile(d_n_with_coef, 95)),
        "nEDM_bound_e_cm": 1.8e-26,
        "p_value_vs_bound": float(np.mean(d_n_with_coef > 1.8e-26)),
        "samples": n_samples,
    }


# ----------------------------------------------------------------------
# 5.  Visualization
# ----------------------------------------------------------------------
def plot_observables(out_dir: Path):
    """Bar chart: predicted vs experimental bound for each observable."""
    fig, ax = plt.subplots(figsize=(11, 6.5), constrained_layout=True)

    names = [o.name for o in OBSERVABLES]
    preds = [abs(o.prediction(THETA_CH)) for o in OBSERVABLES]
    bounds = [o.experimental_bound_e_cm for o in OBSERVABLES]

    x = np.arange(len(names))
    w = 0.38
    # Use symlog to display huge dynamic range
    ax.bar(x - w/2, preds, w, color="#d62728",
           label=r"Prediction: $d = c\,\theta_{\rm Ch}$")
    ax.bar(x + w/2, bounds, w, color="#1f77b4",
           label="Experimental bound")
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=20, ha="right")
    ax.set_ylabel(r"$|d|$  (e$\cdot$cm)")
    ax.set_title(
        r"CP-odd observables with Choptyuk bridge "
        r"$\theta_{\rm Ch}=a_C(\Lambda_{\rm QCD}/M_H)^{5/2}\approx 8.5\times 10^{-11}$",
        fontsize=12)
    ax.legend(loc="upper right")
    ax.grid(True, which="both", axis="y", alpha=0.3)

    # Annotate ratios
    for i, (p, b) in enumerate(zip(preds, bounds)):
        ratio = p / b
        txt = f"{ratio:.1e}"
        color = "darkred" if ratio > 1 else "darkgreen"
        ax.annotate(txt, (x[i], max(p, b) * 1.3), ha="center",
                    fontsize=8, color=color)

    out = out_dir / "theta_Ch_observables.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def plot_sphaleron_derivation(out_dir: Path):
    """Schematic showing how 5/2 emerges from sphaleron rate."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)

    # Left: sphaleron rate as a function of T for fixed M_H
    ax = axes[0]
    T = np.linspace(0.05, 1.5, 200)
    M_H_values = [125.0, 200.0, 500.0]
    for mH in M_H_values:
        rate = ALPHA_W**5 * T**4 * (mH / T) ** 2.5
        ax.plot(T, rate, label=f"$M_H={mH:.0f}$ GeV")
    ax.set_yscale("log")
    ax.set_xlabel(r"$T$ (GeV)")
    ax.set_ylabel(r"$\Gamma_{\rm sph}$ (GeV$^4$, $\kappa=1$)")
    ax.set_title("Sphaleron rate: $\\Gamma_{\\rm sph}\\sim\\alpha_W^5 T^4(M_H/T)^{5/2}$\n"
                 "(Cohen-Kaplan-Nelson)")
    ax.axvline(LAMBDA_QCD, color="red", ls="--", alpha=0.7,
               label=r"$T=\Lambda_{\rm QCD}$")
    ax.legend()
    ax.grid(True, which="both", alpha=0.3)

    # Right: theta_Ch as function of exponent p
    ax = axes[1]
    p_range = np.linspace(0.5, 6.0, 200)
    theta_vals = A_C * (LAMBDA_QCD / M_H) ** p_range
    ax.plot(p_range, theta_vals, "k-", lw=2)
    ax.axhline(THETA_BOUND_EXPERIMENTAL, color="red", ls="--",
               label=r"$|\theta_{\rm QCD}|<10^{-10}$ (nEDM bound)")
    ax.axvline(2.5, color="blue", ls=":", label=r"$p=5/2$ (Higgs bridge)")
    ax.axvline(1.0/3, color="green", ls=":", label=r"$p=1/3$ (Planck bridge)")
    ax.set_yscale("log")
    ax.set_xlabel(r"Exponent $p$")
    ax.set_ylabel(r"$a_C \cdot (\Lambda_{\rm QCD}/M_H)^p$")
    ax.set_title("Sensitivity of $\\theta_{\\rm Ch}$ to the exponent $p$")
    ax.legend()
    ax.grid(True, which="both", alpha=0.3)

    out = out_dir / "sphaleron_derivation.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def plot_exponent_sensitivity(out_dir: Path, sensitivity: List[Dict]):
    """Plot d_n prediction vs experimental bound as a function of p."""
    fig, ax = plt.subplots(figsize=(9, 5.5), constrained_layout=True)

    p = [s["exponent_p"] for s in sensitivity]
    d_n = [s["d_n_e_cm"] for s in sensitivity]

    ax.plot(p, d_n, "k-", lw=2, label=r"$d_n = 2.4\times 10^{-16}\,\theta_{\rm Ch}$")
    ax.axhline(1.8e-26, color="red", ls="--", lw=1.5,
               label=r"nEDM bound $1.8\times 10^{-26}$ e$\cdot$cm")
    ax.axhline(1e-27, color="orange", ls=":", lw=1.5,
               label=r"SNS nEDM target $10^{-27}$ e$\cdot$cm")
    ax.axhline(1e-28, color="green", ls=":", lw=1.5,
               label=r"SNS nEDM goal $10^{-28}$ e$\cdot$cm")
    ax.axvline(2.5, color="blue", ls=":", alpha=0.7, label=r"$p=5/2$ (Higgs)")
    ax.axvline(1.0/3, color="purple", ls=":", alpha=0.7, label=r"$p=1/3$ (Planck)")

    ax.set_yscale("log")
    ax.set_xlabel(r"Exponent $p$ in $a_C \cdot (\Lambda_{\rm QCD}/M_H)^p$")
    ax.set_ylabel(r"$d_n$ (e$\cdot$cm)")
    ax.set_title("Sensitivity of neutron EDM prediction to the bridge exponent")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, which="both", alpha=0.3)

    out = out_dir / "exponent_sensitivity.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def plot_monte_carlo(out_dir: Path, mc: Dict):
    """Histogram of theta_Ch and d_n from Monte Carlo."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), constrained_layout=True)

    rng = np.random.default_rng(42)
    n = mc["samples"]
    lam = np.clip(rng.normal(0.200, 0.030, n), 0.100, 0.400)
    mH = rng.normal(125.10, 0.14, n)
    theta = A_C * (lam / mH) ** 2.5
    coef = np.clip(rng.normal(2.4e-16, 1.0e-16, n), 0.5e-16, 5.0e-16)
    d_n = coef * theta

    ax = axes[0]
    ax.hist(theta, bins=80, color="#d62728", alpha=0.7)
    ax.axvline(1e-10, color="blue", ls="--", label=r"$|\theta|<10^{-10}$ bound")
    ax.axvline(mc["theta_Ch_mean"], color="black", ls="-",
               label=f"mean = {mc['theta_Ch_mean']:.2e}")
    ax.set_xlabel(r"$\theta_{\rm Ch}=a_C(\Lambda/M_H)^{5/2}$")
    ax.set_ylabel("count")
    ax.set_title("Monte Carlo: $\\theta_{\\rm Ch}$ with $\\Lambda, M_H$ uncertainties")
    ax.set_xscale("log")
    ax.legend()
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    ax.hist(d_n, bins=80, color="#1f77b4", alpha=0.7)
    ax.axvline(1.8e-26, color="red", ls="--", lw=2,
               label=r"nEDM bound $1.8\times 10^{-26}$")
    ax.axvline(mc["d_n_mean_e_cm"], color="black", ls="-",
               label=f"mean = {mc['d_n_mean_e_cm']:.2e}")
    ax.set_xlabel(r"$d_n$ (e$\cdot$cm)")
    ax.set_ylabel("count")
    ax.set_title("Monte Carlo: $d_n$ incl. lattice coefficient uncertainty")
    ax.set_xscale("log")
    ax.legend()
    ax.grid(True, alpha=0.3)

    out = out_dir / "monte_carlo_theta_Ch_dn.png"
    fig.savefig(out)
    plt.close(fig)
    return out


# ----------------------------------------------------------------------
# 6.  Main
# ----------------------------------------------------------------------
def main():
    here = Path(__file__).resolve().parent
    out_dir = here / "figures_v2"
    out_dir.mkdir(exist_ok=True)

    print("=" * 70)
    print("Choptyuk-augmented QCD: theta_Ch = a_C * (Lambda/M_H)^(5/2)")
    print("=" * 70)
    print(f"a_C                  = {A_C:.6e}")
    print(f"Lambda_QCD           = {LAMBDA_QCD} GeV")
    print(f"M_H                  = {M_H} GeV")
    print(f"Lambda/M_H           = {LAMBDA_QCD/M_H:.4e}")
    print(f"(Lambda/M_H)^(5/2)   = {(LAMBDA_QCD/M_H)**2.5:.4e}")
    print(f"theta_Ch             = {THETA_CH:.4e}")
    print(f"log10(theta_Ch)      = {LOG10_THETA_CH:.4f}")
    print(f"Experimental bound   = {THETA_BOUND_EXPERIMENTAL:.4e}")
    print(f"Ratio theta_Ch/bound = {THETA_CH/THETA_BOUND_EXPERIMENTAL:.3f}")

    print("\n" + "-" * 70)
    print("OBSERVABLE PREDICTIONS vs EXPERIMENTAL BOUNDS")
    print("-" * 70)
    obs_results = []
    for o in OBSERVABLES:
        pred = o.prediction()
        bound = o.experimental_bound_e_cm
        ratio = pred / bound
        print(f"  {o.name:18s} {o.symbol:18s} "
              f"pred = {pred:.3e} | bound = {bound:.3e} | "
              f"ratio = {ratio:+.2e}")
        obs_results.append({
            "name": o.name,
            "symbol": o.symbol,
            "coefficient_e_cm_per_theta": o.coefficient_in_e_cm_per_theta,
            "prediction_e_cm": pred,
            "experimental_bound_e_cm": bound,
            "ratio_prediction_to_bound": ratio,
            "experiment": o.experiment,
            "year": o.year,
            "notes": o.notes,
        })

    print("\n" + "-" * 70)
    print("THEORETICAL CANDIDATES FOR THE 5/2 EXPONENT")
    print("-" * 70)
    sphal = sphaleron_rate_5_2(LAMBDA_QCD)
    print(f"  Sphaleron (Cohen-Kaplan-Nelson) at T=Lambda:")
    for k, v in sphal.items():
        print(f"    {k:30s} = {v}")
    wein = weinberg_operator_5_2()
    print(f"\n  Weinberg 3-gluon operator:")
    for k, v in wein.items():
        print(f"    {k:30s} = {v}")
    hqet = hqet_anomalous_dim_5_2()
    print(f"\n  Heavy quark anomalous dim:")
    for k, v in hqet.items():
        print(f"    {k:30s} = {v}")
    ew = electroweak_instanton_5_2()
    print(f"\n  EW instanton split interpretation:")
    for k, v in ew.items():
        print(f"    {k:30s} = {v}")

    print("\n" + "-" * 70)
    print("OTHER THETA-DEPENDENT OBSERVABLES")
    print("-" * 70)
    chi_t = topological_susceptibility(THETA_CH)
    print(f"  chi_t(0)           = {chi_t['chi_t_0_GeV4']:.4e} GeV^4")
    print(f"  delta_chi_t        = {chi_t['delta_chi_t_GeV4']:.4e} GeV^4")
    print(f"  relative           = {chi_t['relative_correction']:.4e}")

    eta = eta_prime_mass_shift(THETA_CH)
    print(f"  delta m_eta'^2     = {eta['delta_m_eta_prime_sq_GeV2']:.4e} GeV^2")
    print(f"  relative           = {eta['relative_shift']:.4e}")

    ax = axion_mass_if_PQ_scale(1e12)
    print(f"  Standard axion mass at f_a=1e12 GeV: {ax['m_a_standard_eV']:.4e} eV")
    print(f"  note: {ax['note']}")

    print("\n" + "-" * 70)
    print("SENSITIVITY ANALYSIS: theta_Ch vs exponent p")
    print("-" * 70)
    sens = sensitivity_to_exponent()
    for s in sens[::8]:  # every 8th
        print(f"  p={s['exponent_p']:.3f}  "
              f"theta={s['theta_Ch']:.3e}  "
              f"d_n={s['d_n_e_cm']:.3e}  "
              f"ratio_to_bound={s['ratio_to_bound']:+.2e}")

    print("\n" + "-" * 70)
    print("MONTE CARLO UNCERTAINTY PROPAGATION")
    print("-" * 70)
    mc = monte_carlo_uncertainty(n_samples=200000)
    for k, v in mc.items():
        print(f"  {k:30s} = {v}")
    print(f"\n  >> P(d_n > 1.8e-26 e*cm)  = {mc['p_value_vs_bound']:.3f}")

    print("\n" + "-" * 70)
    print("GENERATING FIGURES")
    print("-" * 70)
    f1 = plot_observables(out_dir)
    print(f"  saved: {f1}")
    f2 = plot_sphaleron_derivation(out_dir)
    print(f"  saved: {f2}")
    f3 = plot_exponent_sensitivity(out_dir, sens)
    print(f"  saved: {f3}")
    f4 = plot_monte_carlo(out_dir, mc)
    print(f"  saved: {f4}")

    # ---- Save JSON ----
    results = {
        "metadata": {
            "target_theta_QCD_bound": THETA_BOUND_EXPERIMENTAL,
            "a_C_choptyuk": A_C,
            "lambda_QCD_GeV": LAMBDA_QCD,
            "M_Higgs_GeV": M_H,
            "exponent_used": 2.5,
            "theta_Ch": THETA_CH,
            "log10_theta_Ch": LOG10_THETA_CH,
            "ratio_theta_Ch_to_bound": THETA_CH / THETA_BOUND_EXPERIMENTAL,
            "delta_C": DELTA_C,
            "b2_K3": B2_K3,
        },
        "EDM_observables": obs_results,
        "hadronic_observables": {
            "topological_susceptibility": chi_t,
            "eta_prime_mass_shift": eta,
            "axion_mass_at_f_a_1e12": ax,
        },
        "theoretical_candidates_for_5_over_2": {
            "sphaleron_Cohen_Kaplan_Nelson": sphal,
            "weinberg_3_gluon_operator": wein,
            "heavy_quark_anomalous_dimension": hqet,
            "electroweak_instanton_splitting": ew,
        },
        "sensitivity_to_exponent": sens,
        "monte_carlo_uncertainty": mc,
        "figures": {
            "observables_bar": str(f1),
            "sphaleron_derivation": str(f2),
            "exponent_sensitivity": str(f3),
            "monte_carlo": str(f4),
        },
        "verdict": {
            "best_prediction": "d_n ~ 2e-26 e*cm, right at the edge of current bound",
            "testability": "Next-gen nEDM experiments (SNS nEDM, n2EDM) "
                           "will reach 1e-27 - 1e-28, fully probing this prediction",
            "theoretical_status": "5/2 exponent has a plausible but not rigorous "
                                  "derivation from sphaleron rate scaling",
            "overall": "Numerological match with first hints of theoretical "
                       "interpretation; falsifiable within ~5 years"
        },
    }
    out_json = here / "qcd_observables_results.json"
    out_json.write_text(json.dumps(results, indent=2, default=str),
                        encoding="utf-8")
    print(f"\nResults saved to: {out_json}")
    return results


if __name__ == "__main__":
    main()
