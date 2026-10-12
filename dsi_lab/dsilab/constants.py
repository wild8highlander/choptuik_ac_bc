"""Constants of the DSI laboratory (single source of truth).

Every number here is either an exact rational/named quantity of the b-C/a-C
framework or a committed verdict threshold of the seven experiments. The
experiments import from this module; nothing is duplicated inline.
"""

from __future__ import annotations

import math
from fractions import Fraction

# --- the framework ----------------------------------------------------------
#: |PSL(2,7)| — the automorphism group of the Klein quartic (genus 3).
PSL27_ORDER: int = 168

#: DSI-4 observation: c_K3 = 3^3 / (2^2 · |PSL(2,7)|) = 27/672 = 9/224.
C_K3_EXACT: Fraction = Fraction(9, 224)

#: The repo-measured value of c_K3 (audit 2026-09 record).
C_K3_MEASURED: float = 0.04017757639214903

#: Deviation of the exact observation from the measured value, in percent.
#: (|9/224 − c_meas| / c_meas · 100 ≈ 0.0025 % — three orders of magnitude
#:  tighter than the structural alternatives: b_Ch(22) +0.82 %,
#: braking RG +0.45 %, 1/25 −0.44 %.)
C_K3_DEVIATION_PCT: float = (
    abs(float(C_K3_EXACT) - C_K3_MEASURED) / C_K3_MEASURED * 100.0
)

#: The septinial constant b_Ch = 1 − cos(2π/7) = 0.37651019814126640.
B_CH_SEVEN: float = 1.0 - math.cos(2.0 * math.pi / 7.0)

#: Sharp trace theorem floor: F >= 5n/7 for all n, i.e. e >= 5/7.
E_FREE: Fraction = Fraction(5, 7)

#: Finding D1 (Hurwitz tower): the corrected genus-14 group is PSL(2,13)
#: (the repo row (g=14, n=11) was inconsistent: 1092 is not divisible by 11),
#: and the framework's universal curve evaluates to Delta_Ch(pi/13) = 3.3672.
DELTA_CH_PI_13: float = 3.3672

# --- committed verdict thresholds --------------------------------------------
#: Experiment 1: trace bridge — the sofic sqrt(eps)-law is refuted when the
#: observed defect e(eps) does not fall below this gap over the eps-scan.
TRACE_BRIDGE_GAP_MAX: float = 5.9e-8

#: Experiment 7, theorem A: max relative error of the identity
#: F = 3n − 2p − 2q + 3r over 24000 random partial-isometry pairs.
IDENTITY_ERR_A_MAX: float = 5.9e-16

#: Experiment 7, theorem B: |F − (n + 2·rank(I−P−Q))| tolerance on the
#: Kunz-tree trimmings (k = 2..10) and random disjoint projections.
THEOREM_B_ABS_TOL: float = 1e-9

#: Experiment 7, theorem C: |F − 2n| tolerance for unitary/permuted pairs.
THEOREM_C_ABS_TOL: float = 1e-9

#: {7,3} census: the valence identity 7F = 3V = 2E = |G| = 168 is exact.
CENSUS_V: int = 56
CENSUS_E: int = 84
CENSUS_F: int = 24

# --- reproducibility ----------------------------------------------------------
#: All experiments fix this seed; regenerated results/*.json must match the
#: committed files to this relative tolerance, otherwise it is a finding.
RNG_SEED: int = 42
RESULTS_RTOL: float = 1e-10
