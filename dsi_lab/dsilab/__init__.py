"""DSI Lab — dynamics of invariants: reusable core of the seven experiments.

The package is intentionally standalone (numpy + stdlib only) so that the
dsi_lab folder can be copied out of the parent repository and run anywhere.
"""

from dsilab.census import GENUS, PSL27, census_identity, genus_family_branches
from dsilab.constants import (
    B_CH_SEVEN,
    C_K3_EXACT,
    C_K3_MEASURED,
    DELTA_CH_PI_13,
    E_FREE,
    PSL27_ORDER,
    RESULTS_RTOL,
    RNG_SEED,
    TRACE_BRIDGE_GAP_MAX,
)
from dsilab.convergents import continued_fraction, convergents_of
from dsilab.leavitt import (
    F_WEIGHTED_FORMULA_TOL,
    kunz_tree_operators,
    kunz_tree_trimmed,
    leavitt_F,
    scaled_permutation_defect,
    weighted_tree_F,
)

__version__ = "2.0.0"

__all__ = [
    "B_CH_SEVEN",
    "C_K3_EXACT",
    "C_K3_MEASURED",
    "DELTA_CH_PI_13",
    "E_FREE",
    "F_WEIGHTED_FORMULA_TOL",
    "GENUS",
    "PSL27",
    "PSL27_ORDER",
    "RESULTS_RTOL",
    "RNG_SEED",
    "TRACE_BRIDGE_GAP_MAX",
    "__version__",
    "census_identity",
    "continued_fraction",
    "convergents_of",
    "genus_family_branches",
    "kunz_tree_operators",
    "kunz_tree_trimmed",
    "leavitt_F",
    "scaled_permutation_defect",
    "weighted_tree_F",
]
