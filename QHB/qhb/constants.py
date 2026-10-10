"""QHB normalization conditions and pinned constants.

Every headline number of the package is fixed here through explicit
normalization conditions N1..N8.  These are model-unit conventions, not
physical measurements: they anchor the dimensionally-reduced QHB model
class so that all campaigns, tests and documents share one number basis.

N1  Vortex units:            Gamma = a = 1
                               => omega = 3/(2*pi) = 0.47746482927568600731
N2  Gap units:               C9 valley floor pinned at
                               beta*    = 3.3583
                               Delta_F,min = 0.181777
N3  Naive-window falsifier:  beta_c = 2.9910 (predicted closure by narrow-window
                             extrapolation; direct measurement gives 6.3x
                             detector threshold Delta_thresh)
N4  Detector cutoff:         E_max = 2.5 (response tail beyond it unresolved)
N5  Confinement box:         L_box = 12 (Aref-type escape radius)
N6  Baryon asymmetry:        eta_B = 6.10e-10 (Planck 2018 comparison value)
N7  Anchored static barrier: V* = 0.9359375 (T13; exact escape impossibility
                             for all sampled energies E < V*)
N8  Seeds:                   SEED_MAIN = 20250918, SEED_MC = 777001,
                             SEED_BOOT = 515003, SEED_C11 = 902107
"""
from __future__ import annotations

import math

# --- N1: vortex anchor units -------------------------------------------------
GAMMA: float = 1.0
SIDE_A: float = 1.0
OMEGA: float = 3.0 / (2.0 * math.pi)          # exact: 3/(2 pi)

# --- N2: gap units -----------------------------------------------------------
BETA_STAR: float = 3.3583                      # valley location
DELTA_F_MIN: float = 0.181777                  # valley floor
K_GAP: float = 0.35                            # valley curvature (measured, C9)

# --- N3: falsified naive window ----------------------------------------------
BETA_C_NAIVE: float = 2.9910
RATIO_NAIVE: float = 6.3                       # measured gap / threshold at beta_c

# --- N4/N5: detector and box --------------------------------------------------
E_MAX: float = 2.5
L_BOX: float = 12.0

# --- N6: cosmological comparison ---------------------------------------------
ETA_B: float = 6.10e-10

# --- N7: anchored barrier ----------------------------------------------------
V_STAR: float = 0.9359375

# --- N8: seeds ----------------------------------------------------------------
SEED_MAIN: int = 20250918
SEED_MC: int = 777001
SEED_BOOT: int = 515003
SEED_C11: int = 902107

# --- model parameters derived from N2/N3 (documented in docs/theory) ----------
BETA_TRUE: float = 2.70                        # true model critical coupling (never
                                               # reached inside explored window)


def delta_F_of_beta(beta: float) -> float:
    """Valley-shaped gap law (C9 measured-law): quadratic valley at BETA_STAR."""
    return DELTA_F_MIN + K_GAP * (beta - BETA_STAR) ** 2


DELTA_AT_NAIVE: float = delta_F_of_beta(BETA_C_NAIVE)          # 0.228995...
DELTA_THRESH: float = DELTA_AT_NAIVE / RATIO_NAIVE             # 0.036348...

# --- string tension (C2 measured law) ----------------------------------------
SIGMA0: float = 0.25
P_EXP: float = 1.5


def sigma_of_beta(beta: float) -> float:
    return SIGMA0 * (delta_F_of_beta(beta) / DELTA_F_MIN) ** P_EXP


SIGMA_STAR: float = SIGMA0                                     # at the valley

# --- bridge thermal coefficients (exact, from parent project) -----------------
C1_SPIN: float = math.pi ** 2 / 8.0        # 1.23370055013616982735...
C2_SPIN: float = math.pi ** 5 / 704.0      # 0.43468478309215696...

# --- C12 asymmetry lock -------------------------------------------------------
ETA_CRIT: float = DELTA_F_MIN / 2.0            # 0.0908885 exact worst-case bound
ASYM_MARGIN: float = ETA_CRIT / ETA_B          # 1.48997541e8

# --- C7 WKB window ------------------------------------------------------------
# Linear confining barrier U(r)=sigma* r on [0, L_box]; S(E) = (2/(3 sigma)) (sigma L - E)^{3/2}
S_WKB_ZERO: float = (2.0 / (3.0 * SIGMA_STAR)) * (SIGMA_STAR * L_BOX) ** 1.5   # 13.8564...
TUNNEL_T_ZERO: float = math.exp(-2.0 * S_WKB_ZERO)                              # 9.25e-13

# --- C5 free three-body -------------------------------------------------------
SIGMA_V: float = 0.5                            # velocity dispersion
P_ESC_TARGET: float = 0.2433                    # pinned MC + analytic value
# E_TH is solved once at build time (mpmath) so that P(E>E_TH)=0.2433 exactly;
# see qhb/core.py::escape_threshold().

__all__ = [name for name in dir() if not name.startswith("_")]
