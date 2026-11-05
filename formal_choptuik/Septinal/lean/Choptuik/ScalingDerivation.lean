/-
   F O R M A L   C H O P T U I K   ·   Choptuik/ScalingDerivation.lean

   Work-plan item 7: DERIVATION of the mass scaling law instead of the
   hypothesis form `M = C δ^γ F(·)`.

   Dynamical model (Poincaré map of the DSS echo): around the critical
   orbit, one half-echo (advance Δ/2, the half-period symmetry of the
   scalar echo) multiplies the deviation by
       μ = e^{λ₀ Δ/2}                      (single growing multiplier),
   while the mass scale shrinks by e^{-Δ/2}.  The exit time n(δ) — the
   number of half-echoes needed to grow the initial distance-to-threshold
   δ to order C₀ — then produces BOTH exponents of the observed law:

   * mass scaling     M(δ) = δ^{1/λ₀} · F(log(1/δ)),  γ = 1/λ₀;
   * wiggle period    λ₀Δ/2 = Δ/(2γ)  (period of F in log(1/δ)).

   Numerical sanity checks (exact rational arithmetic):
   * `wiggle_physical_check` — with the calibrated λ₀ = 2.6745 and
     Choptuik's period Δ ∈ [3.44, 3.45], the wiggle period is 4.61 to
     within 1/100 (the user's check ≈ 4.61);
   * `wiggle_published_check` — with the published echoing period
     Δ = 3.445452402 (Martín-García & Gundlach 2003) the wiggle period
     λ₀Δ/2 = 4.6074… is 4.61 to within 1/100.  (The check is computed
     against the published value fixed in Spectrum/Scaling, never
     against a CSV stub.)

   `scaling_law_derived` realizes the hypothesis form of the repository's
   `mass_scaling_law` (log-log slope → γ = 1/λ₀) as a theorem of the
   echo model.

   Lean landmines handled here: `λ` inside identifiers (`hλ`) collides
   with the `fun` keyword, `Real.mul_add` / `Real.mul_exp` do not exist,
   and several naive `rw` chains do not match.  All identifiers use
   ASCII (`hlam`), the ceiling shift uses `Int.ceil_add_one`, and
   the exponent bookkeeping uses `Real.exp_add` / `Real.exp_neg`.
-/

import Mathlib.Tactic
import Mathlib.Analysis.SpecialFunctions.Exp
import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Algebra.Order.Floor.Ring
import Choptuik.Stability.Spectrum

namespace Choptuik.Scaling

open Choptuik.Stability Filter

/-! ### The echo model -/

/-- The Poincaré/echo model: growth rate `lambda0`, echoing period `Δ`,
threshold scale `C₀`, mass scale `C_M` (all positive). -/
structure EchoModel where
  /-- growth rate of the single unstable mode -/
  lambda0 : ℝ
  hlambda0 : 0 < lambda0
  /-- echoing period -/
  Δ : ℝ
  hΔ : 0 < Δ
  /-- data scale of the exit criterion -/
  C₀ : ℝ
  hC₀ : 0 < C₀
  /-- mass scale -/
  C_M : ℝ
  hC_M : 0 < C_M

namespace EchoModel

variable (m : EchoModel)

/-- The half-echo advance (the half-period symmetry of the scalar echo). -/
noncomputable def half : ℝ := m.Δ / 2

/-- The single growing multiplier per half-echo. -/
noncomputable def mu : ℝ := Real.exp (m.lambda0 * (m.Δ / 2))

lemma mu_pos : 1 < mu m := by
  have h : (0 : ℝ) < m.lambda0 * (m.Δ / 2) :=
    mul_pos m.hlambda0 (div_pos m.hΔ (by norm_num))
  exact Real.one_lt_exp_iff.mpr h

lemma mu_ne_zero : mu m ≠ 0 := ne_of_gt (Real.exp_pos _)

lemma log_mu_eq : Real.log (mu m) = m.lambda0 * (m.Δ / 2) := by
  show Real.log (Real.exp _) = _
  rw [Real.log_exp]

lemma log_mu_pos : 0 < Real.log (mu m) := by
  rw [log_mu_eq m]
  exact mul_pos m.hlambda0 (div_pos m.hΔ (by norm_num))

/-- The exit time: half-echoes needed to grow `δ` to the threshold scale
`C₀` (any `δ > 0`). -/
noncomputable def exitTime (δ : ℝ) : ℤ :=
  Int.ceil (Real.log (m.C₀ / δ) / Real.log (mu m))

/-- The mass at exit: after `n` half-echoes the mass scale is
`C_M e^{-(Δ/2) n}`. -/
noncomputable def exitMass (δ : ℝ) : ℝ :=
  m.C_M * Real.exp (-(m.Δ / 2) * (exitTime m δ : ℝ))

/-- The wiggle: the normalized mass as a function of `s = log(1/δ)`. -/
noncomputable def wiggleF (s : ℝ) : ℝ :=
  exitMass m (Real.exp (-s)) * Real.exp ((1 / m.lambda0) * s)

/-- The exit time grows by exactly one when δ shrinks by one multiplier. -/
lemma exitTime_shrink (δ : ℝ) (hδ : 0 < δ) :
    exitTime m (δ / mu m) = exitTime m δ + 1 := by
  have hmu : (0 : ℝ) < mu m := Real.exp_pos _
  have hpos : (0 : ℝ) < m.C₀ / δ := div_pos m.hC₀ hδ
  have hpos' : (0 : ℝ) < m.C₀ / (δ / mu m) := by
    apply div_pos m.hC₀
    exact div_pos hδ hmu
  have hEq : m.C₀ / (δ / mu m) = (m.C₀ / δ) * mu m := by
    field_simp
  have hlog : Real.log (m.C₀ / (δ / mu m))
      = Real.log (m.C₀ / δ) + Real.log (mu m) := by
    rw [hEq, Real.log_mul (by linarith) (mu_ne_zero m)]
  have hne : Real.log (mu m) ≠ 0 := ne_of_gt (log_mu_pos m)
  have hdiv : Real.log (m.C₀ / δ) / Real.log (mu m) + 1
      = (Real.log (m.C₀ / δ) + Real.log (mu m)) / Real.log (mu m) := by
    field_simp
  unfold exitTime
  rw [hlog, ← hdiv, Int.ceil_add_one]

/-- **The wiggle is periodic with period λ₀Δ/2** — the derived echo
wiggle of the mass scaling law (work-plan item 7). -/
theorem wiggle_periodic (s : ℝ) :
    wiggleF m (s + m.lambda0 * (m.Δ / 2)) = wiggleF m s := by
  have hδpos : (0 : ℝ) < Real.exp (-s) := Real.exp_pos _
  have hshift := exitTime_shrink m (Real.exp (-s)) hδpos
  have hmuEq := log_mu_eq m
  have hexp : Real.exp (-(s + m.lambda0 * (m.Δ / 2)))
      = Real.exp (-s) / mu m := by
    have hneg : Real.exp (-(m.lambda0 * (m.Δ / 2))) = (mu m)⁻¹ := by
      show Real.exp (-(m.lambda0 * (m.Δ / 2))) = (Real.exp _)⁻¹
      rw [Real.exp_neg]
    rw [neg_add, Real.exp_add, hneg, inv_eq_one_div]
    ring
  have hsplit : (1 / m.lambda0) * (s + m.lambda0 * (m.Δ / 2))
      = (1 / m.lambda0) * s + m.Δ / 2 := by
    rw [one_div, mul_add, ← mul_assoc,
      inv_mul_cancel₀ (ne_of_gt m.hlambda0), one_mul]
  have hpair : Real.exp (-(m.Δ / 2)) * Real.exp (m.Δ / 2) = 1 := by
    rw [← Real.exp_add, neg_add_cancel, Real.exp_zero]
  show m.C_M
      * Real.exp (-(m.Δ / 2)
        * ((exitTime m (Real.exp (-(s + m.lambda0 * (m.Δ / 2))) : ℝ))))
      * Real.exp ((1 / m.lambda0) * (s + m.lambda0 * (m.Δ / 2)))
    = m.C_M
      * Real.exp (-(m.Δ / 2) * ((exitTime m (Real.exp (-s)) : ℝ)))
      * Real.exp ((1 / m.lambda0) * s)
  rw [hexp, hshift]
  push_cast
  rw [hsplit, mul_add, mul_one, Real.exp_add, Real.exp_add]
  rw [mul_assoc m.C_M (Real.exp (-(m.Δ / 2) * ↑(m.exitTime (Real.exp (-s))))
        * Real.exp (-(m.Δ / 2)))
      (Real.exp ((1 / m.lambda0) * s) * Real.exp (m.Δ / 2))]
  rw [mul_assoc (Real.exp (-(m.Δ / 2) * ↑(m.exitTime (Real.exp (-s)))))
      (Real.exp (-(m.Δ / 2))) (Real.exp ((1 / m.lambda0) * s) * Real.exp (m.Δ / 2))]
  rw [mul_left_comm (Real.exp (-(m.Δ / 2))) (Real.exp ((1 / m.lambda0) * s))
      (Real.exp (m.Δ / 2)), hpair, mul_one, ← mul_assoc]

/-- **The mass scaling law, derived** (work-plan item 7): the exit mass
factorizes as `δ^{1/λ₀}` times a periodic wiggle — the hypothesis form
of `mass_scaling_law` is now a theorem of the echo model. -/
theorem scaling_law_derived (δ : ℝ) (hδ : 0 < δ) :
    exitMass m δ = δ ^ (1 / m.lambda0)
      * wiggleF m (Real.log (1 / δ)) := by
  have hs : Real.exp (-Real.log (1 / δ)) = δ := by
    rw [one_div δ, Real.log_inv, neg_neg, Real.exp_log hδ]
  have hpow : δ ^ (1 / m.lambda0)
      = Real.exp ((1 / m.lambda0) * Real.log δ) := by
    rw [Real.rpow_def_of_pos hδ, mul_comm]
  have hpowne : δ ^ (1 / m.lambda0) ≠ 0 := by
    rw [hpow]
    exact Real.exp_ne_zero _
  have hE : Real.exp ((1 / m.lambda0) * (-Real.log δ))
      = (δ ^ (1 / m.lambda0))⁻¹ := by
    rw [mul_neg, Real.exp_neg, ← hpow]
  show exitMass m δ = δ ^ (1 / m.lambda0)
    * (exitMass m (Real.exp (-Real.log (1 / δ)))
      * Real.exp ((1 / m.lambda0) * Real.log (1 / δ)))
  rw [hs, one_div δ, Real.log_inv, hE, ← mul_assoc,
    mul_comm (δ ^ (1 / m.lambda0)) (exitMass m δ)]
  exact (mul_inv_cancel_right₀ hpowne (exitMass m δ)).symm

/-- **The wiggle period identity:** `λ₀Δ/2 = Δ/(2γ)` with `γ = 1/λ₀`. -/
theorem wiggle_period (γ : ℝ) (hγ : γ = 1 / m.lambda0) :
    m.lambda0 * (m.Δ / 2) = m.Δ / (2 * γ) := by
  rw [hγ]
  field_simp
  ring

end EchoModel

/-- **Numerical sanity check (physical period).**  With the calibrated
growth rate λ₀ = 2.6745 (`Choptuik.Stability.lambda0`) and Choptuik's
echoing period Δ ∈ [3.44, 3.45], the derived wiggle period λ₀Δ/2 equals
4.61 to within 1/100 — the user's check `λ₀Δ/2 = Δ/(2γ) ≈ 4.61`. -/
theorem wiggle_physical_check : ∀ Δ : ℝ, 3.44 ≤ Δ → Δ ≤ 3.45 →
    |lambda0 * Δ / 2 - 4.61| < 1 / 100 := by
  intro Δ hlo hhi
  have hlam : lambda0 = 26745 / 10000 := by
    show (2.6745 : ℝ) = 26745 / 10000
    norm_num
  rw [hlam]
  have hk1 : (26745 / 10000 : ℝ) * 3.44 = 920028 / 100000 := by norm_num
  have hk2 : (26745 / 10000 : ℝ) * 3.45 = 9227025 / 1000000 := by norm_num
  have h1 : (26745 / 10000 : ℝ) * Δ ≥ (26745 / 10000 : ℝ) * 3.44 :=
    mul_le_mul_of_nonneg_left hlo (by norm_num)
  have h2 : (26745 / 10000 : ℝ) * Δ ≤ (26745 / 10000 : ℝ) * 3.45 :=
    mul_le_mul_of_nonneg_left hhi (by norm_num)
  rw [hk1] at h1
  rw [hk2] at h2
  rw [abs_lt]
  constructor <;> linarith

/-- **Numerical sanity check (published period).**  With the calibrated
growth rate λ₀ = 2.6745 (`Choptuik.Stability.lambda0`) and the published
echoing period Δ = 3.445452402 (`echoingPeriod`; Martín-García &
Gundlach 2003), the derived wiggle period λ₀Δ/2 = 4.6074… equals 4.61
to within 1/100 — the user's check `λ₀Δ/2 = Δ/(2γ) ≈ 4.61`.  The
check is computed against the published period, never against a
CSV-header stub. -/
theorem wiggle_published_check :
    |lambda0 * echoingPeriod / 2 - 4.61| < 1 / 100 := by
  have hlo : (3.44 : ℝ) ≤ echoingPeriod := by
    have h := echoingPeriod_gundlach1997
    rw [abs_lt] at h
    linarith
  have hhi : echoingPeriod ≤ 3.45 := by
    have h := echoingPeriod_gundlach1997
    rw [abs_lt] at h
    linarith
  exact wiggle_physical_check echoingPeriod hlo hhi

end Choptuik.Scaling
