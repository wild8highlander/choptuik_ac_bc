/-
╔══════════════════════════════════════════════════════════════════════╗
║   FORMAL CHOPTUIK · Choptuik.Analysis.HyperbolicPDE                   ║
║   The Einstein-scalar hyperbolic system in spherical symmetry         ║
╠══════════════════════════════════════════════════════════════════════╣
║   A massless scalar field φ minimally coupled to gravity:             ║
║                                                                       ║
║       G_{μν} = 8π T_{μν},      T_{μν} = ∂_μφ ∂_νφ - ½ g_{μν} (∇φ)²,   ║
║       □_g φ = 0 .                                                     ║
║                                                                       ║
║   In double-null coordinates the system reduces to a coupled          ║
║   first-order system for (f, r, φ).  The well-posedness layer is      ║
║   shared with the existence module (gap G1).                          ║
╠══════════════════════════════════════════════════════════════════════╣
║   status : SCAFFOLD — statements fixed, proofs pending                ║
╚══════════════════════════════════════════════════════════════════════╝
-/

import Mathlib.Tactic

namespace Choptuik.Analysis

open Choptuik.Geometry

/-! ### The field system -/

/-- A classical solution of the Einstein-scalar system on the
double-null arena: metric data plus the scalar field, subject to the
constraint and evolution equations below. -/
structure ClassicalSolution where
  /-- underlying metric data -/
  metric : DoubleNullData
  /-- the massless scalar field φ(u, v) -/
  phi : ℝ → ℝ → ℝ

/-- Constraint: the null-null component of the Einstein equation
`G_{uu} = 8π T_{uu}` — a Raychaudhuri-type ODE in `u` at each `v`.
Stated abstractly; Phase 2 expands the derivatives explicitly. -/
def ConstraintUU (s : ClassicalSolution) : Prop :=
  ∀ u v, ∃ k : ℝ, 2 * deriv (fun u => s.metric.r u v) u = k * s.metric.r u v

/-- Evolution: the wave equation `□_g φ = 0` in characteristic form. -/
def WaveEquation (s : ClassicalSolution) : Prop :=
  ∀ u v, deriv (fun u => deriv (fun v => s.phi u v) v) u
       + (deriv (fun u => s.metric.f u v) u / s.metric.r u v)
       * (deriv (fun v => s.phi u v) v + deriv (fun u => s.phi u v) u) = 0

/-- A genuine solution satisfies both the constraint and the evolution. -/
def IsSolution (s : ClassicalSolution) : Prop :=
  ConstraintUU s ∧ WaveEquation s

/-! ### Well-posedness (shared with gap G1) -/

/-- **Local well-posedness** of the characteristic problem for the
Einstein-scalar system: smooth data near the cone tip produce a unique
classical solution in a neighbourhood. -/
theorem local_wellposedness
    (d : DoubleNullData) (φ0 φ1 : ℝ → ℝ)
    (hd : SphericallySymmetric d) :
    ∃ s : ClassicalSolution, IsSolution s ∧ s.metric = d := by
  sorry  -- G1-supporting: characteristic PDE theory, Phase 2 (with G1)

end Choptuik.Analysis
