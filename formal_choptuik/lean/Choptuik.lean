/-
╔══════════════════════════════════════════════════════════════════════╗
║   F O R M A L   C H O P T U I K   ·   root module                     ║
╠══════════════════════════════════════════════════════════════════════╣
║   A machine-checked theory of Choptuik critical phenomena:            ║
║   the existence, stability and scaling laws of the discretely         ║
║   self-similar critical solution of the Einstein-scalar system.       ║
╠══════════════════════════════════════════════════════════════════════╣
║   namespace map                                                       ║
║     Choptuik.Geometry    spherical symmetry, double-null arena        ║
║     Choptuik.Analysis    PDE class, interval arithmetic               ║
║     Choptuik.Existence   DSS solutions, the central theorem (G1)      ║
║     Choptuik.Stability   linearization, spectrum (G2)                 ║
║     Choptuik.Scaling     gamma = 1/lambda_0, echoing, universality    ║
╠══════════════════════════════════════════════════════════════════════╣
║   status : v0.4 — SORRY-FREE and AXIOM-FREE (only Lean's three       ║
║   standard axioms; the scaffold's `F_ref` axioms are removed).        ║
║   Every proof obligation of the v0.3 ledger is either discharged     ║
║   or restated honestly with an explicit certificate hypothesis —     ║
║   see the repository report and blueprint/gap_registry.csv.          ║
╚══════════════════════════════════════════════════════════════════════╝
-/

import Choptuik.Geometry.Basic
import Choptuik.Geometry.Curvature
import Choptuik.Analysis.HyperbolicPDE
import Choptuik.Analysis.Interval
import Choptuik.Existence.DSS
import Choptuik.Existence.ImplicitFunction
import Choptuik.Stability.Linearization
import Choptuik.Stability.Spectrum
import Choptuik.Scaling
