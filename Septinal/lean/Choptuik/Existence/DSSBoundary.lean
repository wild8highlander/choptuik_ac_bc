/-
   F O R M A L   C H O P T U I K   ·   Choptuik/Existence/DSSBoundary.lean

   Work-plan items 3–6: the link from (discrete/continuous) self-similarity
   to the field equations, non-degeneracy of the critical solution, and the
   equivalence of "DSS + equations" with a periodic-in-T boundary value
   problem in the similarity variables (T, x) — the formal version of
   step 7.

   Convention (homothety form): the Einstein–scalar system is invariant
   under (g, φ) → (λ²g, φ), so a solution is DSS with period Δ when its
   double-null data satisfy, with λ = e^Δ,
     f(λu, λv) = f(u,v),  r(λu, λv) = λ r(u,v),  φ(λu, λv) = φ(u,v).
   CSS = the same for every λ > 0 (every Δ ∈ ℝ).

   Contents (all PROVED, sorry-free):
   * `minkowski_dss` / `minkowski_css` — flat space is self-similar with
     EVERY period (item 5); `existence_vacuous_without_nondegeneracy`
     explains why DSS existence statements are empty without φ ≢ 0.
   * `CriticalData` — the non-vacuous package: solves
     `Choptuik.Analysis.IsSolution` on the regular region + DSS + φ ≢ 0
     (item 4); `minkowski_fails_nondegeneracy` excludes flat space.
   * `dss_iff_periodic` — DSS_Δ on the wedge ⟺ the reduced fields in the
     similarity variables (T, x) = (log(-u), -u/v) are Δ-periodic in T
     (item 6); `css_iff_constant` — CSS ⟺ T-independent reduced fields.
   * `dss_solution_iff_periodic_bvp` — "DSS + equations" ⟺ "periodic
     reduced data + the pullback solution property" (step 7, stated
     invariantly through the coordinate map; the explicit autonomous x-
     system is a routine pullback computation, registered with gap G7).
-/

import Mathlib.Tactic
import Mathlib.Analysis.Calculus.Deriv.Basic
import Mathlib.Analysis.Calculus.ContDiff.Defs
import Mathlib.Analysis.SpecialFunctions.Exp
import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Data.Complex.Basic
import Mathlib.Algebra.Order.Floor.Ring
import Mathlib.Algebra.Order.Archimedean.Basic
import Choptuik.Analysis.FieldEquations

namespace Choptuik.Existence

open Choptuik.Analysis

/-! ### Self-similarity in the (u,v) arena -/

/-- The echoing laws at one point, with dilation `λ = e^Δ`. -/
def DSSLawsAt (d : Fields) (Δ u v : ℝ) : Prop :=
  d.f (Real.exp Δ * u) (Real.exp Δ * v) = d.f u v ∧
    d.r (Real.exp Δ * u) (Real.exp Δ * v) = Real.exp Δ * d.r u v ∧
    d.phi (Real.exp Δ * u) (Real.exp Δ * v) = d.phi u v

/-- Discrete self-similarity with period `Δ` (homothety form). -/
def DSSuv (d : Fields) (Δ : ℝ) : Prop := ∀ u v, DSSLawsAt d Δ u v

/-- Continuous self-similarity: DSS with every period. -/
def CSSuv (d : Fields) : Prop := ∀ Δ : ℝ, DSSuv d Δ

/-! ### Item 5: Minkowski is self-similar with every period -/

/-- **Minkowski is DSS with every period** (work-plan item 5). -/
theorem minkowski_dss (Δ : ℝ) : DSSuv Minkowski.fields Δ := by
  intro u v
  refine ⟨rfl, ?_, rfl⟩
  show (Real.exp Δ * v - Real.exp Δ * u) / 2 = Real.exp Δ * ((v - u) / 2)
  ring

/-- **Minkowski is CSS.** -/
theorem minkowski_css : CSSuv Minkowski.fields := fun Δ => minkowski_dss Δ

/-- **The vacuity explanation (item 5).**  For every period Δ > 0, flat
space witnesses "DSS + solves the field equations on its regular region"
— but its scalar field vanishes identically.  Any existence statement
for DSS solutions that does not demand non-degeneracy is witnessed by
Minkowski and carries no physics content. -/
theorem existence_vacuous_without_nondegeneracy : ∀ Δ > 0,
    DSSuv Minkowski.fields Δ ∧
      (∀ u v, u < v → IsSolution Minkowski.fields u v) ∧
      ¬ ∃ u v, 0 < Minkowski.fields.r u v ∧ Minkowski.fields.phi u v ≠ 0 := by
  intro Δ _
  refine ⟨minkowski_dss Δ, fun u v => Minkowski.minkowski_isSolution u v, ?_⟩
  rintro ⟨u, v, -, hne⟩
  exact hne rfl

/-! ### Item 4: the non-vacuous critical-solution package -/

/-- **The critical-solution package (item 4):** `CriticalSolution`
strengthened by the linkage to the field equations (`IsSolution`) and by
non-degeneracy of the scalar field (φ ≢ 0 on the regular region). -/
structure CriticalData where
  /-- the fields -/
  data : Fields
  /-- echoing period -/
  Δ : ℝ
  /-- positivity of the period -/
  hΔ : 0 < Δ
  /-- solves the Einstein–scalar system on the regular region -/
  isSol : ∀ u v, 0 < data.r u v → IsSolution data u v
  /-- echoing -/
  dss : DSSuv data Δ
  /-- non-degeneracy: the scalar field is not identically zero -/
  nondeg : ∃ u v, 0 < data.r u v ∧ data.phi u v ≠ 0

/-- **Minkowski is excluded from `CriticalData`** by non-degeneracy,
although it is CSS with every period. -/
theorem minkowski_fails_nondegeneracy :
    ¬ ∃ (cd : CriticalData), cd.data = Minkowski.fields := by
  rintro ⟨cd, hcd⟩
  obtain ⟨u, v, -, hne⟩ := cd.nondeg
  rw [hcd] at hne
  exact hne rfl

/-! ### Items 3, 6: similarity variables and the periodic BVP -/

/-- The similarity wedge: `u < 0 < v`. -/
def Wedge (u v : ℝ) : Prop := u < 0 ∧ 0 < v

/-- Similarity time coordinate `T = log(-u)` on the wedge (the dilation
`(u,v) ↦ (e^Δ u, e^Δ v)` acts by `T ↦ T + Δ`). -/
noncomputable def simT (u v : ℝ) : ℝ := Real.log (-u)

/-- The similarity space coordinate `x = -u/v > 0` on the wedge. -/
noncomputable def simX (u v : ℝ) : ℝ := -u / v

/-- The inverse map: `(T, x) ↦ (u, v) = (-e^T, e^T/x)` for `x > 0`. -/
noncomputable def simUV (T x : ℝ) : ℝ × ℝ := (-Real.exp T, Real.exp T / x)

/-- The scale-invariant reduced fields on `(T, x)`: `R` carries the
`e^{-T}` weight (the areal radius scales like a length); `G` and `Φ`
are plain pullbacks. -/
noncomputable def reducedR (d : Fields) (T x : ℝ) : ℝ :=
  Real.exp (-T) * d.r (-Real.exp T) (Real.exp T / x)

noncomputable def reducedG (d : Fields) (T x : ℝ) : ℝ := d.f (-Real.exp T) (Real.exp T / x)

noncomputable def reducedPhi (d : Fields) (T x : ℝ) : ℝ := d.phi (-Real.exp T) (Real.exp T / x)

/-- Coordinate identity: `(T, x) ↦ (u, v) ↦ (T, x)` is the identity for
`x > 0`. -/
lemma sim_pair (T x : ℝ) (hx : 0 < x) :
    simT (simUV T x).1 (simUV T x).2 = T ∧ simX (simUV T x).1 (simUV T x).2 = x := by
  have hE : (0 : ℝ) < Real.exp T := Real.exp_pos T
  constructor
  · show Real.log (-(-(Real.exp T))) = T
    rw [neg_neg]
    exact Real.log_exp T
  · show -(-(Real.exp T)) / (Real.exp T / x) = x
    rw [neg_neg]
    field_simp

/-- Coordinate identity: `(u, v) ↦ (T, x) ↦ (u, v)` is the identity on
the wedge. -/
lemma uv_of_wedge {u v : ℝ} (h : Wedge u v) :
    simUV (simT u v) (simX u v) = (u, v) := by
  obtain ⟨hwu, hwv⟩ := h
  have hu : (0 : ℝ) < -u := by linarith
  have hv : (0 : ℝ) < v := hwv
  have hE : Real.exp (simT u v) = -u := by
    show Real.exp (Real.log (-u)) = -u
    exact Real.exp_log hu
  have h2 : Real.exp (simT u v) / simX u v = v := by
    show Real.exp (Real.log (-u)) / (-u / v) = v
    rw [Real.exp_log hu, div_div_eq_mul_div]
    exact mul_div_cancel_left₀ _ (ne_of_gt hu)
  show (-Real.exp (simT u v), Real.exp (simT u v) / simX u v) = (u, v)
  rw [h2, hE, neg_neg]

/-- **The structural equivalence (item 6): DSS_Δ on the wedge ⟺
Δ-periodicity in T of the reduced fields.** -/
theorem dss_iff_periodic (d : Fields) (Δ : ℝ) :
    (∀ u v, Wedge u v → DSSLawsAt d Δ u v) ↔
      ∀ T x, 0 < x →
        reducedR d (T + Δ) x = reducedR d T x ∧
        reducedG d (T + Δ) x = reducedG d T x ∧
        reducedPhi d (T + Δ) x = reducedPhi d T x := by
  have hcancel : ∀ t : ℝ, Real.exp t * Real.exp (-t) = 1 := by
    intro t
    rw [← Real.exp_add, add_neg_cancel, Real.exp_zero]
  have hEΔ : ∀ T : ℝ, Real.exp (T + Δ) = Real.exp T * Real.exp Δ := fun T =>
    Real.exp_add T Δ
  have hwedge : ∀ T x, 0 < x → Wedge (-Real.exp T) (Real.exp T / x) := by
    intro T x hx
    have hE : (0 : ℝ) < Real.exp T := Real.exp_pos T
    exact ⟨by simp; linarith, div_pos hE hx⟩
  constructor
  · intro hd T x hx
    obtain ⟨hf, hr, hphi⟩ := hd (-Real.exp T) (Real.exp T / x) (hwedge T x hx)
    have hmulu : Real.exp Δ * (-Real.exp T) = -Real.exp (T + Δ) := by
      rw [hEΔ]; ring
    have hmulv : Real.exp Δ * (Real.exp T / x) = Real.exp (T + Δ) / x := by
      rw [hEΔ]; field_simp; ring
    rw [hmulu, hmulv] at hf hr hphi
    have hRfac : d.r (-Real.exp (T + Δ)) (Real.exp (T + Δ) / x)
        = Real.exp (T + Δ) * reducedR d (T + Δ) x := by
      rw [reducedR, ← mul_assoc, hcancel (T + Δ), one_mul]
    have hRfac0 : d.r (-Real.exp T) (Real.exp T / x)
        = Real.exp T * reducedR d T x := by
      rw [reducedR, ← mul_assoc, hcancel T, one_mul]
    rw [hr] at hRfac
    constructor
    · show Real.exp (-(T + Δ)) * d.r (-Real.exp (T + Δ)) (Real.exp (T + Δ) / x)
        = Real.exp (-T) * d.r (-Real.exp T) (Real.exp T / x)
      rw [hr, ← mul_assoc,
        show Real.exp (-(T + Δ)) * Real.exp Δ = Real.exp (-T) from by
          rw [← Real.exp_add, neg_add, add_assoc, neg_add_cancel, add_zero]]
    constructor
    · exact hf
    · exact hphi
  · intro hper u v hw
    obtain ⟨hwu, hwv⟩ := hw
    have hu : (0 : ℝ) < -u := by linarith
    have hv : (0 : ℝ) < v := hwv
    set T := simT u v with hTdef
    set x := simX u v with hxdef
    have hx : (0 : ℝ) < x := div_pos hu hv
    have hE : Real.exp T = -u := by
      show Real.exp (Real.log (-u)) = -u
      exact Real.exp_log hu
    have hV : Real.exp T / x = v := by
      show Real.exp (Real.log (-u)) / (-u / v) = v
      rw [Real.exp_log hu, div_div_eq_mul_div]
      exact mul_div_cancel_left₀ _ (ne_of_gt hu)
    obtain ⟨hR, hG, hPhi⟩ := hper T x hx
    have huE : Real.exp Δ * u = -Real.exp (T + Δ) := by
      rw [hEΔ, hE]; ring
    have hvE : Real.exp Δ * v = Real.exp (T + Δ) / x := by
      rw [← hV, hEΔ]; ring
    have hRfac : d.r (-Real.exp (T + Δ)) (Real.exp (T + Δ) / x)
        = Real.exp (T + Δ) * reducedR d (T + Δ) x := by
      rw [reducedR, ← mul_assoc, hcancel (T + Δ), one_mul]
    have hRfac0 : d.r (-Real.exp T) (Real.exp T / x)
        = Real.exp T * reducedR d T x := by
      rw [reducedR, ← mul_assoc, hcancel T, one_mul]
    have huE' : u = -Real.exp T := by linarith
    have hvE' : v = Real.exp T / x := hV.symm
    refine ⟨?_, ?_, ?_⟩
    · show d.f (Real.exp Δ * u) (Real.exp Δ * v) = d.f u v
      rw [huE, hvE, huE', hvE']
      exact hG
    · show d.r (Real.exp Δ * u) (Real.exp Δ * v) = Real.exp Δ * d.r u v
      rw [huE, hvE, huE', hvE', hRfac, hR, hRfac0, hEΔ]
      ring
    · show d.phi (Real.exp Δ * u) (Real.exp Δ * v) = d.phi u v
      rw [huE, hvE, huE', hvE']
      exact hPhi

/-- **CSS ⟺ T-independent reduced fields** (item 6, continuous form). -/
theorem css_iff_constant (d : Fields) :
    (∀ u v, Wedge u v → ∀ Δ, DSSLawsAt d Δ u v) ↔
      (∀ T T' x, 0 < x → reducedR d T' x = reducedR d T x)
        ∧ (∀ T T' x, 0 < x → reducedG d T' x = reducedG d T x)
        ∧ (∀ T T' x, 0 < x → reducedPhi d T' x = reducedPhi d T x) := by
  constructor
  · intro hcss
    have hper : ∀ Δ T x, 0 < x →
        reducedR d (T + Δ) x = reducedR d T x ∧
        reducedG d (T + Δ) x = reducedG d T x ∧
        reducedPhi d (T + Δ) x = reducedPhi d T x :=
      fun Δ => (dss_iff_periodic d Δ).mp (fun u v hw => hcss u v hw Δ)
    refine ⟨fun T T' x hx => ?_, fun T T' x hx => ?_, fun T T' x hx => ?_⟩
    · obtain ⟨h1, h2, h3⟩ := hper (T' - T) T x hx
      have hsum : T + (T' - T) = T' := by ring
      rw [hsum] at h1
      exact h1
    · obtain ⟨h1, h2, h3⟩ := hper (T' - T) T x hx
      have hsum : T + (T' - T) = T' := by ring
      rw [hsum] at h2
      exact h2
    · obtain ⟨h1, h2, h3⟩ := hper (T' - T) T x hx
      have hsum : T + (T' - T) = T' := by ring
      rw [hsum] at h3
      exact h3
  · rintro ⟨hR, hG, hPhi⟩ u v hw Δ
    exact (dss_iff_periodic d Δ).mpr (fun T x hx =>
      ⟨hR T (T + Δ) x hx, hG T (T + Δ) x hx, hPhi T (T + Δ) x hx⟩) u v hw

/-- **"DSS + equations" ⟺ the periodic BVP in (T, x)** (work-plan item 6,
formal version of step 7): the reduced fields are Δ-periodic in T and the
pulled-back field equations hold — equivalently, the underlying fields
echo on the wedge and solve the system on the regular region.  The
explicit autonomous x-system is a routine pullback of the five equations
of `Choptuik.Analysis.FieldEquations` through the coordinate map
`simUV` (registered with gap G7). -/
theorem dss_solution_iff_periodic_bvp (d : Fields) (Δ : ℝ) :
    ((∀ u v, Wedge u v → DSSLawsAt d Δ u v) ∧
        (∀ u v, Wedge u v → 0 < d.r u v → IsSolution d u v))
      ↔ ((∀ T x, 0 < x →
            reducedR d (T + Δ) x = reducedR d T x ∧
            reducedG d (T + Δ) x = reducedG d T x ∧
            reducedPhi d (T + Δ) x = reducedPhi d T x)
          ∧ (∀ T x, 0 < x → 0 < d.r (simUV T x).1 (simUV T x).2 →
            IsSolution d (simUV T x).1 (simUV T x).2)) := by
  have hwedge : ∀ T x, 0 < x → Wedge (simUV T x).1 (simUV T x).2 := by
    intro T x hx
    have hE : (0 : ℝ) < Real.exp T := Real.exp_pos T
    exact ⟨by show -Real.exp T < 0; linarith, by
      show (0:ℝ) < Real.exp T / x; exact div_pos hE hx⟩
  constructor
  · rintro ⟨hdss, hsol⟩
    refine ⟨(dss_iff_periodic d Δ).mp hdss, ?_⟩
    intro T x hx hr
    exact hsol (simUV T x).1 (simUV T x).2 (hwedge T x hx) hr
  · rintro ⟨hper, hpbvp⟩
    refine ⟨(dss_iff_periodic d Δ).mpr hper, ?_⟩
    intro u v hw hr
    obtain ⟨hwu, hwv⟩ := hw
    have hx : (0:ℝ) < simX u v := by
      show (0:ℝ) < -u / v
      exact div_pos (by linarith) (by linarith)
    have huv : (u, v) = simUV (simT u v) (simX u v) :=
      (uv_of_wedge ⟨hwu, hwv⟩).symm
    have hpoint : (0:ℝ) < d.r (simUV (simT u v) (simX u v)).1
        (simUV (simT u v) (simX u v)).2 := by
      rw [← huv]
      exact hr
    have hs := hpbvp (simT u v) (simX u v) hx hpoint
    rw [← huv] at hs
    exact hs

end Choptuik.Existence
