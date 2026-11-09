/-
╔══════════════════════════════════════════════════════════════════════╗
║   FORMAL CHOPTUIK · Choptuik.Stability.Linearization                  ║
║   The linearized perturbation operator of the critical solution       ║
╠══════════════════════════════════════════════════════════════════════╣
║   Critical phenomena = the critical solution is an attractor of       ║
║   codimension one.  The formal statement lives on the spectrum of     ║
║   the operator obtained by linearizing the Einstein-scalar system     ║
║   around the critical solution.                                       ║
╠══════════════════════════════════════════════════════════════════════╣
║   status : SCAFFOLD — Phase-3 interface                               ║
╚══════════════════════════════════════════════════════════════════════╝
-/

import Mathlib.Tactic
import Choptuik.Existence.DSS

namespace Choptuik.Stability

open Choptuik.Existence

/-! ### Perturbations -/

/-- A perturbation mode of the critical solution: spatial profile and
complex growth rate `rate` (log-time dynamics). -/
structure PerturbationMode where
  /-- spatial profile `φ_k(ρ)` -/
  profile : ℝ → ℝ
  /-- complex eigenvalue (growth rate in log-time) -/
  rate : ℂ

/-- A mode is **unstable** when its growth rate has positive real part. -/
def PerturbationMode.Unstable (m : PerturbationMode) : Prop :=
  0 < m.rate.re

/-! ### The linearized operator -/

/-- The linearized operator `L` of the Einstein-scalar system around the
critical solution `cs`: acts on perturbation profiles, returns the
log-time growth rates.  Abstract interface; Phase 3 supplies the
coefficient calculus. -/
structure LinearizedOperator where
  /-- the critical solution being perturbed -/
  base : CriticalSolution
  /-- eigenpair extraction -/
  eigenpairs : List PerturbationMode

/-- The growth-rate spectrum of `L`. -/
def LinearizedOperator.spectrum (L : LinearizedOperator) : List ℂ :=
  L.eigenpairs.map PerturbationMode.rate

end Choptuik.Stability
