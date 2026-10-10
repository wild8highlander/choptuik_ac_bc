"""qhb — Quark-Hawking Bridge model class (dimensionally reduced, deterministic).

Submodules
----------
core        : C1-C8 physics (gap, string, bridge thermal, detector, three body,
              tunneling, bootstrap)
phase_map   : C9 (beta, L) phase map and naive-window falsification
competing   : C10 competing causal models A/B/C
vortex      : C11 classical vortex-triangle anchor (Kirchhoff, from scratch)
asymmetry   : C12 matter-antimatter asymmetry lock (T14/T15)
claims      : Evidence Engine (29 claims registry)
"""
__version__ = "1.3.0"

from . import constants as C  # noqa: F401
