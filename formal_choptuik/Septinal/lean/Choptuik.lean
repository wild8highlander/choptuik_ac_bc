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
║     Choptuik.Bridge      certificate channel to the numerics (G4)     ║
╠══════════════════════════════════════════════════════════════════════╣
║   status : SORRY-FREE and AXIOM-FREE (only Lean's three               ║
║   standard axioms: propext, Classical.choice, Quot.sound).            ║
║   Every proof obligation is either discharged or restated honestly   ║
║   with an explicit certificate hypothesis — see the repository       ║
║   report and blueprint/gap_registry.csv.                             ║
║   The certificate bridge (G4): rational certificates flow from the   ║
║   Python producer into checked Lean data and are discharged into     ║
║   the spectral, Newton-Kantorovich and interval headlines — see      ║
║   Choptuik/Bridge/.                                                  ║
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
import Choptuik.Bridge.Certificates
import Choptuik.Bridge.Generated
import Choptuik.Bridge.Discharge
import Choptuik.Analysis.FieldEquations
import Choptuik.Existence.DSSBoundary
import Choptuik.ScalingDerivation
import Choptuik.Stability.Gershgorin
import Choptuik.Existence.TruncatedDSS
