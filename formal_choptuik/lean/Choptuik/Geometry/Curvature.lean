/-
╔══════════════════════════════════════════════════════════════════════╗
║   FORMAL CHOPTUIK · Choptuik.Geometry.Curvature                       ║
║   Curvature invariants and the isotropic (Weyl-finite) singularity    ║
╠══════════════════════════════════════════════════════════════════════╣
║   Near the Cauchy horizon of the Choptuik solution some curvature     ║
║   invariants diverge while the Weyl components stay finite — the      ║
║   singularity is "isotropic" (conformally compactifiable).  The       ║
║   formal proof of this section is gap G3 of the gap registry.         ║
╠══════════════════════════════════════════════════════════════════════╣
║   status : SCAFFOLD — statements fixed, proofs pending                ║
╚══════════════════════════════════════════════════════════════════════╝
-/

import Mathlib.Tactic

namespace Choptuik.Geometry

/-! ### Curvature bookkeeping (abstract layer) -/

/-- Abstract curvature record of a double-null spacetime: the Kretschmann
scalar `K = R_{abcd} R^{abcd}` and the Weyl amplitude `|C|`.  The Lean
formalization will derive both from mathlib's Christoffel/Riemann
machinery on manifolds; here they are axiomatic data of the statement
layer so that downstream modules can be written now. -/
structure CurvatureProfile where
  /-- Kretschmann scalar `K(u, v)` -/
  K : ℝ → ℝ → ℝ
  /-- Weyl amplitude `|C|(u, v)` -/
  C : ℝ → ℝ → ℝ

/-- Approaching the singularity along the parameter `s ↦ (u s, v s)`. -/
def ApproachesSingular (P : CurvatureProfile) (u v : ℝ → ℝ) : Prop :=
  Tendsto u atTop atTop ∧ Tendsto v atTop atTop

/-! ### The isotropic singularity -/

/-- The singularity is *strong*: the Kretschmann scalar diverges along
every approach. -/
def StrongSingularity (P : CurvatureProfile) (u v : ℝ → ℝ) : Prop :=
  ApproachesSingular P u v →
    Tendsto (fun s => P.K (u s) (v s)) atTop atTop

/-- The singularity is *isotropic*: the Weyl amplitude stays bounded even
as curvature invariants blow up (conformally compactifiable end). -/
def IsotropicSingularity (P : CurvatureProfile) (u v : ℝ → ℝ) : Prop :=
  ApproachesSingular P u v →
    ∃ B > 0, ∀ s, |P.C (u s) (v s)| ≤ B

/-- **Central geometric claim (gap G3, Phase 2/3 of the roadmap).**
The Choptuik critical spacetime ends in a singularity that is strong
*and* isotropic at once. -/
theorem critical_singularity_is_strong_and_isotropic
    (P : CurvatureProfile) (hu : ℝ → ℝ) (hv : ℝ → ℝ)
    (hP : ∀ u v, P.K u v ≥ (P.C u v)^4) :   -- toy linkage of the scaffold
    StrongSingularity P hu hv ∧ IsotropicSingularity P hu hv := by
  sorry  -- G3: requires formalized conformal compactification (Phase 2)

/-- Curvature blow-up is invariant under the DSS echoing map
`(τ, ρ) ↦ (τ + Δ, e^{-Δ} ρ)`: monotone reparametrizations cannot tame a
divergence.  Elementary (compose with `x ↦ c·x`, `c > 0`); scheduled for
discharge during Phase 1 together with the mathlib order/filter review. -/
theorem divergence_invariant_under_rescaling
    {K : ℝ → ℝ} {c : ℝ} (hc : 0 < c)
    (hdiv : Tendsto K atTop atTop) :
    Tendsto (fun s => K (c * s)) atTop atTop := by
  sorry  -- elementary Phase-1 exercise: Filter.Tendsto.comp with x ↦ c * x

end Choptuik.Geometry
