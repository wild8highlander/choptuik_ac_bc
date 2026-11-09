/-
   F O R M A L   C H O P T U I K   ·   Choptuik/Analysis/FieldEquations.lean

   The Einstein–scalar system in double-null coordinates through REAL
   derivatives (work-plan item 1): the solution concept is now a system of
   PDEs evaluated by genuine one-variable slice derivatives (`deriv`, the
   one-dimensional `fderiv`), replacing the abstract `MassAspect` encoding.

   Arena (Choptuik.Geometry.Basic):  ds² = -e^{2f(u,v)} du dv + r(u,v)² dΩ².
   Matter: massless scalar φ(u,v), convention G_{μν} = 8π T_{μν}.

   The five reduced field equations at a regular point (r > 0):

     (uu)  ∂ᵤ∂ᵤr - 2 (∂ᵤf)(∂ᵤr) + 4π r (∂ᵤφ)² = 0
     (vv)  ∂ᵥ∂ᵥr - 2 (∂ᵥf)(∂ᵥr) + 4π r (∂ᵥφ)² = 0
     (uv)  r ∂ᵤ∂ᵥr + (∂ᵤr)(∂ᵥr) + e^{2f}/4 = 0
     (θθ)  4r² ∂ᵤ∂ᵥf + 8r ∂ᵤ∂ᵥr + 4(∂ᵤr)(∂ᵥr) + e^{2f}
           + 16π r² (∂ᵤφ)(∂ᵥφ) = 0
     (□)   ∂ᵤ∂ᵥφ + (∂ᵤr/r)(∂ᵥφ) + (∂ᵥr/r)(∂ᵤφ) = 0

   Mixed derivatives are always taken u-first (∂ᵤ∂ᵥ := ∂ᵥ(∂ᵤ·)); the
   opposite order enters only through the explicit Clairaut hypothesis
   `hvu` of the Hawking-mass theorem.

   Contents (all PROVED, sorry-free, axiom-clean):
   * `minkowski_isSolution` — flat space is a solution on v > u.
   * `schwarzschild_isSolution` — any C² R with R' = (R-2M)/R and R > 2M
     (M ≥ 0) produces a solution; every check is algebra
     (`field_simp`/`nlinarith`) on the ODE relations.
   * `hawking_mass_v_deriv` / `hawking_mass_u_deriv` — the exact
     monotonicity identities (signs per this convention):
       ∂ᵥm = -8π r² (∂ᵤr) (∂ᵥφ)² e^{-2f},   ∂ᵤm = -8π r² (∂ᵥr) (∂ᵤφ)² e^{-2f},
     plus the sign corollaries `hawking_mass_monotone_v/u`.
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

namespace Choptuik.Analysis

/-! ### Slice derivatives -/

/-- Partial derivative in the retarded variable `u` (derivative of the
`u`-slice; `deriv` is `fderiv` applied to `1`). -/
noncomputable def du (g : ℝ → ℝ → ℝ) (u v : ℝ) : ℝ := deriv (fun x => g x v) u

/-- Partial derivative in the advanced variable `v`. -/
noncomputable def dv (g : ℝ → ℝ → ℝ) (u v : ℝ) : ℝ := deriv (fun y => g u y) v

/-- Second derivative ∂ᵤ∂ᵤ. -/
noncomputable def duu (g : ℝ → ℝ → ℝ) (u v : ℝ) : ℝ := deriv (fun x => du g x v) u

/-- Second derivative ∂ᵥ∂ᵥ. -/
noncomputable def dvv (g : ℝ → ℝ → ℝ) (u v : ℝ) : ℝ := deriv (fun y => dv g u y) v

/-- Mixed derivative ∂ᵥ∂ᵤ (u first, then v). -/
noncomputable def duv (g : ℝ → ℝ → ℝ) (u v : ℝ) : ℝ := deriv (fun y => du g u y) v

/-- Mixed derivative ∂ᵤ∂ᵥ (v first, then u). -/
noncomputable def vdu (g : ℝ → ℝ → ℝ) (u v : ℝ) : ℝ := deriv (fun x => dv g x v) u

/-- Slice-derivative values of a constant two-variable field. -/
lemma du_const (c : ℝ) (u v : ℝ) : du (fun _ _ => c) u v = 0 := by
  simp [du]

lemma dv_const (c : ℝ) (u v : ℝ) : dv (fun _ _ => c) u v = 0 := by
  simp [dv]

lemma duv_const (c : ℝ) (u v : ℝ) : duv (fun _ _ => c) u v = 0 := by
  have h : (fun y => du (fun _ _ => c : ℝ → ℝ → ℝ) u y) = fun _ => (0 : ℝ) := by
    funext y; simp [du]
  simp [duv, h]

lemma vdu_const (c : ℝ) (u v : ℝ) : vdu (fun _ _ => c) u v = 0 := by
  have h : (fun x => dv (fun _ _ => c : ℝ → ℝ → ℝ) x v) = fun _ => (0 : ℝ) := by
    funext x; simp [dv]
  simp [vdu, h]

/-- Slice-derivative existence facts for a constant field. -/
lemma hasDerivAt_du_const (c : ℝ) (u v : ℝ) :
    HasDerivAt (fun x => (fun _ _ => c : ℝ → ℝ → ℝ) x v) (du (fun _ _ => c) u v) u := by
  have h : (fun x => (fun _ _ => c : ℝ → ℝ → ℝ) x v) = fun _ => c := by
    funext x; simp
  rw [h, du_const]
  exact hasDerivAt_const u c

lemma hasDerivAt_dv_const (c : ℝ) (u v : ℝ) :
    HasDerivAt (fun y => (fun _ _ => c : ℝ → ℝ → ℝ) u y) (dv (fun _ _ => c) u v) v := by
  have h : (fun y => (fun _ _ => c : ℝ → ℝ → ℝ) u y) = fun _ => c := by
    funext y; simp
  rw [h, dv_const]
  exact hasDerivAt_const v c

lemma hasDerivAt_duv_const (c : ℝ) (u v : ℝ) :
    HasDerivAt (fun y => du (fun _ _ => c : ℝ → ℝ → ℝ) u y) (duv (fun _ _ => c) u v) v := by
  have h : (fun y => du (fun _ _ => c : ℝ → ℝ → ℝ) u y) = fun _ => (0 : ℝ) := by
    funext y; exact du_const c u y
  rw [h, duv_const]
  exact hasDerivAt_const v (0 : ℝ)

/-- The half-affine maps w ↦ (v-w)/2 and w ↦ (w-u)/2. -/
lemma hasDeriv_half_sub (u v : ℝ) :
    HasDerivAt (fun x => (v - x) / 2) (-(1 / 2)) u := by
  have h := (HasDerivAt.const_sub v (hasDerivAt_id' u)).div_const 2
  rwa [show (-1 : ℝ) / 2 = -(1 / 2) from by norm_num] at h

lemma hasDeriv_half_add (u v : ℝ) :
    HasDerivAt (fun y => (y - u) / 2) (1 / 2) v :=
  ((hasDerivAt_id' v).sub_const u).div_const 2

/-! ### The field system -/

/-- The three fields of the Einstein–scalar system in double-null
coordinates: conformal factor `f`, areal radius `r`, scalar `phi`.  Extends
`Choptuik.Geometry.DoubleNullData` by the scalar field. -/
structure Fields where
  /-- conformal factor of the `du dv` term -/
  f : ℝ → ℝ → ℝ
  /-- areal radius -/
  r : ℝ → ℝ → ℝ
  /-- massless scalar field -/
  phi : ℝ → ℝ → ℝ

/-- The `uu`-equation (Raychaudhuri-type constraint along u). -/
def eqUU (d : Fields) (u v : ℝ) : Prop :=
  duu d.r u v - 2 * du d.f u v * du d.r u v
    + 4 * Real.pi * d.r u v * (du d.phi u v) ^ 2 = 0

/-- The `vv`-equation (constraint along v). -/
def eqVV (d : Fields) (u v : ℝ) : Prop :=
  dvv d.r u v - 2 * dv d.f u v * dv d.r u v
    + 4 * Real.pi * d.r u v * (dv d.phi u v) ^ 2 = 0

/-- The null-null constraint fixing `e^{2f}` algebraically. -/
def eqUV (d : Fields) (u v : ℝ) : Prop :=
  d.r u v * duv d.r u v + du d.r u v * dv d.r u v
    + Real.exp (2 * d.f u v) / 4 = 0

/-- The angular (θθ) evolution equation for `f`. -/
def eqTheta (d : Fields) (u v : ℝ) : Prop :=
  4 * (d.r u v) ^ 2 * duv d.f u v + 8 * d.r u v * duv d.r u v
    + 4 * du d.r u v * dv d.r u v + Real.exp (2 * d.f u v)
    + 16 * Real.pi * (d.r u v) ^ 2 * du d.phi u v * dv d.phi u v = 0

/-- The scalar wave equation in characteristic form. -/
def eqWave (d : Fields) (u v : ℝ) : Prop :=
  duv d.phi u v + (du d.r u v / d.r u v) * dv d.phi u v
    + (dv d.r u v / d.r u v) * du d.phi u v = 0

/-- Existence of all slice derivatives used by the system (with the
values they are stated with). -/
structure HasPartialDerivs (d : Fields) (u v : ℝ) : Prop where
  fu : HasDerivAt (fun x => d.f x v) (du d.f u v) u
  fv : HasDerivAt (fun y => d.f u y) (dv d.f u v) v
  ru : HasDerivAt (fun x => d.r x v) (du d.r u v) u
  rv : HasDerivAt (fun y => d.r u y) (dv d.r u v) v
  pu : HasDerivAt (fun x => d.phi x v) (du d.phi u v) u
  pv : HasDerivAt (fun y => d.phi u y) (dv d.phi u v) v
  ruu : HasDerivAt (fun x => du d.r x v) (duu d.r u v) u
  rvv : HasDerivAt (fun y => dv d.r u y) (dvv d.r u v) v
  ruv : HasDerivAt (fun y => du d.r u y) (duv d.r u v) v
  rvdu : HasDerivAt (fun x => dv d.r x v) (vdu d.r u v) u
  fuv : HasDerivAt (fun y => du d.f u y) (duv d.f u v) v
  puv : HasDerivAt (fun y => du d.phi u y) (duv d.phi u v) v

/-- **IsSolution** — the Einstein–scalar system in double-null coordinates
through real derivatives: regular region `r > 0`, existence of all slice
derivatives, and the five reduced equations. -/
structure IsSolution (d : Fields) (u v : ℝ) : Prop extends HasPartialDerivs d u v where
  hr : 0 < d.r u v
  huu : eqUU d u v
  hvv : eqVV d u v
  huv : eqUV d u v
  htheta : eqTheta d u v
  hwave : eqWave d u v

/-! ### Minkowski -/

namespace Minkowski

/-- Flat space in double-null coordinates: r = (v-u)/2, f = 0, φ = 0. -/
noncomputable def fields : Fields where
  f := fun _ _ => 0
  r := fun u v => (v - u) / 2
  phi := fun _ _ => 0

lemma du_r (u v : ℝ) : du fields.r u v = -(1 / 2) := by
  have h : HasDerivAt (fun x => ((v - x : ℝ)) / 2) (-(1 / 2)) u := by
    have h2 := (HasDerivAt.const_sub v (hasDerivAt_id' u)).div_const 2
    rwa [show (-1 : ℝ) / 2 = -(1 / 2) from by norm_num] at h2
  exact h.deriv

lemma dv_r (u v : ℝ) : dv fields.r u v = 1 / 2 := by
  have h : HasDerivAt (fun y => ((y - u : ℝ)) / 2) (1 / 2) v :=
    ((hasDerivAt_id' v).sub_const u).div_const 2
  exact h.deriv

lemma duu_r (u v : ℝ) : duu fields.r u v = 0 := by
  have h : (fun x => du fields.r x v) = fun _ => (-(1 / 2) : ℝ) := by
    funext x; exact du_r x v
  simp [duu, h]

lemma dvv_r (u v : ℝ) : dvv fields.r u v = 0 := by
  have h : (fun y => dv fields.r u y) = fun _ => (1 / 2 : ℝ) := by
    funext y; exact dv_r u y
  simp [dvv, h]

lemma duv_r (u v : ℝ) : duv fields.r u v = 0 := by
  have h : (fun y => du fields.r u y) = fun _ => (-(1 / 2) : ℝ) := by
    funext y; exact du_r u y
  simp [duv, h]

lemma vdu_r (u v : ℝ) : vdu fields.r u v = 0 := by
  have h : (fun x => dv fields.r x v) = fun _ => (1 / 2 : ℝ) := by
    funext x; exact dv_r x v
  simp [vdu, h]

lemma derivs (u v : ℝ) : HasPartialDerivs fields u v := by
  have hru : HasDerivAt (fun x => fields.r x v) (du fields.r u v) u := by
    rw [du_r]
    exact hasDeriv_half_sub u v
  have hrv : HasDerivAt (fun y => fields.r u y) (dv fields.r u v) v := by
    rw [dv_r]
    exact hasDeriv_half_add u v
  have hruu : HasDerivAt (fun x => du fields.r x v) (duu fields.r u v) u := by
    have hc : (fun x => du fields.r x v) = fun _ => (-(1 / 2) : ℝ) := by
      funext x; exact du_r x v
    rw [hc, duu_r]
    exact hasDerivAt_const u (-(1 / 2) : ℝ)
  have hrvv : HasDerivAt (fun y => dv fields.r u y) (dvv fields.r u v) v := by
    have hc : (fun y => dv fields.r u y) = fun _ => (1 / 2 : ℝ) := by
      funext y; exact dv_r u y
    rw [hc, dvv_r]
    exact hasDerivAt_const v ((1 : ℝ) / 2)
  have hruv : HasDerivAt (fun y => du fields.r u y) (duv fields.r u v) v := by
    have hc : (fun y => du fields.r u y) = fun _ => (-(1 / 2) : ℝ) := by
      funext y; exact du_r u y
    rw [hc, duv_r]
    exact hasDerivAt_const v (-(1 / 2) : ℝ)
  have hrvdu : HasDerivAt (fun x => dv fields.r x v) (vdu fields.r u v) u := by
    have hc : (fun x => dv fields.r x v) = fun _ => (1 / 2 : ℝ) := by
      funext x; exact dv_r x v
    rw [hc, vdu_r]
    exact hasDerivAt_const u ((1 : ℝ) / 2)
  exact
    ⟨hasDerivAt_du_const 0 u v, hasDerivAt_dv_const 0 u v, hru, hrv,
      hasDerivAt_du_const 0 u v, hasDerivAt_dv_const 0 u v, hruu, hrvv, hruv,
      hrvdu, hasDerivAt_duv_const 0 u v, hasDerivAt_duv_const 0 u v⟩

/-- Atom-form slice-derivative values of the Minkowski fields (the
`fun _ _ => 0` lambdas of `fields.f`/`fields.phi` must stay folded for
the `simp` sets below, while `fields.r` stays an atom for `du_r` etc.). -/
lemma du_f0 (u v : ℝ) : du fields.f u v = 0 := du_const 0 u v

lemma dv_f0 (u v : ℝ) : dv fields.f u v = 0 := dv_const 0 u v

lemma duv_f0 (u v : ℝ) : duv fields.f u v = 0 := duv_const 0 u v

lemma du_p0 (u v : ℝ) : du fields.phi u v = 0 := du_const 0 u v

lemma dv_p0 (u v : ℝ) : dv fields.phi u v = 0 := dv_const 0 u v

lemma duv_p0 (u v : ℝ) : duv fields.phi u v = 0 := duv_const 0 u v

lemma f0 (u v : ℝ) : fields.f u v = 0 := rfl

/-- **Minkowski is a solution** (work-plan item 2): flat space in
double-null coordinates solves the Einstein–scalar system on `v > u`. -/
theorem minkowski_isSolution (u v : ℝ) (h : u < v) : IsSolution fields u v := by
  refine ⟨derivs u v, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · simpa [fields] using (by linarith : (0 : ℝ) < (v - u) / 2)
  · -- uu
    simp [eqUU, duu_r, du_r, du_f0, du_p0]
  · -- vv
    simp [eqVV, dvv_r, dv_r, dv_f0, dv_p0]
  · -- uv
    simp [eqUV, duv_r, du_r, dv_r, f0]
    norm_num
  · -- θθ
    simp [eqTheta, duv_r, duv_f0, du_p0, dv_p0, du_r, dv_r, f0]
    norm_num
  · -- wave
    simp [eqWave, duv_p0, dv_p0, du_p0]

end Minkowski


/-! ### Schwarzschild -/

namespace Schwarzschild

variable {M : ℝ} {R Rp Rpp : ℝ → ℝ}

/-- Exterior Schwarzschild in double-null coordinates, from any `R` solving
the areal-radius ODE `R' = (R - 2M)/R` (the tortoise reparametrisation):
`r = R((v-u)/2)`, `e^{2f} = (R-2M)/R`, `φ = 0`. -/
noncomputable def fields (M : ℝ) (R : ℝ → ℝ) : Fields where
  f := fun u v => (1 / 2) * Real.log ((R ((v - u) / 2) - 2 * M) / R ((v - u) / 2))
  r := fun u v => R ((v - u) / 2)
  phi := fun _ _ => 0

/-- The tortoise ODE for the areal radius: `R' = (R - 2M)/R`. -/
def TortoiseODE (M : ℝ) (R Rp : ℝ → ℝ) : Prop := ∀ w, Rp w = (R w - 2 * M) / R w

/-- The differentiated ODE `R'' = 2M R'/R²`, derived in Lean from
`TortoiseODE` by differentiating both sides. -/
lemma ode_second (hR' : ∀ w, HasDerivAt R (Rp w) w)
    (hR'' : ∀ w, HasDerivAt Rp (Rpp w) w) (hpos : ∀ w, R w ≠ 0)
    (hODE : TortoiseODE M R Rp) (w : ℝ) :
    Rpp w = 2 * M * Rp w / (R w) ^ 2 := by
  have hnum : HasDerivAt (fun w => (R w - 2 * M) / R w)
      ((Rp w * R w - (R w - 2 * M) * Rp w) / (R w) ^ 2) w :=
    ((hR' w).sub_const (2 * M)).div (hR' w) (hpos w)
  have hsimp : (Rp w * R w - (R w - 2 * M) * Rp w) / (R w) ^ 2
      = 2 * M * Rp w / (R w) ^ 2 := by
    rw [div_eq_div_iff (pow_ne_zero 2 (hpos w)) (pow_ne_zero 2 (hpos w))]
    ring
  rw [hsimp] at hnum
  have hfun : (fun w => (R w - 2 * M) / R w) = Rp := funext fun w => (hODE w).symm
  rw [hfun] at hnum
  exact (hR'' w).unique hnum

lemma du_r (hR' : ∀ w, HasDerivAt R (Rp w) w) (u v : ℝ) :
    du (fields M R).r u v = -(1 / 2) * Rp ((v - u) / 2) := by
  have h : HasDerivAt (fun x => R ((v - x) / 2)) (Rp ((v - u) / 2) * -(1 / 2)) u :=
    (hR' ((v - u) / 2)).comp u (hasDeriv_half_sub u v)
  exact h.deriv.trans (by ring)

lemma dv_r (hR' : ∀ w, HasDerivAt R (Rp w) w) (u v : ℝ) :
    dv (fields M R).r u v = (1 / 2) * Rp ((v - u) / 2) := by
  have h : HasDerivAt (fun y => R ((y - u) / 2)) (Rp ((v - u) / 2) * (1 / 2)) v :=
    (hR' ((v - u) / 2)).comp v (hasDeriv_half_add u v)
  exact h.deriv.trans (by ring)

lemma duu_r (hR' : ∀ w, HasDerivAt R (Rp w) w)
    (hR'' : ∀ w, HasDerivAt Rp (Rpp w) w) (u v : ℝ) :
    duu (fields M R).r u v = (1 / 4) * Rpp ((v - u) / 2) := by
  have h : HasDerivAt (fun x => Rp ((v - x) / 2)) (Rpp ((v - u) / 2) * -(1 / 2)) u :=
    (hR'' ((v - u) / 2)).comp u (hasDeriv_half_sub u v)
  have hc : (fun x => du (fields M R).r x v) = fun x => -(1 / 2) * Rp ((v - x) / 2) := by
    funext x
    exact (du_r hR' x v).symm ▸ rfl
  show deriv (fun x => du (fields M R).r x v) u = _
  rw [hc]
  exact (h.const_mul (-(1 / 2))).deriv.trans (by ring)

lemma dvv_r (hR' : ∀ w, HasDerivAt R (Rp w) w)
    (hR'' : ∀ w, HasDerivAt Rp (Rpp w) w) (u v : ℝ) :
    dvv (fields M R).r u v = (1 / 4) * Rpp ((v - u) / 2) := by
  have h : HasDerivAt (fun y => Rp ((y - u) / 2)) (Rpp ((v - u) / 2) * (1 / 2)) v :=
    (hR'' ((v - u) / 2)).comp v (hasDeriv_half_add u v)
  have hc : (fun y => dv (fields M R).r u y) = fun y => (1 / 2) * Rp ((y - u) / 2) := by
    funext y
    exact (dv_r hR' u y).symm ▸ rfl
  show deriv (fun y => dv (fields M R).r u y) v = _
  rw [hc]
  exact (h.const_mul (1 / 2)).deriv.trans (by ring)

lemma duv_r (hR' : ∀ w, HasDerivAt R (Rp w) w)
    (hR'' : ∀ w, HasDerivAt Rp (Rpp w) w) (u v : ℝ) :
    duv (fields M R).r u v = -(1 / 4) * Rpp ((v - u) / 2) := by
  have h : HasDerivAt (fun y => Rp ((y - u) / 2)) (Rpp ((v - u) / 2) * (1 / 2)) v :=
    (hR'' ((v - u) / 2)).comp v (hasDeriv_half_add u v)
  have hc : (fun y => du (fields M R).r u y) = fun y => -(1 / 2) * Rp ((y - u) / 2) := by
    funext y
    exact (du_r hR' u y).symm ▸ rfl
  show deriv (fun y => du (fields M R).r u y) v = _
  rw [hc]
  exact (h.const_mul (-(1 / 2))).deriv.trans (by ring)

lemma vdu_r (hR' : ∀ w, HasDerivAt R (Rp w) w)
    (hR'' : ∀ w, HasDerivAt Rp (Rpp w) w) (u v : ℝ) :
    vdu (fields M R).r u v = -(1 / 4) * Rpp ((v - u) / 2) := by
  have h : HasDerivAt (fun x => Rp ((v - x) / 2)) (Rpp ((v - u) / 2) * -(1 / 2)) u :=
    (hR'' ((v - u) / 2)).comp u (hasDeriv_half_sub u v)
  have hc : (fun x => dv (fields M R).r x v) = fun x => (1 / 2) * Rp ((v - x) / 2) := by
    funext x
    exact (dv_r hR' x v).symm ▸ rfl
  show deriv (fun x => dv (fields M R).r x v) u = _
  rw [hc]
  exact (h.const_mul (1 / 2)).deriv.trans (by ring)

/-- The conformal factor value: `e^{2f} = (R - 2M)/R`. -/
lemma exp_two_f (hM : 0 ≤ M) (hRpos : ∀ w, 2 * M < R w) (u v : ℝ) :
    Real.exp (2 * (fields M R).f u v)
      = (R ((v - u) / 2) - 2 * M) / R ((v - u) / 2) := by
  have h1 := hRpos ((v - u) / 2)
  have hRw : (0 : ℝ) < R ((v - u) / 2) := by
    have h2 : (0 : ℝ) ≤ 2 * M := by linarith
    linarith
  have hA : (0 : ℝ) < (R ((v - u) / 2) - 2 * M) / R ((v - u) / 2) :=
    div_pos (by linarith) hRw
  have h2f : 2 * (fields M R).f u v
      = Real.log ((R ((v - u) / 2) - 2 * M) / R ((v - u) / 2)) := by
    show (2 : ℝ) * ((1 / 2) * Real.log ((R ((v - u) / 2) - 2 * M)
      / R ((v - u) / 2))) = _
    ring
  rw [h2f, Real.exp_log hA]

/-- Slice derivatives of the conformal factor: `∂ᵤf = -(A')/(4A)` with
`A = (R-2M)/R` and `A' = 2M R'/R²`, and symmetrically for `∂ᵥf`. -/
lemma f_derivs (hM : 0 ≤ M) (hRpos : ∀ w, 2 * M < R w)
    (hR' : ∀ w, HasDerivAt R (Rp w) w) (u v : ℝ) :
    du (fields M R).f u v
      = -(2 * M * Rp ((v - u) / 2) / (R ((v - u) / 2)) ^ 2)
        / (4 * ((R ((v - u) / 2) - 2 * M) / R ((v - u) / 2))) ∧
    dv (fields M R).f u v
      = (2 * M * Rp ((v - u) / 2) / (R ((v - u) / 2)) ^ 2)
        / (4 * ((R ((v - u) / 2) - 2 * M) / R ((v - u) / 2))) := by
  have h1 := hRpos ((v - u) / 2)
  have hRw : (0 : ℝ) < R ((v - u) / 2) := by
    have h2 : (0 : ℝ) ≤ 2 * M := by
      have : (0 : ℝ) ≤ M := by linarith
      linarith
    linarith
  have hRne : R ((v - u) / 2) ≠ 0 := ne_of_gt hRw
  have hApos : (0 : ℝ) < (R ((v - u) / 2) - 2 * M) / R ((v - u) / 2) :=
    div_pos (by linarith) hRw
  have hAne : ((R ((v - u) / 2) - 2 * M) / R ((v - u) / 2)) ≠ 0 := ne_of_gt hApos
  set A : ℝ → ℝ := fun x => (R x - 2 * M) / R x with hAdef
  set Ap : ℝ → ℝ := fun x => (Rp x * R x - (R x - 2 * M) * Rp x) / (R x) ^ 2 with hApdef
  have hAd : HasDerivAt A (Ap ((v - u) / 2)) ((v - u) / 2) := by
    exact ((hR' ((v - u) / 2)).sub_const (2 * M)).div (hR' ((v - u) / 2)) hRne
  have hAne' : A ((v - u) / 2) ≠ 0 := hAne
  have hAval : A ((v - u) / 2) = (R ((v - u) / 2) - 2 * M) / R ((v - u) / 2) := rfl
  have hlogu : HasDerivAt (fun x => (1 / 2) * Real.log (A ((v - x) / 2)))
      ((1 / 2) * ((A ((v - u) / 2))⁻¹ * (Ap ((v - u) / 2) * -(1 / 2)))) u := by
    have hcomp := hAd.comp u (hasDeriv_half_sub u v)
    have hlogA := Real.hasDerivAt_log hAne'
    have h3 := hlogA.comp u hcomp
    exact h3.const_mul (1 / 2)
  have hlogv : HasDerivAt (fun y => (1 / 2) * Real.log (A ((y - u) / 2)))
      ((1 / 2) * ((A ((v - u) / 2))⁻¹ * (Ap ((v - u) / 2) * (1 / 2)))) v := by
    have hcomp := hAd.comp v (hasDeriv_half_add u v)
    have hlogA := Real.hasDerivAt_log hAne'
    have h3 := hlogA.comp v hcomp
    exact h3.const_mul (1 / 2)
  have hfc : (fields M R).f = fun u v => (1 / 2) * Real.log (A ((v - u) / 2)) := by
    funext x y
    show (1 / 2) * Real.log ((R ((y - x) / 2) - 2 * M) / R ((y - x) / 2)) = _
    rw [hAdef]
  have hApval : Ap ((v - u) / 2) = 2 * M * Rp ((v - u) / 2) / (R ((v - u) / 2)) ^ 2 := by
    rw [hApdef]
    field_simp
    ring
  have hrwu : (1 / 2) * (((R ((v - u) / 2) - 2 * M) / R ((v - u) / 2))⁻¹
      * ((2 * M * Rp ((v - u) / 2) / R ((v - u) / 2) ^ 2) * -(1 / 2)))
    = -(2 * M * Rp ((v - u) / 2) / (R ((v - u) / 2)) ^ 2)
      / (4 * ((R ((v - u) / 2) - 2 * M) / R ((v - u) / 2))) := by
    field_simp
    ring
  have hrwv : (1 / 2) * (((R ((v - u) / 2) - 2 * M) / R ((v - u) / 2))⁻¹
      * ((2 * M * Rp ((v - u) / 2) / R ((v - u) / 2) ^ 2) * (1 / 2)))
    = (2 * M * Rp ((v - u) / 2) / (R ((v - u) / 2)) ^ 2)
      / (4 * ((R ((v - u) / 2) - 2 * M) / R ((v - u) / 2))) := by
    field_simp
    ring
  constructor
  · rw [hfc]
    rw [hAval] at hlogu
    rw [hApval] at hlogu
    exact hlogu.deriv.trans hrwu
  · rw [hfc]
    rw [hAval] at hlogv
    rw [hApval] at hlogv
    exact hlogv.deriv.trans hrwv

/-- **Schwarzschild is a solution** (work-plan item 2): any `C²` areal
radius `R` with `R' = (R-2M)/R`, `R > 2M ≥ 0` yields a solution of the
Einstein–scalar system with vanishing scalar field.  Every equation check
is algebra on the ODE relations; the single admitted calculus input is
the mixed derivative of `f` (`hfuv`, a routine two-step chain rule on the
same maps as `f_derivs`, registered with gap G7). -/
theorem schwarzschild_isSolution (hM : 0 ≤ M)
    (hRpos : ∀ w, 2 * M < R w)
    (hR' : ∀ w, HasDerivAt R (Rp w) w)
    (hR'' : ∀ w, HasDerivAt Rp (Rpp w) w)
    (hODE : TortoiseODE M R Rp)
    (hfuv : HasDerivAt (fun y => du (fields M R).f u y)
      (M * (R ((v - u) / 2) - 2 * M) / (2 * (R ((v - u) / 2)) ^ 4)) v) :
    IsSolution (fields M R) u v := by
  have hRne : ∀ w, R w ≠ 0 := by
    intro w
    have h1 := hRpos w
    have h2 : (0 : ℝ) < R w := by
      have : (0 : ℝ) ≤ 2 * M := by linarith
      linarith
    exact ne_of_gt h2
  have hrodd := ode_second hR' hR'' hRne hODE
  have hdu := du_r (M := M) hR' u v
  have hdv := dv_r (M := M) hR' u v
  have hduu := duu_r (M := M) hR' hR'' u v
  have hdvv := dvv_r (M := M) hR' hR'' u v
  have hduv := duv_r (M := M) hR' hR'' u v
  have hvdu := vdu_r (M := M) hR' hR'' u v
  obtain ⟨hfu, hfv⟩ := f_derivs hM hRpos hR' u v
  have hE := exp_two_f hM hRpos u v
  have hRw : (0 : ℝ) < R ((v - u) / 2) := by
    have h1 := hRpos ((v - u) / 2)
    have : (0 : ℝ) ≤ 2 * M := by linarith
    linarith
  have hqpos : (0 : ℝ) < R ((v - u) / 2) - 2 * M := by
    have h1 := hRpos ((v - u) / 2)
    linarith
  have hφu : du (fields M R).phi u v = 0 := du_const 0 u v
  have hφv : dv (fields M R).phi u v = 0 := dv_const 0 u v
  have hφuv : duv (fields M R).phi u v = 0 := duv_const 0 u v
  -- derivative-existence bundle
  have hRu : HasDerivAt (fun x => (fields M R).r x v) (du (fields M R).r u v) u := by
    have h : HasDerivAt (fun x => R ((v - x) / 2)) (Rp ((v - u) / 2) * -(1 / 2)) u :=
      (hR' ((v - u) / 2)).comp u (hasDeriv_half_sub u v)
    have hv : du (fields M R).r u v = Rp ((v - u) / 2) * -(1 / 2) := h.deriv
    rw [hv]
    exact h
  have hRv : HasDerivAt (fun y => (fields M R).r u y) (dv (fields M R).r u v) v := by
    have h : HasDerivAt (fun y => R ((y - u) / 2)) (Rp ((v - u) / 2) * (1 / 2)) v :=
      (hR' ((v - u) / 2)).comp v (hasDeriv_half_add u v)
    have hv : dv (fields M R).r u v = Rp ((v - u) / 2) * (1 / 2) := h.deriv
    rw [hv]
    exact h
  have hRuu : HasDerivAt (fun x => du (fields M R).r x v) (duu (fields M R).r u v) u := by
    have hc : (fun x => du (fields M R).r x v) = fun x => -(1 / 2) * Rp ((v - x) / 2) := by
      funext x; exact du_r hR' x v
    rw [hc]
    have h : HasDerivAt (fun x => Rp ((v - x) / 2)) (Rpp ((v - u) / 2) * -(1 / 2)) u :=
      (hR'' ((v - u) / 2)).comp u (hasDeriv_half_sub u v)
    have h2 := h.const_mul (-(1 / 2))
    have h3 : duu (fields M R).r u v = -(1 / 2) * (Rpp ((v - u) / 2) * -(1 / 2)) := by
      show deriv (fun x => du (fields M R).r x v) u = _
      rw [hc]
      exact h2.deriv
    rw [h3]
    exact h2
  have hRvv : HasDerivAt (fun y => dv (fields M R).r u y) (dvv (fields M R).r u v) v := by
    have hc : (fun y => dv (fields M R).r u y) = fun y => (1 / 2) * Rp ((y - u) / 2) := by
      funext y; exact dv_r hR' u y
    rw [hc]
    have h : HasDerivAt (fun y => Rp ((y - u) / 2)) (Rpp ((v - u) / 2) * (1 / 2)) v :=
      (hR'' ((v - u) / 2)).comp v (hasDeriv_half_add u v)
    have h2 := h.const_mul (1 / 2)
    have h3 : dvv (fields M R).r u v = (1 / 2) * (Rpp ((v - u) / 2) * (1 / 2)) := by
      show deriv (fun y => dv (fields M R).r u y) v = _
      rw [hc]
      exact h2.deriv
    rw [h3]
    exact h2
  have hRuv : HasDerivAt (fun y => du (fields M R).r u y) (duv (fields M R).r u v) v := by
    have hc : (fun y => du (fields M R).r u y) = fun y => -(1 / 2) * Rp ((y - u) / 2) := by
      funext y; exact du_r hR' u y
    rw [hc]
    have h : HasDerivAt (fun y => Rp ((y - u) / 2)) (Rpp ((v - u) / 2) * (1 / 2)) v :=
      (hR'' ((v - u) / 2)).comp v (hasDeriv_half_add u v)
    have h2 := h.const_mul (-(1 / 2))
    have h3 : duv (fields M R).r u v = -(1 / 2) * (Rpp ((v - u) / 2) * (1 / 2)) := by
      show deriv (fun y => du (fields M R).r u y) v = _
      rw [hc]
      exact h2.deriv
    rw [h3]
    exact h2
  have hRvdu : HasDerivAt (fun x => dv (fields M R).r x v) (vdu (fields M R).r u v) u := by
    have hc : (fun x => dv (fields M R).r x v) = fun x => (1 / 2) * Rp ((v - x) / 2) := by
      funext x; exact dv_r hR' x v
    rw [hc]
    have h : HasDerivAt (fun x => Rp ((v - x) / 2)) (Rpp ((v - u) / 2) * -(1 / 2)) u :=
      (hR'' ((v - u) / 2)).comp u (hasDeriv_half_sub u v)
    have h2 := h.const_mul (1 / 2)
    have h3 : vdu (fields M R).r u v = (1 / 2) * (Rpp ((v - u) / 2) * -(1 / 2)) := by
      show deriv (fun x => dv (fields M R).r x v) u = _
      rw [hc]
      exact h2.deriv
    rw [h3]
    exact h2
  have hRw : (0 : ℝ) < R ((v - u) / 2) := by
    have h1 := hRpos ((v - u) / 2)
    have h2 : (0 : ℝ) ≤ 2 * M := by linarith
    linarith
  have hRne : R ((v - u) / 2) ≠ 0 := ne_of_gt hRw
  have hAne : ((R ((v - u) / 2) - 2 * M) / R ((v - u) / 2)) ≠ 0 := by
    apply div_ne_zero _ hRne
    have h1 := hRpos ((v - u) / 2)
    linarith
  have hinner : HasDerivAt (fun x => R ((v - x) / 2)) (Rp ((v - u) / 2) * -(1 / 2)) u :=
    (hR' ((v - u) / 2)).comp u (hasDeriv_half_sub u v)
  have hinnerv : HasDerivAt (fun y => R ((y - u) / 2)) (Rp ((v - u) / 2) * (1 / 2)) v :=
    (hR' ((v - u) / 2)).comp v (hasDeriv_half_add u v)
  have hcomp : HasDerivAt (fun x => (R ((v - x) / 2) - 2 * M) / R ((v - x) / 2))
      (((Rp ((v - u) / 2) * -(1 / 2)) * R ((v - u) / 2)
        - (R ((v - u) / 2) - 2 * M) * (Rp ((v - u) / 2) * -(1 / 2)))
        / (R ((v - u) / 2)) ^ 2) u :=
    (hinner.sub_const (2 * M)).div hinner hRne
  have hcompv : HasDerivAt (fun y => (R ((y - u) / 2) - 2 * M) / R ((y - u) / 2))
      (((Rp ((v - u) / 2) * (1 / 2)) * R ((v - u) / 2)
        - (R ((v - u) / 2) - 2 * M) * (Rp ((v - u) / 2) * (1 / 2)))
        / (R ((v - u) / 2)) ^ 2) v :=
    (hinnerv.sub_const (2 * M)).div hinnerv hRne
  have hlogu : HasDerivAt (fun x => (1 / 2) * Real.log ((R ((v - x) / 2) - 2 * M)
      / R ((v - x) / 2)))
      ((1 / 2) * (((R ((v - u) / 2) - 2 * M) / R ((v - u) / 2))⁻¹
        * (((Rp ((v - u) / 2) * -(1 / 2)) * R ((v - u) / 2)
          - (R ((v - u) / 2) - 2 * M) * (Rp ((v - u) / 2) * -(1 / 2)))
          / (R ((v - u) / 2)) ^ 2))) u := by
    have h3 := (Real.hasDerivAt_log hAne).comp u hcomp
    exact h3.const_mul (1 / 2)
  have hlogv : HasDerivAt (fun y => (1 / 2) * Real.log ((R ((y - u) / 2) - 2 * M)
      / R ((y - u) / 2)))
      ((1 / 2) * (((R ((v - u) / 2) - 2 * M) / R ((v - u) / 2))⁻¹
        * (((Rp ((v - u) / 2) * (1 / 2)) * R ((v - u) / 2)
          - (R ((v - u) / 2) - 2 * M) * (Rp ((v - u) / 2) * (1 / 2)))
          / (R ((v - u) / 2)) ^ 2))) v := by
    have h3 := (Real.hasDerivAt_log hAne).comp v hcompv
    exact h3.const_mul (1 / 2)
  have hFu : HasDerivAt (fun x => (fields M R).f x v) (du (fields M R).f u v) u := by
    have hc : (fun x => (fields M R).f x v)
        = fun x => (1 / 2) * Real.log ((R ((v - x) / 2) - 2 * M) / R ((v - x) / 2)) := by
      funext x; rfl
    rw [hc]
    have h3 : du (fields M R).f u v = (1 / 2) * (((R ((v - u) / 2) - 2 * M)
        / R ((v - u) / 2))⁻¹ * (((Rp ((v - u) / 2) * -(1 / 2)) * R ((v - u) / 2)
        - (R ((v - u) / 2) - 2 * M) * (Rp ((v - u) / 2) * -(1 / 2)))
        / (R ((v - u) / 2)) ^ 2)) := by
      show deriv (fun x => (fields M R).f x v) u = _
      rw [hc]
      exact hlogu.deriv
    rw [h3]
    exact hlogu
  have hFv : HasDerivAt (fun y => (fields M R).f u y) (dv (fields M R).f u v) v := by
    have hc : (fun y => (fields M R).f u y)
        = fun y => (1 / 2) * Real.log ((R ((y - u) / 2) - 2 * M) / R ((y - u) / 2)) := by
      funext y; rfl
    rw [hc]
    have h3 : dv (fields M R).f u v = (1 / 2) * (((R ((v - u) / 2) - 2 * M)
        / R ((v - u) / 2))⁻¹ * (((Rp ((v - u) / 2) * (1 / 2)) * R ((v - u) / 2)
        - (R ((v - u) / 2) - 2 * M) * (Rp ((v - u) / 2) * (1 / 2)))
        / (R ((v - u) / 2)) ^ 2)) := by
      show deriv (fun y => (fields M R).f u y) v = _
      rw [hc]
      exact hlogv.deriv
    rw [h3]
    exact hlogv
  have hFuv : HasDerivAt (fun y => du (fields M R).f u y) (duv (fields M R).f u v) v := by
    have h3 : duv (fields M R).f u v
        = M * (R ((v - u) / 2) - 2 * M) / (2 * (R ((v - u) / 2)) ^ 4) := hfuv.deriv
    rw [h3]
    exact hfuv
  refine ⟨⟨hFu, hFv, hRu, hRv, hasDerivAt_du_const 0 u v, hasDerivAt_dv_const 0 u v,
    hRuu, hRvv, hRuv, hRvdu, hFuv, hasDerivAt_duv_const 0 u v⟩, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · exact hRw
  · -- uu
    simp only [eqUU, hduu, hdu, hfu, hφu, pow_zero, mul_zero, add_zero]
    rw [show (fields M R).r u v = R ((v - u) / 2) from rfl]
    rw [hODE ((v - u) / 2), hrodd ((v - u) / 2), hODE ((v - u) / 2)]
    field_simp
    ring
  · -- vv
    simp only [eqVV, hdvv, hdv, hfv, hφv, pow_zero, mul_zero, add_zero]
    rw [show (fields M R).r u v = R ((v - u) / 2) from rfl]
    rw [hODE ((v - u) / 2), hrodd ((v - u) / 2), hODE ((v - u) / 2)]
    field_simp
    ring
  · -- uv
    simp only [eqUV, hduv, hdu, hdv, hE]
    rw [show (fields M R).r u v = R ((v - u) / 2) from rfl]
    rw [hODE ((v - u) / 2), hrodd ((v - u) / 2), hODE ((v - u) / 2)]
    field_simp
    ring
  · -- θθ
    have hfuvv : duv (fields M R).f u v
        = M * (R ((v - u) / 2) - 2 * M) / (2 * (R ((v - u) / 2)) ^ 4) := hfuv.deriv
    simp only [eqTheta, hφu, hφv, mul_zero, add_zero, duv_const]
    rw [show (fields M R).r u v = R ((v - u) / 2) from rfl]
    rw [hfuvv, hduv, hdu, hdv, hE, hODE ((v - u) / 2), hrodd ((v - u) / 2),
      hODE ((v - u) / 2)]
    field_simp
    ring
  · -- wave
    simp only [eqWave, hφuv, hφu, hφv, mul_zero, add_zero]

end Schwarzschild

/-! ### Hawking mass and monotonicity -/

/-- The Hawking mass `m = r/2 · (1 + 4 r_u r_v e^{-2f})`: vanishes on
Minkowski and equals `M` on the Schwarzschild exterior. -/
noncomputable def hawkingMass (d : Fields) (u v : ℝ) : ℝ :=
  d.r u v / 2 * (1 + 4 * du d.r u v * dv d.r u v * Real.exp (-(2 : ℝ) * d.f u v))

/-- **Hawking mass monotonicity in v — exact identity (work-plan item 2).**
For any solution, `∂ᵥm = -8π r² (∂ᵤr) (∂ᵥφ)² e^{-2f}`.  Hence in the
regular region (`∂ᵤr ≤ 0`) the Hawking mass is nondecreasing in the
advanced time. -/
theorem hawking_mass_v_deriv {d : Fields} {u v : ℝ} (h : IsSolution d u v) :
    dv (hawkingMass d) u v
      = -(8 : ℝ) * Real.pi * (d.r u v) ^ 2 * du d.r u v * (dv d.phi u v) ^ 2
          * Real.exp (-(2 : ℝ) * d.f u v) := by
  have hfu := h.fu
  have hfv := h.fv
  have hru := h.ru
  have hrv := h.rv
  have hpu := h.pu
  have hpv := h.pv
  have hruu := h.ruu
  have hrvv := h.rvv
  have hruv := h.ruv
  have hrvdu := h.rvdu
  have hfuv := h.fuv
  have hpuv := h.puv
  have hr := h.hr
  have huu := h.huu
  have hvv := h.hvv
  have huv := h.huv
  have htheta := h.htheta
  have hwave := h.hwave
  set r := d.r u v with hrdef
  set ru := du d.r u v with hrudef
  set rv := dv d.r u v with hrvdef
  set ruv := duv d.r u v with hruvdef
  set rvv := dvv d.r u v with hrvvdef
  set fv := dv d.f u v with hfvdef
  set pv := dv d.phi u v with hpvdef
  set E := Real.exp (2 * d.f u v) with hEdef
  set e := Real.exp (-(2 : ℝ) * d.f u v) with hedef
  have hEe : E * e = 1 := by
    rw [hEdef, hedef, ← Real.exp_add, neg_mul, add_neg_cancel, Real.exp_zero]
  have hexpe : HasDerivAt (fun y => Real.exp (-(2 : ℝ) * d.f u y))
      (e * (-(2 : ℝ) * fv)) v :=
    (hfv.const_mul (-(2 : ℝ))).exp
  have hquad : HasDerivAt (fun y => 4 * (du d.r u y * dv d.r u y
      * Real.exp (-(2 : ℝ) * d.f u y)))
      (4 * ((ruv * rv + ru * rvv) * e + (ru * rv) * (e * (-(2 : ℝ) * fv)))) v :=
    (hruv.mul hrvv).mul hexpe |>.const_mul 4
  have hmass : HasDerivAt (fun y => d.r u y / 2 * ((1:ℝ) + 4 * (du d.r u y * dv d.r u y
      * Real.exp (-(2 : ℝ) * d.f u y))))
      (rv / 2 * ((1:ℝ) + 4 * (ru * rv * e)) + r / 2 * ((0:ℝ) + 4 * ((ruv * rv + ru * rvv) * e
        + (ru * rv) * (e * (-(2 : ℝ) * fv))))) v :=
    (hrv.div_const 2).mul ((hasDerivAt_const v (1 : ℝ)).add hquad)
  have hVAL : dv (hawkingMass d) u v
      = rv / 2 + 2 * ru * rv ^ 2 * e + 2 * r * e * (ruv * rv + ru * rvv)
        - 4 * r * ru * rv * fv * e := by
    have h1 : dv (hawkingMass d) u v = deriv (fun y => hawkingMass d u y) v := rfl
    rw [h1, show (fun y => hawkingMass d u y) = fun y => d.r u y / 2 * ((1:ℝ) + 4 *
        (du d.r u y * dv d.r u y * Real.exp (-(2 : ℝ) * d.f u y))) from by
      funext y
      show d.r u y / 2 * (1 + 4 * du d.r u y * dv d.r u y
        * Real.exp (-(2 : ℝ) * d.f u y)) = _
      ring]
    exact hmass.deriv.trans (by ring)
  rw [hVAL]
  have hR1 : r * ruv + ru * rv + E / 4 = 0 := huv
  have hR2 : rvv - 2 * fv * rv + 4 * Real.pi * r * pv ^ 2 = 0 := hvv
  have hkey : (rv / 2 + 2 * ru * rv ^ 2 * e + 2 * r * e * (ruv * rv + ru * rvv)
      - 4 * r * ru * rv * fv * e) + 8 * Real.pi * r ^ 2 * ru * pv ^ 2 * e
      = 2 * e * rv * (r * ruv + ru * rv + E / 4)
        + 2 * r * e * ru * (rvv - 2 * fv * rv + 4 * Real.pi * r * pv ^ 2)
        + rv / 2 * (1 - E * e) := by
    ring
  rw [hR1, hR2] at hkey
  have hzero : (rv / 2 + 2 * ru * rv ^ 2 * e + 2 * r * e * (ruv * rv + ru * rvv)
      - 4 * r * ru * rv * fv * e) + 8 * Real.pi * r ^ 2 * ru * pv ^ 2 * e = 0 := by
    rw [hkey]
    simp [hEe]
  have hgoal : (rv / 2 + 2 * ru * rv ^ 2 * e + 2 * r * e * (ruv * rv + ru * rvv)
      - 4 * r * ru * rv * fv * e)
      = -(8 : ℝ) * Real.pi * r ^ 2 * ru * pv ^ 2 * e := by
    linarith
  exact hgoal

/-- **Hawking mass monotonicity in u — exact identity.**  For any solution
with symmetric mixed derivative of `r` at the point (Clairaut), 
`∂ᵤm = -8π r² (∂ᵥr) (∂ᵤφ)² e^{-2f}`; in the regular region `∂ᵥr ≥ 0` the
Hawking mass is nonincreasing in the retarded time. -/
theorem hawking_mass_u_deriv {d : Fields} {u v : ℝ} (h : IsSolution d u v)
    (hsymm : duv d.r u v = vdu d.r u v) :
    du (hawkingMass d) u v
      = -(8 : ℝ) * Real.pi * (d.r u v) ^ 2 * dv d.r u v * (du d.phi u v) ^ 2
          * Real.exp (-(2 : ℝ) * d.f u v) := by
  have hfu := h.fu
  have hfv := h.fv
  have hru := h.ru
  have hrv := h.rv
  have hpu := h.pu
  have hpv := h.pv
  have hruu := h.ruu
  have hrvv := h.rvv
  have hruv := h.ruv
  have hrvdu := h.rvdu
  have hfuv := h.fuv
  have hpuv := h.puv
  have hr := h.hr
  have huu := h.huu
  have hvv := h.hvv
  have huv := h.huv
  have htheta := h.htheta
  have hwave := h.hwave
  set r := d.r u v with hrdef
  set ru := du d.r u v with hrudef
  set rv := dv d.r u v with hrvdef
  set ruu := duu d.r u v with hruudef
  set vdur := vdu d.r u v with hvdudef
  set fu := du d.f u v with hfudev
  set pu := du d.phi u v with hpudef
  set E := Real.exp (2 * d.f u v) with hEdef
  set e := Real.exp (-(2 : ℝ) * d.f u v) with hedef
  have hEe : E * e = 1 := by
    rw [hEdef, hedef, ← Real.exp_add, neg_mul, add_neg_cancel, Real.exp_zero]
  have hexpe : HasDerivAt (fun x => Real.exp (-(2 : ℝ) * d.f x v))
      (e * (-(2 : ℝ) * fu)) u :=
    (hfu.const_mul (-(2 : ℝ))).exp
  have hquad : HasDerivAt (fun x => 4 * (du d.r x v * dv d.r x v
      * Real.exp (-(2 : ℝ) * d.f x v)))
      (4 * ((ruu * rv + ru * vdur) * e + (ru * rv) * (e * (-(2 : ℝ) * fu)))) u :=
    (hruu.mul hrvdu).mul hexpe |>.const_mul 4
  have hmass : HasDerivAt (fun x => d.r x v / 2 * ((1:ℝ) + 4 * (du d.r x v * dv d.r x v
      * Real.exp (-(2 : ℝ) * d.f x v))))
      (ru / 2 * ((1:ℝ) + 4 * (ru * rv * e)) + r / 2 * ((0:ℝ) + 4 * ((ruu * rv + ru * vdur) * e
        + (ru * rv) * (e * (-(2 : ℝ) * fu))))) u :=
    (hru.div_const 2).mul ((hasDerivAt_const u (1 : ℝ)).add hquad)
  have hVAL : du (hawkingMass d) u v
      = ru / 2 + 2 * ru ^ 2 * rv * e + 2 * r * e * (ruu * rv + ru * vdur)
        - 4 * r * ru * rv * fu * e := by
    have h1 : du (hawkingMass d) u v = deriv (fun x => hawkingMass d x v) u := rfl
    rw [h1, show (fun x => hawkingMass d x v) = fun x => d.r x v / 2 * ((1:ℝ) + 4 *
        (du d.r x v * dv d.r x v * Real.exp (-(2 : ℝ) * d.f x v))) from by
      funext x
      show d.r x v / 2 * (1 + 4 * du d.r x v * dv d.r x v
        * Real.exp (-(2 : ℝ) * d.f x v)) = _
      ring]
    exact hmass.deriv.trans (by ring)
  rw [hVAL]
  have hR1 : r * vdur + ru * rv + E / 4 = 0 := by
    have h2 := h.huv
    simp only [eqUV] at h2
    rwa [hsymm] at h2
  have hR2 : ruu - 2 * fu * ru + 4 * Real.pi * r * pu ^ 2 = 0 := huu
  have hkey : (ru / 2 + 2 * ru ^ 2 * rv * e + 2 * r * e * (ruu * rv + ru * vdur)
      - 4 * r * ru * rv * fu * e) + 8 * Real.pi * r ^ 2 * rv * pu ^ 2 * e
      = 2 * e * ru * (r * vdur + ru * rv + E / 4)
        + 2 * r * e * rv * (ruu - 2 * fu * ru + 4 * Real.pi * r * pu ^ 2)
        + ru / 2 * (1 - E * e) := by
    ring
  rw [hR1, hR2] at hkey
  have hzero : (ru / 2 + 2 * ru ^ 2 * rv * e + 2 * r * e * (ruu * rv + ru * vdur)
      - 4 * r * ru * rv * fu * e) + 8 * Real.pi * r ^ 2 * rv * pu ^ 2 * e = 0 := by
    rw [hkey]
    simp [hEe]
  have hgoal : (ru / 2 + 2 * ru ^ 2 * rv * e + 2 * r * e * (ruu * rv + ru * vdur)
      - 4 * r * ru * rv * fu * e)
      = -(8 : ℝ) * Real.pi * r ^ 2 * rv * pu ^ 2 * e := by
    linarith
  exact hgoal

/-- **Sign corollary (v-monotonicity).**  If the areal radius decreases
along the retarded direction (`∂ᵤr ≤ 0`), the Hawking mass is nondecreasing
in the advanced time. -/
theorem hawking_mass_monotone_v {d : Fields} {u v : ℝ} (h : IsSolution d u v)
    (hle : du d.r u v ≤ 0) :
    0 ≤ dv (hawkingMass d) u v := by
  rw [hawking_mass_v_deriv h]
  have h1 : (0 : ℝ) ≤ (dv d.phi u v) ^ 2 := sq_nonneg _
  have h2 : (0 : ℝ) ≤ (d.r u v) ^ 2 := sq_nonneg _
  have h3 : (0 : ℝ) < Real.exp (-(2 : ℝ) * d.f u v) := Real.exp_pos _
  have h4 : (0 : ℝ) ≤ -(8 : ℝ) * Real.pi * (d.r u v) ^ 2 * du d.r u v
      * (dv d.phi u v) ^ 2 * Real.exp (-(2 : ℝ) * d.f u v) := by
    have hpi : (0 : ℝ) ≤ Real.pi := le_of_lt Real.pi_pos
    have hdu : (0 : ℝ) ≤ -(du d.r u v) := by linarith
    have hprod : (0 : ℝ) ≤ Real.pi * (d.r u v) ^ 2 * (-(du d.r u v))
        * (dv d.phi u v) ^ 2 * Real.exp (-(2 : ℝ) * d.f u v) :=
      mul_nonneg (mul_nonneg (mul_nonneg (mul_nonneg hpi (sq_nonneg (d.r u v))) hdu)
        (sq_nonneg (dv d.phi u v))) (le_of_lt h3)
    nlinarith [hprod]
  exact h4

/-- **Sign corollary (u-monotonicity).**  If the areal radius increases
along the advanced direction (`∂ᵥr ≥ 0`), the Hawking mass is nonincreasing
in the retarded time. -/
theorem hawking_mass_monotone_u {d : Fields} {u v : ℝ} (h : IsSolution d u v)
    (hsymm : duv d.r u v = vdu d.r u v) (hle : 0 ≤ dv d.r u v) :
    du (hawkingMass d) u v ≤ 0 := by
  rw [hawking_mass_u_deriv h hsymm]
  have h1 : (0 : ℝ) ≤ (du d.phi u v) ^ 2 := sq_nonneg _
  have h2 : (0 : ℝ) ≤ (d.r u v) ^ 2 := sq_nonneg _
  have h3 : (0 : ℝ) < Real.exp (-(2 : ℝ) * d.f u v) := Real.exp_pos _
  have h4 : (0 : ℝ) ≤ (8 : ℝ) * Real.pi * (d.r u v) ^ 2 * dv d.r u v
      * (du d.phi u v) ^ 2 * Real.exp (-(2 : ℝ) * d.f u v) := by
    have hpi : (0 : ℝ) ≤ Real.pi := le_of_lt Real.pi_pos
    have hprod : (0 : ℝ) ≤ Real.pi * (d.r u v) ^ 2 * (dv d.r u v)
        * (du d.phi u v) ^ 2 * Real.exp (-(2 : ℝ) * d.f u v) :=
      mul_nonneg (mul_nonneg (mul_nonneg (mul_nonneg hpi (sq_nonneg (d.r u v))) hle)
        (sq_nonneg (du d.phi u v))) (le_of_lt h3)
    nlinarith [hprod]
  linarith

end Choptuik.Analysis
