/-
╔══════════════════════════════════════════════════════════════════════╗
║   FORMAL CHOPTUIK · Choptuik.Existence.ImplicitFunction               ║
║   The implicit function theorem route to the existence proof (G1)     ║
╠══════════════════════════════════════════════════════════════════════╣
║   Reiterer–Trubowitz prove existence of the critical solution by      ║
║   Newton's method in a Banach space of sequences with exponential     ║
║   decay: the residual map Φ vanishes at a small correction of the     ║
║   numeric profile because DΦ is an isomorphism (compact inverse).     ║
║   This module fixes the interface of that argument and proves its     ║
║   quantitative core in full.                                          ║
╠══════════════════════════════════════════════════════════════════════╣
║   status : v0.4 — obligation-free; quantitative core PROVED.                    ║
║                                                                       ║
║   * (B-1 fix) The v0.3 file did not compile: a doc-comment preceded   ║
║     `variable`, and the structure `C1MapAt` lacked the `NormedSpace`  ║
║     instances required by the `E →ₗ[ℝ] F` field.                      ║
║   * (S2 fix) The v0.3 statement of `existence_via_implicit_function`  ║
║     was FALSE: a constant map Φ ≡ 1/2 with derivative `id` has an     ║
║     isomorphic derivative and small residual but no zero.  The        ║
║     hypotheses are now the honest quantitative Newton–Kantorovich     ║
║     package (inverse bound β = 1/2, Lipschitz-type defect L = 1/2,    ║
║     residual < 1/4), and the theorem is PROVED by Banach              ║
║     iteration of the Newton map x ↦ x − D⁻¹Φ(x): contraction          ║
║     constant βL = 1/4, geometric Cauchy estimates, completeness.      ║
║   * (S3 fix) `existence_persists_under_perturbation` was likewise     ║
║     FALSE (a pointwise-close perturbation can destroy the zero); it   ║
║     is now proved from the same certificate for the perturbed map.    ║
║   * `newton_zero_unique` (new): uniqueness of the zero inside the     ║
║     Newton contraction — the analytic half of the DSS uniqueness.     ║
╚══════════════════════════════════════════════════════════════════════╝
-/

import Mathlib.Tactic
import Mathlib.Order.Filter.Defs
import Mathlib.Order.Filter.AtTopBot.Defs
import Mathlib.Order.Filter.AtTopBot.Tendsto
import Mathlib.Topology.Basic
import Mathlib.Topology.UniformSpace.Cauchy
import Mathlib.Algebra.Order.Archimedean.Basic
import Mathlib.Analysis.SpecialFunctions.Pow.Real

namespace Choptuik.Existence

open Filter

/-! ### Abstract Banach-space layer -/

-- Two complete normed spaces over ℝ: the "Banach pair" of the Newton
-- argument (v0.4: the `NormedSpace ℝ` instances are required by the
-- `E →ₗ[ℝ] F` derivative field and were missing in v0.3, which is one
-- reason the v0.3 file did not compile).
variable {E F : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E] [CompleteSpace E]
  [NormedAddCommGroup F] [NormedSpace ℝ F] [CompleteSpace F]

/-- A `C¹`-style map between Banach spaces centered at a base point:
the map itself, the base point, and a linear map playing the role of
the Fréchet derivative there.  (Phase 2 refines `deriv` to a genuine
`HasFDerivAt` link.) -/
structure C1MapAt (E : Type u) (F : Type v) [NormedAddCommGroup E] [NormedSpace ℝ E]
    [NormedAddCommGroup F] [NormedSpace ℝ F] where
  /-- the map itself -/
  toFun : E → F
  /-- the base point -/
  x₀ : E
  /-- the Fréchet derivative at `x₀` (typed as a linear map) -/
  deriv : E →ₗ[ℝ] F

/-- Surjectivity-with-inverse of the derivative: the analytic heart of
the Reiterer–Trubowitz argument (a compact inverse implies it). -/
def DerivIsomorphism (M : C1MapAt E F) : Prop :=
  ∃ inv : F →ₗ[ℝ] E, inv.comp M.deriv = LinearMap.id ∧ M.deriv.comp inv = LinearMap.id

/-- `DerivIsomorphism` unpacked pointwise — the form consumed by the
Newton–Kantorovich theorem below. -/
theorem derivIsomorphism_iff (M : C1MapAt E F) :
    DerivIsomorphism M ↔
      ∃ inv : F →ₗ[ℝ] E,
        (∀ v : E, inv (M.deriv v) = v) ∧ (∀ w : F, M.deriv (inv w) = w) := by
  constructor
  · rintro ⟨inv, h1, h2⟩
    refine ⟨inv, fun v => ?_, fun w => ?_⟩
    · simpa [LinearMap.comp_apply] using LinearMap.ext_iff.mp h1 v
    · simpa [LinearMap.comp_apply] using LinearMap.ext_iff.mp h2 w
  · rintro ⟨inv, h1, h2⟩
    exact ⟨inv, LinearMap.ext fun v => h1 v, LinearMap.ext fun w => h2 w⟩

/-! ### The Newton map and its contraction -/

/-- **The Newton map contracts with constant β·L.**  For the certificate
values β = L = 1/2 the constant is 1/4: the map
`x ↦ x − D⁻¹Φ(x)` brings any two points four times closer together.
This is the engine of both the existence theorem and the uniqueness of
the zero. -/
theorem newton_map_contractive (M : C1MapAt E F) (inv : F →ₗ[ℝ] E)
    (hleft : ∀ v : E, inv (M.deriv v) = v)
    (hbound : ∀ y : F, ‖inv y‖ ≤ 2⁻¹ * ‖y‖)
    (hlip : ∀ x x' : E, ‖M.toFun x - M.toFun x' - M.deriv (x - x')‖ ≤ 2⁻¹ * ‖x - x'‖)
    (x x' : E) :
    ‖(x - inv (M.toFun x)) - (x' - inv (M.toFun x'))‖ ≤ 4⁻¹ * ‖x - x'‖ := by
  have h1 : inv (M.deriv (x - x')) = x - x' := hleft (x - x')
  have ealg : (x - inv (M.toFun x)) - (x' - inv (M.toFun x'))
      = inv (M.deriv (x - x') - (M.toFun x - M.toFun x')) := by
    rw [map_sub, h1, map_sub inv (M.toFun x) (M.toFun x')]
    abel
  rw [ealg]
  have hlip2 : ‖M.deriv (x - x') - (M.toFun x - M.toFun x')‖ ≤ 2⁻¹ * ‖x - x'‖ := by
    rw [norm_sub_rev]
    exact hlip x x'
  calc ‖inv (M.deriv (x - x') - (M.toFun x - M.toFun x'))‖
      ≤ 2⁻¹ * ‖M.deriv (x - x') - (M.toFun x - M.toFun x')‖ := hbound _
    _ ≤ 2⁻¹ * (2⁻¹ * ‖x - x'‖) := mul_le_mul_of_nonneg_left hlip2 (by norm_num)
    _ = 4⁻¹ * ‖x - x'‖ := by ring

/-! ### The implicit function theorem route -/

/-- **Quantitative Newton–Kantorovich existence (gap G1 centerpiece,
PROVED; repairs the false v0.3 statement — finding S2).**

If the residual map `Φ = M.toFun` carries the certificate
* `hleft`/`hright`: `inv` is a two-sided linear inverse of the
  derivative `D = M.deriv` (the algebraic content of
  `DerivIsomorphism`, see `derivIsomorphism_iff`),
* `hbound`: the inverse is bounded with constant β = 1/2,
* `hlip`: `Φ` deviates from its linearization by at most L = 1/2 per
  unit distance (a global strict-differentiability bound; the local
  version follows by shrinking the constants),
* `hsmall`: the residual at the base point is below 1/4,
then `Φ` has an exact zero within distance 1 of the base point —
applied to the RT picture: numeric profile + small Newton correction =
exact critical solution.

*Proof.*  The Newton map `N x = x − D⁻¹Φ x` contracts with constant
βL = 1/4 (`newton_map_contractive`) and moves `x₀` by less than 1/8.
Its iteration sequence is therefore Cauchy with geometric speed (tail
estimate `‖N x₀ − x₀‖ · 4 · (1/4)ⁿ`), converges by completeness, and
the limit is a fixed point of `N` because `N` is continuous (it
contracts).  A fixed point of `N` is a zero of `Φ` since `D⁻¹Φ(x) = 0`
forces `Φ(x) = D(D⁻¹Φ(x)) = 0` by `hright`.  The position bound
`‖x − x₀‖ ≤ 4‖N x₀ − x₀‖ < 1` comes from the same tail estimate. -/
theorem existence_via_implicit_function
    (M : C1MapAt E F) (inv : F →ₗ[ℝ] E)
    (hleft : ∀ v : E, inv (M.deriv v) = v)
    (hright : ∀ w : F, M.deriv (inv w) = w)
    (hbound : ∀ y : F, ‖inv y‖ ≤ 2⁻¹ * ‖y‖)
    (hlip : ∀ x x' : E, ‖M.toFun x - M.toFun x' - M.deriv (x - x')‖ ≤ 2⁻¹ * ‖x - x'‖)
    (hsmall : ‖M.toFun M.x₀‖ < 4⁻¹) :
    ∃ x : E, M.toFun x = 0 ∧ ‖x - M.x₀‖ < 1 := by
  have hcontract := newton_map_contractive M inv hleft hbound hlip
  -- the first Newton step displaces x₀ by less than 1/8
  have hx1 : ‖(M.x₀ - inv (M.toFun M.x₀)) - M.x₀‖ < 8⁻¹ := by
    have hnorm : (M.x₀ - inv (M.toFun M.x₀)) - M.x₀ = -(inv (M.toFun M.x₀)) := by abel
    rw [hnorm, norm_neg]
    have h1 := hbound (M.toFun M.x₀)
    have h2 : (2⁻¹ : ℝ) * ‖M.toFun M.x₀‖ < 2⁻¹ * 4⁻¹ :=
      mul_lt_mul_of_pos_left hsmall (by norm_num)
    have h3 : (2⁻¹ : ℝ) * 4⁻¹ = 8⁻¹ := by ring
    linarith
  -- the Newton iteration
  set seq : ℕ → E := fun n => Nat.rec M.x₀ (fun _ s => s - inv (M.toFun s)) n with hseqdef
  -- telescoping identity
  have htele : ∀ (j n : ℕ),
      seq (n + j) - seq n = ∑ k ∈ Finset.range j, (seq (n + k + 1) - seq (n + k)) := by
    intro j
    induction j with
    | zero => intro n; simp
    | succ i ih =>
      intro n
      have h1 : n + (i + 1) = (n + i) + 1 := by omega
      rw [h1, Finset.sum_range_succ, ← ih n]
      abel
  -- geometric partial sums, exact closed form
  have hgeo : ∀ j : ℕ, ∑ k ∈ Finset.range j, (4⁻¹ : ℝ) ^ k
      = 4 / 3 - (4 / 3) * (4⁻¹ : ℝ) ^ j := by
    intro j
    induction j with
    | zero => norm_num
    | succ i ih =>
      rw [Finset.sum_range_succ, ih, pow_succ]
      field_simp
      ring
  -- geometric tail estimate
  have hgeoTail : ∀ (j n : ℕ),
      ∑ k ∈ Finset.range j, (4⁻¹ : ℝ) ^ (n + k) ≤ 4 * (4⁻¹ : ℝ) ^ n := by
    intro j n
    have hshift : ∑ k ∈ Finset.range j, (4⁻¹ : ℝ) ^ (n + k)
        = (4⁻¹ : ℝ) ^ n * ∑ k ∈ Finset.range j, (4⁻¹ : ℝ) ^ k := by
      rw [Finset.mul_sum]
      refine Finset.sum_congr rfl fun k _ => ?_
      rw [← pow_add]
    rw [hshift, hgeo]
    have hpow : (0 : ℝ) ≤ (4⁻¹ : ℝ) ^ n := pow_nonneg (by norm_num) n
    have hle : (4 / 3 : ℝ) - (4 / 3) * (4⁻¹ : ℝ) ^ j ≤ 4 := by
      have hj : (0 : ℝ) ≤ (4⁻¹ : ℝ) ^ j := pow_nonneg (by norm_num) j
      nlinarith
    linarith [mul_le_mul_of_nonneg_left hle hpow]
  -- per-step decay of the iteration
  have hstep : ∀ m : ℕ, ‖seq (m + 1) - seq m‖
      ≤ (4⁻¹ : ℝ) ^ m * ‖(M.x₀ - inv (M.toFun M.x₀)) - M.x₀‖ := by
    intro m
    induction m with
    | zero => simp only [pow_zero, one_mul]; exact le_rfl
    | succ i ih =>
      have heq : seq (i + 1 + 1) - seq (i + 1)
          = (seq (i + 1) - inv (M.toFun (seq (i + 1))))
            - (seq i - inv (M.toFun (seq i))) := rfl
      rw [heq]
      calc ‖(seq (i + 1) - inv (M.toFun (seq (i + 1)))) - (seq i - inv (M.toFun (seq i)))‖
          ≤ 4⁻¹ * ‖seq (i + 1) - seq i‖ := hcontract _ _
        _ ≤ 4⁻¹ * ((4⁻¹ : ℝ) ^ i * ‖(M.x₀ - inv (M.toFun M.x₀)) - M.x₀‖) :=
            mul_le_mul_of_nonneg_left ih (by norm_num)
        _ = (4⁻¹ : ℝ) ^ (i + 1) * ‖(M.x₀ - inv (M.toFun M.x₀)) - M.x₀‖ := by
            rw [pow_succ]; ring
  -- pair bound via telescoping and the geometric tail
  have hpair : ∀ (m n : ℕ), n ≤ m → ‖seq m - seq n‖
      ≤ ‖(M.x₀ - inv (M.toFun M.x₀)) - M.x₀‖ * (4 * (4⁻¹ : ℝ) ^ n) := by
    intro m n hnm
    have hsplit : m = n + (m - n) := by omega
    rw [hsplit, htele]
    calc ‖∑ k ∈ Finset.range (m - n), (seq (n + k + 1) - seq (n + k))‖
        ≤ ∑ k ∈ Finset.range (m - n), ‖seq (n + k + 1) - seq (n + k)‖ := norm_sum_le _ _
      _ ≤ ∑ k ∈ Finset.range (m - n),
            (4⁻¹ : ℝ) ^ (n + k) * ‖(M.x₀ - inv (M.toFun M.x₀)) - M.x₀‖ :=
          Finset.sum_le_sum fun k _ => hstep (n + k)
      _ = ‖(M.x₀ - inv (M.toFun M.x₀)) - M.x₀‖
            * ∑ k ∈ Finset.range (m - n), (4⁻¹ : ℝ) ^ (n + k) := by
          rw [Finset.mul_sum]
          exact Finset.sum_congr rfl fun k _ => mul_comm _ _
      _ ≤ ‖(M.x₀ - inv (M.toFun M.x₀)) - M.x₀‖ * (4 * (4⁻¹ : ℝ) ^ n) :=
          mul_le_mul_of_nonneg_left (hgeoTail (m - n) n) (norm_nonneg _)
  -- the sequence is Cauchy
  have hcauchy : CauchySeq seq := by
    rw [Metric.cauchySeq_iff]
    intro ε hε
    obtain ⟨N, hN⟩ := exists_pow_lt_of_lt_one (by linarith : (0 : ℝ) < 2 * ε)
      (by norm_num : (2⁻¹ : ℝ) < 1)
    have hNq : (4⁻¹ : ℝ) ^ N < 2 * ε := by
      have hle : (4⁻¹ : ℝ) ^ N ≤ (2⁻¹ : ℝ) ^ N :=
        pow_le_pow_left₀ (by norm_num : (0 : ℝ) ≤ 4⁻¹)
          (by norm_num : (4⁻¹ : ℝ) ≤ 2⁻¹) N
      linarith
    have finish : ∀ a b : ℕ, N ≤ b → b ≤ a → ‖seq a - seq b‖ < ε := by
      intro a b hb hba
      have hbound := hpair a b hba
      have hq : (4⁻¹ : ℝ) ^ b ≤ (4⁻¹ : ℝ) ^ N := by
        have hpow : (4⁻¹ : ℝ) ^ b = (4⁻¹ : ℝ) ^ N * (4⁻¹ : ℝ) ^ (b - N) := by
          have hex : N + (b - N) = b := by omega
          rw [← pow_add, hex]
        rw [hpow]
        exact mul_le_of_le_one_right (pow_nonneg (by norm_num) N)
          (pow_le_one₀ (by norm_num) (by norm_num))
      have hc8 : ‖(M.x₀ - inv (M.toFun M.x₀)) - M.x₀‖ * 4 ≤ 2⁻¹ := by nlinarith
      have hmul : ‖(M.x₀ - inv (M.toFun M.x₀)) - M.x₀‖ * (4 * (4⁻¹ : ℝ) ^ b)
          ≤ 2⁻¹ * (4⁻¹ : ℝ) ^ N := by
        have e1 : ‖(M.x₀ - inv (M.toFun M.x₀)) - M.x₀‖ * (4 * (4⁻¹ : ℝ) ^ b)
            = (‖(M.x₀ - inv (M.toFun M.x₀)) - M.x₀‖ * 4) * (4⁻¹ : ℝ) ^ b := by ring
        rw [e1]
        exact mul_le_mul hc8 hq (pow_nonneg (by norm_num) b) (by norm_num)
      nlinarith
    refine ⟨N, fun m hm n hn => ?_⟩
    rw [dist_eq_norm]
    rcases le_total n m with hmn | hmn
    · exact finish m n hn hmn
    · rw [norm_sub_rev]
      exact finish n m hm hmn
  -- its limit
  obtain ⟨xstar, hxstar⟩ := cauchySeq_tendsto_of_complete hcauchy
  -- the limit is a fixed point of the Newton map
  have hfix : xstar - inv (M.toFun xstar) = xstar := by
    have hd : Filter.Tendsto
        (fun n => (seq n - inv (M.toFun (seq n))) - (xstar - inv (M.toFun xstar)))
        atTop (nhds 0) := by
      rw [tendsto_zero_iff_norm_tendsto_zero]
      have hle : ∀ n : ℕ, ‖(seq n - inv (M.toFun (seq n))) - (xstar - inv (M.toFun xstar))‖
          ≤ 4⁻¹ * ‖seq n - xstar‖ := fun n => hcontract (seq n) xstar
      have hnorm : Filter.Tendsto (fun n => ‖seq n - xstar‖) atTop (nhds 0) := by
        have hsub : Filter.Tendsto (fun n => seq n - xstar) atTop (nhds (xstar - xstar)) :=
          hxstar.sub tendsto_const_nhds
        have hzz : xstar - xstar = 0 := sub_self xstar
        rw [hzz] at hsub
        have hn := hsub.norm
        rwa [norm_zero] at hn
      exact squeeze_zero (fun n => norm_nonneg _) hle
        (by simpa [mul_zero] using hnorm.const_mul (4⁻¹ : ℝ))
    have hA : Filter.Tendsto (fun n => seq n - inv (M.toFun (seq n))) atTop
        (nhds (xstar - inv (M.toFun xstar))) := by
      have hadd := hd.add_const (xstar - inv (M.toFun xstar))
      simpa [sub_add_cancel] using hadd
    have hB : Filter.Tendsto (fun n => seq n - inv (M.toFun (seq n))) atTop (nhds xstar) := by
      have heq : (fun n => seq n - inv (M.toFun (seq n))) = fun n => seq (n + 1) :=
        funext fun n => rfl
      rw [heq]
      have hsucc : Filter.Tendsto (fun n : ℕ => n + 1) atTop atTop :=
        Filter.tendsto_atTop_atTop.mpr fun K => ⟨K, fun n hn => by omega⟩
      exact hxstar.comp hsucc
    exact tendsto_nhds_unique (Y := ℕ) (l := Filter.atTop) hA hB
  -- a fixed point of the Newton map is a zero of the residual
  have hzero : M.toFun xstar = 0 := by
    have hinv0 : inv (M.toFun xstar) = 0 := by
      have h1 : xstar - (xstar - inv (M.toFun xstar)) = 0 := by rw [hfix, sub_self]
      rw [sub_sub_cancel] at h1
      exact h1
    have h2 := hright (M.toFun xstar)
    rw [hinv0, map_zero] at h2
    exact h2.symm
  -- position of the zero: within distance 4‖N x₀ − x₀‖ < 1
  have hpos : ‖xstar - M.x₀‖ < 1 := by
    have hbound' : ∀ j : ℕ, ‖seq ((0 : ℕ) + j) - seq 0‖
        ≤ ‖(M.x₀ - inv (M.toFun M.x₀)) - M.x₀‖ * (4 * ((4⁻¹ : ℝ) ^ (0 : ℕ))) :=
      fun j => hpair ((0 : ℕ) + j) 0 (by omega)
    have hlim : ‖xstar - M.x₀‖
        ≤ ‖(M.x₀ - inv (M.toFun M.x₀)) - M.x₀‖ * (4 * ((4⁻¹ : ℝ) ^ (0 : ℕ))) := by
      have h2 : Filter.Tendsto (fun j => ‖seq ((0 : ℕ) + j) - seq 0‖) atTop
          (nhds (‖xstar - M.x₀‖)) := by
        simp only [Nat.zero_add]
        exact Filter.Tendsto.norm (hxstar.sub tendsto_const_nhds)
      exact le_of_tendsto h2 (Filter.Eventually.of_forall hbound')
    rw [pow_zero, mul_one] at hlim
    have h4 : ‖(M.x₀ - inv (M.toFun M.x₀)) - M.x₀‖ * 4 < 1 := by nlinarith
    have hring : ‖(M.x₀ - inv (M.toFun M.x₀)) - M.x₀‖ * 4
        = 4 * ‖(M.x₀ - inv (M.toFun M.x₀)) - M.x₀‖ := by ring
    rw [hring] at h4
    nlinarith
  exact ⟨xstar, hzero, hpos⟩

/-- **Uniqueness of the zero inside the Newton contraction (new in
v0.4, PROVED).**  Two zeros of the residual map coincide: both are
fixed points of the contracting Newton map, and a contraction has at
most one fixed point.  This is the analytic half of the
Reiterer–Trubowitz uniqueness statement for the critical solution (the
other half — that DSS solutions of the field equations are captured by
the Newton basin — is Phase-2 content). -/
theorem newton_zero_unique (M : C1MapAt E F) (inv : F →ₗ[ℝ] E)
    (hleft : ∀ v : E, inv (M.deriv v) = v)
    (hbound : ∀ y : F, ‖inv y‖ ≤ 2⁻¹ * ‖y‖)
    (hlip : ∀ x x' : E, ‖M.toFun x - M.toFun x' - M.deriv (x - x')‖ ≤ 2⁻¹ * ‖x - x'‖)
    (x₁ x₂ : E) (h₁ : M.toFun x₁ = 0) (h₂ : M.toFun x₂ = 0) :
    x₁ = x₂ := by
  have hc := newton_map_contractive M inv hleft hbound hlip x₁ x₂
  have e1 : (x₁ - inv (M.toFun x₁)) - (x₂ - inv (M.toFun x₂)) = x₁ - x₂ := by
    simp only [h₁, h₂, map_zero, sub_zero]
  rw [← e1] at hc
  have h0 : (0 : ℝ) ≤ ‖x₁ - x₂‖ := norm_nonneg _
  rcases eq_or_lt_of_le h0 with h0' | h0'
  · exact sub_eq_zero.mp (norm_eq_zero.mp h0'.symm)
  · exfalso
    have hq : (4⁻¹ : ℝ) < 1 := by norm_num
    have hND : ‖(x₁ - inv (M.toFun x₁)) - (x₂ - inv (M.toFun x₂))‖
        = ‖x₁ - x₂‖ := by rw [e1]
    rw [hND] at hc
    have hlt : (4⁻¹ : ℝ) * ‖x₁ - x₂‖ < ‖x₁ - x₂‖ :=
      by simpa using mul_lt_mul_of_pos_right hq h0'
    linarith

/-- **Stability of the conclusion under perturbation of the data —
PROVED in repaired form (was finding S3).**  The v0.3 statement was
false: a map pointwise within 0.001 of `Φ` need not have a zero (e.g.
`Φ' (x) = x + 0.0009·sgn-step`).  The honest version keeps the full
Newton certificate for both maps (same derivative isomorphism, same
bounds) and a quantitative closeness `1/16`; then the perturbed map
also has a zero.  This is the lemma through which strict interval
certificates from the Python service (`interval_bound` endpoint, gap
G5→G1) enter the existence proof. -/
theorem existence_persists_under_perturbation
    (M M' : C1MapAt E F) (inv : F →ₗ[ℝ] E)
    (hleft : ∀ v : E, inv (M.deriv v) = v)
    (hright : ∀ w : F, M.deriv (inv w) = w)
    (hbound : ∀ y : F, ‖inv y‖ ≤ 2⁻¹ * ‖y‖)
    (hlip : ∀ x x' : E, ‖M.toFun x - M.toFun x' - M.deriv (x - x')‖ ≤ 2⁻¹ * ‖x - x'‖)
    (hderiv : M'.deriv = M.deriv)
    (hx₀ : M'.x₀ = M.x₀)
    (hlip' : ∀ x x' : E, ‖M'.toFun x - M'.toFun x' - M.deriv (x - x')‖ ≤ 2⁻¹ * ‖x - x'‖)
    (hsmall : ‖M.toFun M.x₀‖ ≤ 16⁻¹)
    (hclose : ∀ x : E, ‖M'.toFun x - M.toFun x‖ ≤ 16⁻¹) :
    (∃ x : E, M.toFun x = 0) → ∃ x' : E, M'.toFun x' = 0 := by
  intro _
  have hleft' : ∀ v : E, inv (M'.deriv v) = v := by
    intro v
    rw [hderiv]
    exact hleft v
  have hright' : ∀ w : F, M'.deriv (inv w) = w := by
    intro w
    rw [hderiv]
    exact hright w
  have hlip'M' : ∀ x x' : E,
      ‖M'.toFun x - M'.toFun x' - M'.deriv (x - x')‖ ≤ 2⁻¹ * ‖x - x'‖ := by
    intro x x'
    rw [hderiv]
    exact hlip' x x'
  have hsmall' : ‖M'.toFun M'.x₀‖ < 4⁻¹ := by
    rw [hx₀]
    have h1 : ‖M'.toFun M.x₀‖ ≤ ‖M'.toFun M.x₀ - M.toFun M.x₀‖ + ‖M.toFun M.x₀‖ := by
      have h2 : M'.toFun M.x₀ - M.toFun M.x₀ + M.toFun M.x₀ = M'.toFun M.x₀ := by abel
      calc ‖M'.toFun M.x₀‖ = ‖M'.toFun M.x₀ - M.toFun M.x₀ + M.toFun M.x₀‖ := by rw [h2]
        _ ≤ ‖M'.toFun M.x₀ - M.toFun M.x₀‖ + ‖M.toFun M.x₀‖ := norm_add_le _ _
    have h2 := hclose M.x₀
    have h3 : (16⁻¹ : ℝ) + 16⁻¹ < 4⁻¹ := by norm_num
    linarith
  obtain ⟨x', hx', -⟩ := existence_via_implicit_function M' inv hleft' hright' hbound hlip'M' hsmall'
  exact ⟨x', hx'⟩

end Choptuik.Existence
