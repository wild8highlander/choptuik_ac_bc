r"""formal_choptuik — numerical service for the Choptuik formalization programme.

This package is the Python computational wing of the ``formal_choptuik``
directory inside ``wild8highlander/choptuik_ac_bc``.  It provides:

* ``evolver``        — a calibrated linear-mode model of the discretely
  self-similar (DSS) critical solution, used for visualization, data
  generation and regression testing of the scaling machinery;
* ``spectrum``       — construction and diagonalization of the linearized
  perturbation operator of the truncated mode model;
* ``interval_checks``— directed-rounding interval arithmetic used for
  strict error bounds (gap G5 of the gap registry);
* ``server``         — a JSON-over-ZMQ service exposing the above to the
  Lean 4 proof assistant (bridge protocol, see ``bridge/protocol.md``);
* ``certify``        — the certificate producer (gap G4): exact rational
  certificates + the generated Lean module consumed by the theory;
* ``client``         — the typed client of the interactive channel
  (schema-checked decoding, fail-closed timeouts).

Honest-scope note (the discipline of the parent repository):
``hypothesis -> machine confirmation -> honest caveats``.  The mode model
implemented here is *calibrated* to the published Choptuik constants
(gamma ~ 0.374, Delta = ln 2, single unstable eigenvalue) — it is a toy
laboratory for the verification workflow, NOT a solution of the full
Einstein-scalar system.  The full system is the subject of the Lean
formalization roadmap.

ASCII banner
------------
::

     ____    __  ___  ____  ___  ____  __  __ _   ___  ____
    / ___|  /  |/  \|  _ \|  _ \|  _ \|  \/  | | / _ \|  _ \
   | |     | || || | |_| | |_| | |_| || |\/| | || | | | |_| |
   | |___  | || || |  __/|  __/|  __/ | |  | | || |_| |  __/
    \____| |_||_||_|_|   |_|   |_|    |_|  |_|_| \___/|_|

    numerical wing of the machine-checked proof programme
"""

from __future__ import annotations

__all__ = ["evolver", "spectrum", "interval_checks", "server", "certify", "client"]
__version__ = "0.4.1"

BANNER = r"""
+--------------------------------------------------------------+
|              F O R M A L   C H O P T U I K                   |
|        numerical service  ·  python/choptuik_service         |
|                                                              |
|   modes: lambda_0 = 2.6745 (unstable) | Delta = ln 2         |
|   scaling: M_BH ~ |p - p*|^gamma,  gamma = 1/lambda_0        |
+--------------------------------------------------------------+
"""
