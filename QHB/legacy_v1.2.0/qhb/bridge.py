# -*- coding: utf-8 -*-
"""
bridge.py — the Quark-Hawking Bridge mapping.

The bridge inherits the CHB mapping verbatim and adds the QCD contact:

    M_BH(eps; M_in) = M_in * f~(eps),   f~ in {0.2877, 0.2684, 1.0}

(the dimensionless born-ensemble members are INHERITED ANCHORS from
CHB campaign C1, N=800 — collapse_verdict_summary.json; this package
measures nothing about them and derives nothing from them).

Two cosmological contact points anchor the master table:

  CMB contact (inherited):  T_H(M) = T_CMB      ->  M = 4.5016e22 kg
  QCD contact (theorem T8): T_H(M) = T_QCD      ->  M = 6.81e10 kg
      with T_QCD = 155.16 MeV / k_B (lattice-QCD crossover anchor):
      the black hole whose Hawking temperature equals the
      deconfinement temperature of the universe.  Literature
      comparison: primordial holes of the QCD epoch ~ 1e11 kg
      (same order, comparison only — 0.67%-style honesty).

The master table renders 3 members x 5 input scales x 23 columns —
from r_s/l_P and T_H/T_QCD to the Wu residual and the code-unit gap.
"""
import math

from .constants import (G, c, hbar, k_B, h, M_sun, M_earth, M_moon, T_CMB,
                        T_QCD_K, LAMBDA_QCD_MeV, MeV_J, m_P, l_P, t_P, rho_P,
                        yr, Gyr, AU, lyr, FTILDE_MEMBERS, FTILDE_LABELS,
                        A_WU_ANCHOR, SEED, e_charge)
from . import wu as _wu

PAGE_FRACTION = 1.0 - 2.0 ** (-1.5)   # inherited CHB exact identity


# ----------------------------------------------------------------------------
# closed-form Schwarzschild thermodynamics (mirror of chbridge.hawking)
# ----------------------------------------------------------------------------
def r_s(M):
    """Schwarzschild radius [m]."""
    return 2.0 * G * M / c**2


def horizon_area(M):
    """Horizon area [m^2]."""
    return 4.0 * math.pi * r_s(M) ** 2


def S_BH(M):
    """Bekenstein-Hawking entropy [J/K]."""
    return k_B * c**3 * horizon_area(M) / (4.0 * G * hbar)


def T_H(M):
    """Hawking temperature [K]."""
    return hbar * c**3 / (8.0 * math.pi * G * M * k_B)


def P_H(M):
    """Hawking luminosity, photon-only [W]."""
    return hbar * c**6 / (15360.0 * math.pi * G**2 * M**2)


def t_evap(M):
    """Idealised photon-only lifetime [s]."""
    return 5120.0 * math.pi * G**2 * M**3 / (hbar * c**4)


def t_page(M):
    """Page time [s] (inherited exact fraction)."""
    return PAGE_FRACTION * t_evap(M)


def rho_mean(M):
    """Mean density inside the horizon [kg/m^3]."""
    return 3.0 * M / (4.0 * math.pi * r_s(M) ** 3)


def surface_gravity(M):
    """Schwarzschild surface gravity [m/s^2]."""
    return c**4 / (4.0 * G * M)


def f_ringdown(M):
    """l=2 ringdown frequency [Hz] (Chandrasekhar-Detweiler M*omega=0.3737)."""
    return 0.3737 * c**3 / (2.0 * math.pi * G * M)


def kretschmann_horizon(M):
    """Kretschmann scalar at the horizon [1/m^4]."""
    return 3.0 * c**8 / (4.0 * G**4 * M**4)


# ----------------------------------------------------------------------------
# the two contact points
# ----------------------------------------------------------------------------
def equal_cmb_mass():
    """CMB contact (inherited): T_H = T_CMB [kg]."""
    return hbar * c**3 / (8.0 * math.pi * G * k_B * T_CMB)


def equal_qcd_mass(T_QCD=None):
    """QCD contact (theorem T8): T_H = T_QCD [kg]."""
    if T_QCD is None:
        T_QCD = T_QCD_K
    return hbar * c**3 / (8.0 * math.pi * G * k_B * T_QCD)


def nu_of_T(T_K):
    """Photon frequency of a temperature [Hz]."""
    return k_B * T_K / h


def lambda_qcd_hz():
    """Lambda_QCD = 332 MeV as a frequency [Hz] (comparison anchor)."""
    return LAMBDA_QCD_MeV * MeV_J / h


# ----------------------------------------------------------------------------
# formatters (mirror of chbridge.hawking)
# ----------------------------------------------------------------------------
def fmt_len(x):
    if x < 1e-3:
        return f"{x*1e6:.3g} um"
    if x < 1.0:
        return f"{x*1e3:.3g} mm"
    return f"{x:.4g} m"


def fmt_time(x):
    if x < 1e-6:
        return f"{x:.3g} s"
    if x < 1e3 * yr:
        return f"{x/yr:.4g} yr"
    if x < 1e6 * yr:
        return f"{x/(1e3*yr):.4g} kyr"
    if x < 1e9 * yr:
        return f"{x/(1e6*yr):.4g} Myr"
    if x < 1e12 * yr:
        return f"{x/Gyr:.4g} Gyr"
    return f"{x/yr:.3e} yr"


# ----------------------------------------------------------------------------
# the master table: 3 members x 5 scales x 23 columns
# ----------------------------------------------------------------------------
def bridge_scales():
    """The five committed input scales (QCD contact included)."""
    return [
        ("Planck input", m_P),
        ("QCD input", equal_qcd_mass()),
        ("Asteroid input (1e12 kg)", 1e12),
        ("CMB input", 4.50e22),
        ("Solar input", M_sun),
    ]


def master_row(scale_name, M_in, member_label, ftilde):
    """One master-table row: 23 columns, SI units (numbers, not strings)."""
    M = M_in * ftilde
    Rs = r_s(M)
    TH = T_H(M)
    row = {
        "input_scale": scale_name,
        "M_in_kg": M_in,
        "member": member_label,
        "ftilde": ftilde,
        "M_BH_kg": M,
        "r_s_m": Rs,
        "r_s_over_lP": Rs / l_P,
        "T_H_K": TH,
        "T_H_over_TCMB": TH / T_CMB,
        "T_H_over_TQCD": TH / T_QCD_K,
        "S_BH_over_kB": S_BH(M) / k_B,
        "P_H_W": P_H(M),
        "t_evap_s": t_evap(M),
        "t_page_s": t_page(M),
        "t_evap_human": fmt_time(t_evap(M)),
        "rho_mean_kg_m3": rho_mean(M),
        "rho_over_rhoP": rho_mean(M) / rho_P,
        "kappa_s gravity": surface_gravity(M),
        "f_ringdown_Hz": f_ringdown(M),
        "Kretschmann_m4": kretschmann_horizon(M),
        "wu_residual_alpha09_x100": _wu.residual(A_WU_ANCHOR, 100.0),
        "gap_code_Delta0": None,      # filled by campaigns (C1 committed)
        "gap_shift_beta05": None,     # filled by campaigns (C1 committed)
    }
    return row


def master_table(gap_values=None):
    """15 rows x 23 columns; gap columns filled from committed C1 when given."""
    rows = []
    for scale_name, M_in in bridge_scales():
        for label, ftd in zip(FTILDE_LABELS, FTILDE_MEMBERS):
            rows.append(master_row(scale_name, M_in, label, ftd))
    if gap_values is not None:
        for r in rows:
            r["gap_code_Delta0"] = gap_values.get("gap_static")
            r["gap_shift_beta05"] = gap_values.get("gap_shift_beta05")
    return rows


# ----------------------------------------------------------------------------
# write_outputs — byte-deterministic rendering (mirror of chbridge.bridge)
# ----------------------------------------------------------------------------
_COLUMNS = ["input_scale", "M_in_kg", "member", "ftilde", "M_BH_kg", "r_s_m",
            "r_s_over_lP", "T_H_K", "T_H_over_TCMB", "T_H_over_TQCD",
            "S_BH_over_kB", "P_H_W", "t_evap_s", "t_page_s", "t_evap_human",
            "rho_mean_kg_m3", "rho_over_rhoP", "kappa_s gravity",
            "f_ringdown_Hz", "Kretschmann_m4", "wu_residual_alpha09_x100",
            "gap_code_Delta0", "gap_shift_beta05"]


def _fmt(v):
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    return f"{v:.10e}"


def write_outputs(rows, out_dir):
    """Write bridge_master.csv (byte-deterministic column order/format)."""
    import os
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "bridge_master.csv")
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(",".join(_COLUMNS) + "\n")
        for r in rows:
            fh.write(",".join(_fmt(r[c]) for c in _COLUMNS) + "\n")
    return path
