/-
╔══════════════════════════════════════════════════════════════════════╗
║   FORMAL CHOPTUIK · Choptuik.Geometry.Curvature                       ║
║   Curvature invariants and the isotropic (Weyl-finite) singularity    ║
╠══════════════════════════════════════════════════════════════════════╣
║   Near the Cauchy horizon of the Choptuik solution some curvature    ║
║   invariants diverge while the Weyl components stay finite — the      ║
║   singularity is "isotropic" (conformally compactifiable).  The       ║
║   formal proof of this section is gap G3 of the gap registry.         ║
╠══════════════════════════════════════════════════════════════════════╣
║   status : v0.4 — obligation-free.                                                                        ║
║                                                                       ║
║   * `divergence_invariant_under_rescaling` is now PROVED (the         ║
║     Phase-1 filter-composition exercise is discharged).               ║
║   * `critical_singularity_is_strong_and_isotropic` is PROVED from     ║
║     two explicit certificate hypotheses (coercive divergence of the   ║
║     Kretschmann scalar and boundedness of the Weyl amplitude).  The   ║
║     v0.3 "toy linkage" `K ≥ C⁴` was insufficient: it admits           ║
║     counterexamples with unbounded Weyl amplitude (e.g. C(u,v) = v    ║
║     with K ≥ C⁴ + v), so the original statement was false as         ║
║     written — see the repository report, finding S1.                  ║
╚══════════════════════════════════════════════════════════════════════╝
-/

import Mathlib.Tactic
import Mathlib.Order.Filter.Defs
import Mathlib.Order.Filter.AtTopBot.Defs
import Mathlib.Order.Filter.AtTopBot.Tendsto
import Mathlib.Topology.Basic
import Choptuik.Geometry.Basic

namespace Choptuik.Geometry

open Filter

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

/-! ### The repaired central geometric claim (gap G3) -/

/-- **Central geometric claim — gap G3, conditional core (PROVED).**
If the curvature profile carries the two G3 certificates —
* `hK`: a coercive lower bound making the Kretschmann scalar blow up
  along every future-complete approach, and
* `hC`: a global bound on the Weyl amplitude (the "Weyl-finite" half of
  the isotropic-singularity statement),
then the singularity reached along `hu, hv` is strong *and* isotropic
at once.  Discharging `hK`/`hC` for the Choptuik spacetime itself is the
remaining analytic content of G3 (Phase 2/3): it requires the conformal
compactification layer of the roadmap, and is *not* provable from the
v0.3 toy linkage `K ≥ C⁴` alone. -/
theorem critical_singularity_is_strong_and_isotropic
    (P : CurvatureProfile) (hu : ℝ → ℝ) (hv : ℝ → ℝ)
    (hK : ∀ u v, (u + v) ^ 2 ≤ P.K u v)          -- coercivity certificate
    (hC : ∃ B > 0, ∀ u v, |P.C u v| ≤ B) :        -- Weyl-finiteness certificate
    StrongSingularity P hu hv ∧ IsotropicSingularity P hu hv := by
  constructor
  · -- strong: K ≥ (u+v)² and u+v → ∞ along any approach
    intro happroach
    have hsum : Tendsto (fun s => hu s + hv s) atTop atTop := by
      rw [tendsto_atTop_atTop]
      intro M
      obtain ⟨N₁, hN₁⟩ := tendsto_atTop_atTop.mp happroach.1 M
      obtain ⟨N₂, hN₂⟩ := tendsto_atTop_atTop.mp happroach.2 0
      refine ⟨max N₁ N₂, fun s hs => ?_⟩
      have h1 : M ≤ hu s := hN₁ s (le_trans (le_max_left _ _) hs)
      have h2 : (0 : ℝ) ≤ hv s := hN₂ s (le_trans (le_max_right _ _) hs)
      linarith
    have hsq : Tendsto (fun s => (hu s + hv s) ^ 2) atTop atTop := by
      rw [tendsto_atTop_atTop]
      intro M
      obtain ⟨N, hN⟩ := tendsto_atTop_atTop.mp hsum (max 1 M)
      refine ⟨N, fun s hs => ?_⟩
      have h1 : max (1 : ℝ) M ≤ hu s + hv s := hN s hs
      have hone : (1 : ℝ) ≤ hu s + hv s := le_trans (le_max_left _ _) h1
      have hM : M ≤ hu s + hv s := le_trans (le_max_right _ _) h1
      nlinarith
    exact tendsto_atTop_mono (fun s => hK (hu s) (hv s)) hsq
  · -- isotropic: the Weyl amplitude is globally bounded
    intro _
    obtain ⟨B, hB0, hB⟩ := hC
    exact ⟨B, hB0, fun s => hB _ _⟩

/-- Curvature blow-up is invariant under the DSS echoing map
`(τ, ρ) ↦ (τ + Δ, e^{-Δ} ρ)`: monotone reparametrizations cannot tame a
divergence.  **PROVED** (v0.4 — the Phase-1 filter-composition exercise
is discharged: compose with `s ↦ c • s`, which diverges for `c > 0`). -/
theorem divergence_invariant_under_rescaling
    {K : ℝ → ℝ} {c : ℝ} (hc : 0 < c)
    (hdiv : Tendsto K atTop atTop) :
    Tendsto (fun s => K (c * s)) atTop atTop := by
  have hmul : Tendsto (fun s => c * s) atTop atTop := by
    rw [tendsto_atTop_atTop]
    intro M
    refine ⟨M / c, fun s hs => ?_⟩
    have hcs : c * (M / c) ≤ c * s := mul_le_mul_of_nonneg_left hs hc.le
    have hmc : c * (M / c) = M := by field_simp
    linarith
  exact hdiv.comp hmul

end Choptuik.Geometry
