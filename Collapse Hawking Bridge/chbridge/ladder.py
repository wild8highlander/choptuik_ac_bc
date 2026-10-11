"""
ladder.py — ladders of fundamental scales across the two bridge sides.

Three comparison tables (lengths, accelerations, curvatures) mixing:

  * cosmological scales (Hubble radius c/H0, c H0/2pi, MOND a0 anchor);
  * horizon scales of the critical-collapse-born ensemble
    (surface gravity c^4/4GM, horizon Kretschmann, r_s/l_P);
  * the Planck barrier (semiclassical evaporation ends near r ~ 1.9 l_P)
    and the septinial constants of the engine family (b_Ch, delta_C).

The ladders are COMPARISON tables: no derivation of a0 (or of any
cosmological quantity) from horizon physics is claimed anywhere in this
project — honest-negative discipline.
"""
import csv
import math
import os

from .constants import (
    H0,
    M_earth,
    M_sun,
    Mpc,
    a0,
    b_Ch,
    c,
    delta_C,
    kretschmann_horizon,
    kretschmann_planck,
    l_P,
    m_P,
)
from .hawking import equal_CMB_mass, r_s, surface_gravity

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

F_MID = 0.2877   # dimensionless near-floor member of the born ensemble


def write_outputs(out_dir):
    """Write scale_ladder_{length,accel,curvature}.csv and bridge_constants.csv."""
    os.makedirs(out_dir, exist_ok=True)
    M_CMB = equal_CMB_mass()
    H0_SI = H0 / Mpc  # s^-1

    # ---------------- accelerations -----------------------------------------
    rows = [
        {"quantity": "MOND acceleration a0 (literature anchor)", "value_m_s2": a0,
         "formula": "a0 = 1.2e-10 m/s^2"},
        {"quantity": "c H0", "value_m_s2": c * H0_SI, "formula": "c H0"},
        {"quantity": "c H0 / 2pi (MOND coincidence)", "value_m_s2": c * H0_SI / (2 * math.pi),
         "formula": "c H0 / 2pi — a NUMERICAL coincidence with a0, not a derivation"},
        {"quantity": "Surface gravity, CMB-mass BH", "value_m_s2": surface_gravity(M_CMB),
         "formula": "kappa = c^4/(4GM), M = 4.50e22 kg (T_H = T_CMB)"},
        {"quantity": "Surface gravity, born BH at CMB input", "value_m_s2": surface_gravity(M_CMB * F_MID),
         "formula": "kappa for M = f_tilde * M_CMB, f_tilde = 0.2877"},
        {"quantity": "Surface gravity, solar BH", "value_m_s2": surface_gravity(M_sun),
         "formula": "kappa = c^4/(4GM_sun)"},
        {"quantity": "g at r_s of Sgr A*", "value_m_s2": surface_gravity(4.297e6 * M_sun),
         "formula": "kappa for M = 4.297e6 M_sun"},
    ]
    with open(os.path.join(out_dir, "scale_ladder_accel.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["quantity", "value_m_s2", "formula"])
        w.writeheader()
        w.writerows(rows)

    # ---------------- lengths -------------------------------------------------
    lrows = [
        {"quantity": "Planck length l_P", "value_m": l_P, "formula": "sqrt(hbar G / c^3)"},
        {"quantity": "Planck barrier r_P", "value_m": 1.9 * l_P,
         "formula": "r_P ~ 1.9 l_P — end of semiclassical evaporation"},
        {"quantity": "r_s of born BH at Planck input", "value_m": r_s(m_P * F_MID),
         "formula": "2G M / c^2, M = 0.2877 m_P"},
        {"quantity": "r_s of CMB-mass BH", "value_m": r_s(M_CMB),
         "formula": "2G M / c^2, M = 4.50e22 kg"},
        {"quantity": "r_s of born BH at CMB input", "value_m": r_s(M_CMB * F_MID),
         "formula": "M = 0.2877 M_CMB"},
        {"quantity": "r_s of Earth-mass BH", "value_m": r_s(M_earth),
         "formula": "2G M / c^2"},
        {"quantity": "r_s of solar BH", "value_m": r_s(M_sun), "formula": "2G M / c^2"},
        {"quantity": "Hubble radius c / H0", "value_m": c / H0_SI, "formula": "c / H0"},
    ]
    with open(os.path.join(out_dir, "scale_ladder_length.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["quantity", "value_m", "formula"])
        w.writeheader()
        w.writerows(lrows)

    # ---------------- curvatures -----------------------------------------------
    K_P = kretschmann_planck()
    crows = [
        {"quantity": "K at horizon, solar BH", "value_m4": kretschmann_horizon(M_sun),
         "K_over_KP": kretschmann_horizon(M_sun) / K_P,
         "formula": "K = 3c^8/(4G^4 M^4) = 48G^2M^2/(c^4 r_s^6)"},
        {"quantity": "K at horizon, born BH at Solar input", "value_m4": kretschmann_horizon(M_sun * F_MID),
         "K_over_KP": kretschmann_horizon(M_sun * F_MID) / K_P,
         "formula": "M = 0.2877 M_sun"},
        {"quantity": "K at horizon, born BH at CMB input", "value_m4": kretschmann_horizon(M_CMB * F_MID),
         "K_over_KP": kretschmann_horizon(M_CMB * F_MID) / K_P,
         "formula": "M = 0.2877 M_CMB"},
        {"quantity": "K at horizon, born BH at Planck input", "value_m4": kretschmann_horizon(m_P * F_MID),
         "K_over_KP": kretschmann_horizon(m_P * F_MID) / K_P,
         "formula": "M = 0.2877 m_P — above the Planck barrier"},
        {"quantity": "Planck curvature 1/l_P^4", "value_m4": K_P, "K_over_KP": 1.0,
         "formula": "1/l_P^4 = c^6/(hbar^2 G^2)"},
    ]
    with open(os.path.join(out_dir, "scale_ladder_curvature.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["quantity", "value_m4", "K_over_KP", "formula"])
        w.writeheader()
        w.writerows(crows)

    # ---------------- bridge constants table -------------------------------------
    brows = [
        {"bridge_quantity": "Critical exponent gamma (literature anchor)",
         "value": 0.374, "source": "literature anchor; NOT fitted in this project"},
        {"bridge_quantity": "b_Ch = 1 - cos(2pi/7) (septinial constant, exact)",
         "value": b_Ch, "source": "Klein-quartic spinor phases, septinial sector"},
        {"bridge_quantity": "|gamma_Ch - b_Ch|",
         "value": abs(0.374 - b_Ch), "source": "0.67% — a COMPARISON, never a fit"},
        {"bridge_quantity": "delta_C = pi/7 (septinial spinor phase)",
         "value": delta_C, "source": "exact"},
        {"bridge_quantity": "Echo period Delta (engine measurement)",
         "value": 3.44, "source": "effective period at fixed grid (NOT-DSS verdict)"},
        {"bridge_quantity": "t_Page / t_evap (Page model)",
         "value": 1.0 - 2.0**(-1.5), "source": "unitary entropy-flux model"},
        {"bridge_quantity": "Delta * gamma (product, C3 target)",
         "value": 1.27, "source": "project invariant; anchors give 1.28656 (1.3%)"},
        {"bridge_quantity": "A* (N=800), fixed-grid observable",
         "value": 0.08053436279296877,
         "source": ("ladder drift 2.79e-3 to N=1600 (F-1 remediation); "
                    "the stale 1.06e-6 agreement is RETRACTED")},
    ]
    with open(os.path.join(out_dir, "bridge_constants.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["bridge_quantity", "value", "source"])
        w.writeheader()
        w.writerows(brows)

    return {
        "accel_rows": len(rows), "length_rows": len(lrows),
        "curvature_rows": len(crows), "constants_rows": len(brows),
        "a0_over_cH0_2pi": a0 / (c * H0_SI / (2 * math.pi)),
        "gamma_vs_bch_pct": 100 * abs(0.374 - b_Ch) / b_Ch,
    }
