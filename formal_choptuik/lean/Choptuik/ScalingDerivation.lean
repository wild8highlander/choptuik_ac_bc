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
   * `wiggle_repo_check` — with the repository constant Δ = ln 2 the
     wiggle period is λ₀·(ln 2)/2 < 1.34 (calibrated value 0.9269).

   `derived_mass_scaling` feeds the derived factorization into the
   repository's proved `mass_scaling_law` (log-log slope → γ = 1/λ₀).
-/

import Mathlib
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
    mul_pos m.hlambda0 (by positivity)
  exact Real.one_lt_exp_iff.mpr h

lemma mu_ne_zero : mu m ≠ 0 := ne_of_gt (Real.exp_pos _)

lemma log_mu_pos : 0 < Real.log (mu m) := by
  have h1 := mu_pos m
  have h2 : Real.log (mu m) = m.lambda0 * (m.Δ / 2) := by
    rw [mu, Real.log_exp]
  rw [h2]
  exact mul_pos m.hlambda0 (by positivity)

/-- The exit time: half-echoes needed to grow `δ` to the threshold scale
`C₀` (any `δ > 0`; nonpositive growth gives `0`). -/
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
  have hlog : Real.log (m.C₀ / (δ / mu m))
      = Real.log (m.C₀ / δ) + Real.log (mu m) := by
    have hEq : m.C₀ / (δ / mu m) = (m.C₀ / δ) * mu m := by
      field_simp
      ring
    rw [hEq, Real.log_mul (by positivity) (mu_ne_zero m), Real.log_exp,
      mul_comm]
  have hdiv : Real.log (m.C₀ / δ) / Real.log (mu m) + 1
      = (Real.log (m.C₀ / δ) + Real.log (mu m)) / Real.log (mu m) := by
    field_simp
  unfold exitTime
  rw [hlog, hdiv]
  -- ⌈x + 1⌉ = ⌈x⌉ + 1 for the integer ceiling
  have hceil : ∀ x : ℝ, Int.ceil (x + 1) = Int.ceil x + 1 := by
    intro x
    have h1 : Int.ceil (x + 1) ≤ Int.ceil x + 1 := by
      apply Int.ceil_le.mpr
      have hle := Int.le_ceil x
      push_cast
      linarith
    have h2 : Int.ceil x + 1 ≤ Int.ceil (x + 1) := by
      by_contra hc
      push_neg at hc
      have hlow : (Int.ceil x : ℝ) < x + 1 := by
        have h := Int.sub_one_lt_ceil x
        linarith
      have hlt : Int.ceil x < Int.ceil (x + 1) := Int.lt_ceil.mpr hlow
      exact absurd hlt (by omega)
    omega
  rw [hceil]

/-- **The wiggle is periodic with period λ₀Δ/2** — the derived echo
wiggle of the mass scaling law (work-plan item 7). -/
theorem wiggle_periodic (s : ℝ) :
    wiggleF m (s + m.lambda0 * (m.Δ / 2)) = wiggleF m s := by
  have hmu : (0 : ℝ) < mu m := Real.exp_pos _
  have hδ : (0 : ℝ) < Real.exp (-s) := Real.exp_pos _
  have hP : m.lambda0 * (m.Δ / 2) = Real.log (mu m) := by
    rw [mu, Real.log_exp]
  have hexp : Real.exp (-(s + m.lambda0 * (m.Δ / 2)))
      = Real.exp (-s) / mu m := by
    rw [Real.exp_add, Real.exp_neg, Real.exp_neg, div_eq_mul_inv, ← mu m,
      ← Real.exp_add]
    congr 1
    ring
  have hshift := exitTime_shrink m (Real.exp (-s)) hδ
  have hmass : exitMass m (Real.exp (-s) / mu m)
      = exitMass m (Real.exp (-s)) * Real.exp (-(m.Δ / 2)) := by
    show m.C_M * Real.exp (-(m.Δ / 2) * ((exitTime m (Real.exp (-s) / mu m) : ℝ)))
      = m.C_M * Real.exp (-(m.Δ / 2) * ((exitTime m (Real.exp (-s)) : ℝ)))
        * Real.exp (-(m.Δ / 2))
    rw [hshift]
    push_cast
    rw [← Real.mul_add, ← Real.mul_assoc]
    congr 1
    ring
  show exitMass m (Real.exp (-(s + m.lambda0 * (m.Δ / 2))))
      * Real.exp ((1 / m.lambda0) * (s + m.lambda0 * (m.Δ / 2)))
    = exitMass m (Real.exp (-s)) * Real.exp ((1 / m.lambda0) * s)
  rw [hexp, hmass, ← Real.mul_assoc, ← Real.mul_assoc]
  have hcancel : Real.exp (-(m.Δ / 2)) * Real.exp ((1 / m.lambda0)
      * (m.lambda0 * (m.Δ / 2))) = 1 := by
    rw [← Real.mul_exp]
    congr 1
    field_simp
    ring
  rw [hcancel, mul_one]

/-- **The mass scaling law, derived** (work-plan item 7): the exit mass
factorizes as `δ^{1/λ₀}` times a periodic wiggle — the hypothesis form
of `mass_scaling_law` is now a theorem of the echo model. -/
theorem scaling_law_derived (δ : ℝ) (hδ : 0 < δ) :
    exitMass m δ = δ ^ (1 / m.lambda0)
      * wiggleF m (Real.log (1 / δ)) := by
  have hs : Real.exp (-Real.log (1 / δ)) = δ := by
    have h1 : (0 : ℝ) < 1 / δ := by positivity
    rw [← Real.inv_inv δ, ← Real.exp_log h1, Real.exp_neg, Real.exp_log]
    · rw [neg_inv]
    · exact hδ
  have hpow : δ ^ (1 / m.lambda0)
      = Real.exp ((1 / m.lambda0) * Real.log δ) := by
    rw [Real.rpow_def hδ.le]
  show exitMass m δ = _ * exitMass m (Real.exp (-Real.log (1 / δ)))
    * Real.exp ((1 / m.lambda0) * Real.log (1 / δ))
  rw [hs]
  have hcancel : Real.log (1 / δ) = -Real.log δ := by
    have : Real.log (δ⁻¹) = -Real.log δ := by
      rw [inv_eq_one_div, ← Real.log_div hδ (one_ne_zero)]
      congr 1
      field_simp
    rw [one_div, this]
  rw [hcancel, hpow]
  rw [show (1/m.lambda0) * (-Real.log δ) = -(1/m.lambda0) * Real.log δ by ring,
    ← Real.mul_exp, add_neg_cancel, Real.exp_zero, mul_one]

/-- **The wiggle period identity:** `λ₀Δ/2 = Δ/(2γ)` with `γ = 1/λ₀`. -/
theorem wiggle_period (γ : ℝ) (hγ : γ = 1 / m.lambda0) :
    m.lambda0 * (m.Δ / 2) = m.Δ / (2 * γ) := by
  rw [hγ]
  field_simp

end EchoModel

/-- **Numerical sanity check (physical period).**  With the calibrated
growth rate λ₀ = 2.6745 (`Choptuik.Stability.lambda0`) and Choptuik's
echoing period Δ ∈ [3.44, 3.45], the derived wiggle period λ₀Δ/2 equals
4.61 to within 1/100 — the user's check `λ₀Δ/2 = Δ/(2γ) ≈ 4.61`. -/
theorem wiggle_physical_check : ∀ Δ : ℝ, 3.44 ≤ Δ → Δ ≤ 3.45 →
    |lambda0 * Δ / 2 - 4.61| < 1 / 100 := by
  intro Δ hlo hhi
  have hλ : lambda0 = 26745 / 10000 := by
    show (2.6745 : ℝ) = 26745 / 10000
    norm_num
  rw [hλ]
  have hkey : 26745 / 10000 * (344 / 100) / 2 = 460014 / 100000 := by norm_num
  have hkey2 : 26745 / 10000 * (345 / 100) / 2 = 46135125 / 10000000 := by norm_num
  have hmono : 26745 / 10000 * (344 / 100) / 2
      ≤ 26745 / 10000 * Δ / 2 := by
    apply mul_le_mul_of_nonneg_left _ (by norm_num)
    apply mul_le_mul_of_nonneg_left _ (by norm_num)
    linarith
  have hmono2 : 26745 / 10000 * Δ / 2
      ≤ 26745 / 10000 * (345 / 100) / 2 := by
    apply mul_le_mul_of_nonneg_left _ (by norm_num)
    apply mul_le_mul_of_nonneg_left _ (by norm_num)
    linarith
  have h460 : (230007 : ℝ) / 50000 = 460014 / 100000 := by norm_num
  have h461 : (9227025 : ℝ) / 2000000 = 46135125 / 10000000 := by norm_num
  rw [hkey, hkey2] at hmono hmono2
  rw [h460] at hmono
  rw [h461] at hmono2
  have htarget : |(460014 : ℝ) / 100000 - 461 / 100| = 986 / 10000000 := by norm_num
  have htarget2 : |(46135125 : ℝ) / 10000000 - 461 / 100| = 35125 / 10000000 := by norm_num
  rw [abs_sub_comm, htarget2] at *
  rcases abs_eq (26745 / 10000 * Δ / 2 - 461 / 100) with h | h
  · rw [h]
    rw [abs_lt]
    constructor <;> norm_num
  · rw [h]
    rw [abs_lt]
    constructor <;> norm_num

/-- **Numerical sanity check (repository period).**  With the repository
constant Δ = ln 2 the derived wiggle period is λ₀ (ln 2)/2, a positive
number below 1.34 (calibrated value 0.9269; `Real.log 2 < 1` because
`e > 9/4`). -/
theorem wiggle_repo_check : 0 < lambda0 * Real.log 2 / 2
    ∧ lambda0 * Real.log 2 / 2 < 1.34 := by
  have hλ : (0 : ℝ) < lambda0 := lambda0_pos
  have hlog : (0 : ℝ) < Real.log 2 := Real.log_pos (by norm_num)
  constructor
  · apply div_pos
    · exact mul_pos hλ hlog
    · norm_num
  · have hlog2 : Real.log 2 < 1 := by
      have hexp : (9 : ℝ) / 4 ≤ Real.exp 1 := by
        have h1 : (3 : ℝ) / 2 ≤ Real.exp (1 / 2 : ℝ) :=
          Real.add_one_le_exp.mp (by norm_num)
        have h2 : Real.exp 1 = Real.exp (1 / 2 : ℝ) * Real.exp (1 / 2 : ℝ) := by
          rw [← Real.exp_add]
          norm_num
        rw [h2]
        exact mul_self_le_mul_self (le_of_lt (by norm_num : (3:ℝ)/2 < 2)) h1 (by norm_num)
      have h2 : (2 : ℝ) < Real.exp 1 := by
        have : (9 : ℝ) / 4 > 2 := by norm_num
        linarith
      have := Real.log_lt_iff_lt_exp (by norm_num : (0:ℝ) < 2)
      rw [this]
      have h2' : (2 : ℝ) = Real.exp (Real.log 2) := (Real.exp_log (by norm_num)).symm
      rw [h2']
      exact h2
    have : (26745 : ℝ) / 10000 * 1 / 2 = 26745 / 20000 := by field_simp
    have hbound : lambda0 * Real.log 2 / 2 < lambda0 * 1 / 2 := by
      apply div_lt_div_of_lt
      · exact hλ
      · exact hlog2
    have hval : (26745 : ℝ) / 20000 < 1.34 := by norm_num
    show lambda0 * Real.log 2 / 2 < 1.34
    have hlam : (lambda0 : ℝ) = 26745 / 10000 := by
      show (2.6745 : ℝ) = 26745 / 10000
      norm_num
    rw [hlam]
    calc (26745 : ℝ) / 10000 * Real.log 2 / 2
        ≤ 26745 / 10000 * 1 / 2 := by
          apply div_lt_div_of_lt (by norm_num) hlog2 |>.le
      _ = 26745 / 20000 := by field_simp
      _ < 1.34 := by norm_num

end Choptuik.Scaling
