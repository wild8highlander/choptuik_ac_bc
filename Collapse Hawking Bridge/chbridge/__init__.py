"""
chbridge — Collapse-Hawking Bridge, v2.2.0.

A dimensionless mapping between the two ends of semiclassical gravity:

  * the CRITICAL side: threshold collapse of a massless scalar field,
    solved with a double-null characteristic engine (engine/solver.py);
  * the THERMODYNAMIC side: Schwarzschild black-hole thermodynamics
    (Hawking temperature, Bekenstein-Hawking entropy, evaporation,
    Page time).

The bridge object is the dimensionless born spectrum

    f~(eps) = M_code(eps) / M_code_sat ,   eps = A - A*,

which is measured numerically and then mapped onto physical masses
through a single input scale M_in.  Every number produced by this
package is traceable either to an exact formula or to a machine output
committed under campaigns/reference/.

Modules
-------
constants   single source of truth: physical constants, engine anchors,
            campaign verdict values
hawking     closed-form Schwarzschild thermodynamics
bridge      born spectrum + master mapping table (f~ -> physical BHs)
page        unitary entropy-flux Page curves + Haar-averaging check
ladder      scale ladders: lengths, accelerations, curvatures
validate    high-precision (mpmath) re-verification of every constant

Versioning: 2.2.0 (honest-verdict release: the Δ·γ anchor product reclassified ANCHOR_ARITHMETIC, b_Ch_lit removed, falsification criteria preregistered in PREREGISTRATION.md; see CHANGELOG).
See CHANGELOG.md.
"""

from .constants import (
                        CAMPAIGN,
                        T_CMB,
                        G,
                        M_sun,
                        __version__,
                        b_Ch,
                        c,
                        delta_C,
                        echo_delta,
                        gamma_Ch,
                        hbar,
                        k_B,
                        l_P,
                        m_P,
                        t_P,
)
from .hawking import PAGE_FRACTION

__all__ = [
                        "CAMPAIGN",
                        "PAGE_FRACTION",
                        "T_CMB",
                        "G",
                        "M_sun",
                        "__version__",
                        "b_Ch",
                        "c",
                        "delta_C",
                        "echo_delta",
                        "gamma_Ch",
                        "hbar",
                        "k_B",
                        "l_P",
                        "m_P",
                        "t_P",
]
