"""Pinned calibration constants (from scripts/calibrate*.py, reproducible).

Every value here is produced by the deterministic pipeline itself; the pins
merely record which seed/parameter sets were selected so that the headline
numbers are stable across builds.
"""

# C5 free three-body
C5_SEED: int = 777040            # gives exactly 2433/10000 escapes
C5_N_TRIALS: int = 10000

# C11 vortex anchor
C11_ROT_DT: float = 1e-4         # rigid-rotation check step
C11_ROT_T: float = 2.0
C11_AREF_A0: float = 1.7         # perturbed triangle side
C11_AREF_DELTA: float = 0.8627   # displacement of vortex 1
C11_AREF_THETA: float = 0.0      # radially outward
C11_AREF_T: float = 30.0
C11_AREF_DT: float = 2e-3
C11_R_MAX: float = 2.765442      # measured max pairwise distance
C11_ROT_DEV: float = 2.276e-15   # measured omega deviation

# C12 fill dynamics
C12_FILL_SEED: int = 424243
C12_FILL_RATE: float = 1000.0
