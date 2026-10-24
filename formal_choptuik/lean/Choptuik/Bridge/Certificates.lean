/-
╔══════════════════════════════════════════════════════════════════════╗
║   FORMAL CHOPTUIK · Choptuik.Bridge.Certificates                      ║
║   The typed certificate layer of the Lean ⇄ Python bridge (gap G4)    ║
╠══════════════════════════════════════════════════════════════════════╣
║   The bridge ships certificates, never raw floats, into the proof     ║
║   layer (the discipline of blueprint/axiomatic_base.md).  This        ║
║   module fixes the certificate currency and proves the two            ║
║   interpretation theorems that turn certificate data into physics:    ║
║                                                                       ║
║   * `RatIv` — a closed rational interval; the emitted enclosures of   ║
║     `python/choptuik_service/certify.py` are values of this type.     ║
║                                                                       ║
║   * `SpectrumChecks` / `spectrum_shape_of_certificate` — the G2       ║
║     consumption pattern: a certificate whose checks pass (tight       ║
║     rational enclosures, agreement with the model targets, odd-       ║
║     multiple echo structure) forces the universality shape — one      ║
║     unstable mode, the rest stable, and every positive imaginary      ║
║     part an odd multiple of one fundamental within a fixed 1e-5       ║
║     tolerance — for ANY operator whose eigenvalues pair with the      ║
║     slots.  The pairing itself is numerical content, locked by the    ║
║     pytest regression, not by Lean (the honest boundary of G4).       ║
║                                                                       ║
║   * `newton_kantorovich_local` — the bridge-driven generalization     ║
║     of the v0.4 Newton–Kantorovich core: the constants (β, L, r, R)   ║
║     are now SUPPLIED BY THE CERTIFICATE instead of being hardcoded    ║
║     to 1/2, and the Lipschitz defect is only required on the closed   ║
║     ball where the iteration lives (the local form promised by the    ║
║     v0.4 comments and now actually proved).                          ║
╠══════════════════════════════════════════════════════════════════════╣
║   status : v0.4.1 — certificate layer complete; consumers in          ║
║   Choptuik.Bridge.Generated (emitted data) and Choptuik.Bridge.       ║
║   Discharge (headline theorems).                                     ║
╚══════════════════════════════════════════════════════════════════════╝
-/

import Mathlib.Tactic
import Choptuik.Existence.ImplicitFunction

namespace Choptuik.Bridge

open Choptuik.Existence Filter

/-! ### Rational intervals — the certificate currency -/

/-- A closed interval with rational endpoints.  The Python producer
emits these as exact decimal rationals; nothing floating-point ever
crosses the bridge. -/
structure RatIv where
  /-- lower endpoint -/
  lo : ℚ
  /-- upper endpoint -/
  hi : ℚ

namespace RatIv

/-- Rational membership `lo ≤ x ≤ hi`. -/
def mem (I : RatIv) (x : ℚ) : Prop := I.lo ≤ x ∧ x ≤ I.hi

/-- Width `hi - lo` (the tightness coordinate of a certificate). -/
def width (I : RatIv) : ℚ := I.hi - I.lo

/-- Real membership: a real number lies in the rational enclosure. -/
def realMem (I : RatIv) (x : ℝ) : Prop := (I.lo : ℝ) ≤ x ∧ x ≤ (I.hi : ℝ)

/-- Rational membership casts to real membership. -/
theorem realMem_of_mem {x : ℚ} {I : RatIv} (h : I.mem x) : I.realMem (x : ℝ) :=
  ⟨Rat.cast_le.mpr h.1, Rat.cast_le.mpr h.2⟩

end RatIv

/-! ### Tolerances (module constants shared with the producer) -/

/-- Echo-family tolerance: every positive imaginary part sits within
`1/100000` of an odd multiple of the fundamental. -/
def echoTolerance : ℚ := 1 / 100000

/-- Maximum admitted width of a spectrum enclosure. -/
def widthMax : ℚ := 1 / 10 ^ 6

/-- Maximum admitted width of the interval-Newton band. -/
def bandWidthMax : ℚ := 1 / 10 ^ 5

/-! ### The spectrum certificate -/

/-- The spectrum certificate: rational enclosures of the computed
eigenvalues of the truncated mode model — the unstable rate `lam0`,
the real parts `re k` of the decaying pairs, and the positive imaginary
parts `im k` of the echo family (slots `k < n`; conjugate entries share
the `re` slot). -/
structure SpectrumCert where
  /-- number of decaying conjugate pairs -/
  n : ℕ
  /-- enclosure of the unstable eigenvalue (real) -/
  lam0 : RatIv
  /-- enclosure of the real part of pair `k` (both conjugates) -/
  re : ℕ → RatIv
  /-- enclosure of the positive imaginary part of pair `k` -/
  im : ℕ → RatIv

/-- The full check suite of a spectrum certificate — everything the
Lean side verifies, by exact rational arithmetic, about the emitted
data.  Shape half: one positive slot, stable decaying slots, positive
echo slots, fundamental separated from the tolerance.  Agreement half:
the model targets (λ₀ = 2.6745, Re = -(4.3 + 1.8k)) lie inside the
enclosures, and the echo family is odd-multiple structured.  Tightness
half: all widths bounded. -/
structure SpectrumChecks (c : SpectrumCert) : Prop where
  unstable_pos : 0 < c.lam0.lo
  decaying_neg : ∀ k < c.n, (c.re k).hi < 0
  im_pos : ∀ k < c.n, 0 < (c.im k).lo
  fundamental_gt_slack : echoTolerance < (c.im 0).lo
  lam0_agree : c.lam0.mem (26745 / 10000)
  re_agree : ∀ k < c.n, (c.re k).mem (-(43 + 18 * (k : ℚ)) / 10)
  odd_lo : ∀ k < c.n, ((2 * k + 1 : ℕ) : ℚ) * (c.im 0).hi - echoTolerance ≤ (c.im k).lo
  odd_hi : ∀ k < c.n, (c.im k).hi ≤ ((2 * k + 1 : ℕ) : ℚ) * (c.im 0).lo + echoTolerance
  lam0_width : c.lam0.width ≤ widthMax
  re_width : ∀ k < c.n, (c.re k).width ≤ widthMax
  im_width : ∀ k < c.n, (c.im k).width ≤ widthMax

/-! ### Interpretation lemmas (ℚ data → ℝ conclusions) -/

/-- An eigenvalue certified by the unstable slot has positive real part. -/
theorem certified_unstable_pos {c : SpectrumCert} (hc : SpectrumChecks c)
    {lam0 : ℝ} (h0 : c.lam0.realMem lam0) : 0 < lam0 := by
  have h : (0 : ℝ) < ((c.lam0.lo : ℚ) : ℝ) := by exact_mod_cast hc.unstable_pos
  linarith [h0.1, h]

/-- An eigenvalue certified by a decaying slot has negative real part. -/
theorem certified_decaying_neg {c : SpectrumCert} (hc : SpectrumChecks c)
    {k : ℕ} (hk : k < c.n) {y : ℝ} (hy : (c.re k).realMem y) : y < 0 := by
  have h : ((c.re k).hi : ℚ) < (0 : ℚ) := hc.decaying_neg k hk
  have h' : ((c.re k).hi : ℝ) < (0 : ℝ) := by exact_mod_cast h
  linarith [hy.2, h']

/-- **Odd-multiple structure of the echo family (the heart of the
spectral interpretation).**  If `y` lies in slot `k` and `z` in the
fundamental slot, then `y` is within `echoTolerance` of the odd
multiple `(2k+1)·z`.  The proof combines the certificate inequalities
`odd_lo`/`odd_hi` with the monotone transport through the fundamental
enclosure — pure rational arithmetic cast to ℝ. -/
theorem im_odd_multiple {c : SpectrumCert} (hc : SpectrumChecks c)
    {k : ℕ} (hk : k < c.n) {y z : ℝ}
    (hy : (c.im k).realMem y) (hz : (c.im 0).realMem z) :
    |y - (2 * (k : ℝ) + 1) * z| ≤ (echoTolerance : ℝ) := by
  have hk0 : (0 : ℝ) ≤ (k : ℝ) := Nat.cast_nonneg k
  have hcoef : (0 : ℝ) ≤ 2 * (k : ℝ) + 1 := by linarith
  -- upper: y ≤ hi_k ≤ (2k+1)·lo_0 + W ≤ (2k+1)·z + W
  have hup : y - (2 * (k : ℝ) + 1) * z ≤ (echoTolerance : ℝ) := by
    have a1 : ((c.im k).hi : ℝ) ≤ (2 * (k : ℝ) + 1) * ((c.im 0).lo : ℝ)
        + (echoTolerance : ℝ) := by exact_mod_cast hc.odd_hi k hk
    have a2 : (2 * (k : ℝ) + 1) * ((c.im 0).lo : ℝ)
        ≤ (2 * (k : ℝ) + 1) * z :=
      mul_le_mul_of_nonneg_left hz.1 hcoef
    linarith [hy.2, a1, a2]
  -- lower: (2k+1)·z ≤ (2k+1)·hi_0 ≤ lo_k + W ≤ y + W
  have hdown : (2 * (k : ℝ) + 1) * z - y ≤ (echoTolerance : ℝ) := by
    have a1 : (2 * (k : ℝ) + 1) * ((c.im 0).hi : ℝ) - (echoTolerance : ℝ)
        ≤ ((c.im k).lo : ℝ) := by exact_mod_cast hc.odd_lo k hk
    have a2 : (2 * (k : ℝ) + 1) * z
        ≤ (2 * (k : ℝ) + 1) * ((c.im 0).hi : ℝ) :=
      mul_le_mul_of_nonneg_left hz.2 hcoef
    linarith [hy.1, a1, a2]
  rw [abs_le]
  exact ⟨by linarith, by linarith⟩

/-- **The spectrum-shape theorem (G2 consumption, robustness form).**
Any family of complex eigenvalues pairing with a checked certificate
has the universality shape: the certified unstable rate is positive,
every decaying slot is strictly stable with a positive echo member,
and every echo frequency is an odd multiple of the fundamental within
the fixed tolerance `1/100000`. -/
theorem spectrum_shape_of_certificate {c : SpectrumCert} (hc : SpectrumChecks c)
    {lam0 : ℝ} (h0 : c.lam0.realMem lam0)
    {m : ℕ → ℂ} (hm : ∀ k < c.n, (c.re k).realMem (m k).re ∧ (c.im k).realMem (m k).im) :
    0 < lam0 ∧ (∀ k < c.n, (m k).re < 0 ∧ 0 < (m k).im) ∧
      ∀ k < c.n, |(m k).im - (2 * (k : ℝ) + 1) * (m 0).im| ≤ (echoTolerance : ℝ) := by
  refine ⟨certified_unstable_pos hc h0, ?_, ?_⟩
  · intro k hk
    obtain ⟨hre, him⟩ := hm k hk
    have hpos : (0 : ℝ) < ((c.im k).lo : ℚ) := by exact_mod_cast hc.im_pos k hk
    have hpos' : (0 : ℝ) < ((c.im k).lo : ℝ) := by exact_mod_cast hc.im_pos k hk
    exact ⟨certified_decaying_neg hc hk hre, by linarith [him.1, hpos']⟩
  · intro k hk
    obtain ⟨-, him⟩ := hm k hk
    obtain ⟨-, him0⟩ := hm 0 (lt_of_le_of_lt (Nat.zero_le k) hk)
    exact im_odd_multiple hc hk him him0

/-! ### Local Newton–Kantorovich with certificate-supplied constants -/

variable {E F : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E] [CompleteSpace E]
  [NormedAddCommGroup F] [NormedSpace ℝ F]

/-- **Local Newton–Kantorovich (bridge-driven generalization of the v0.4
core).**  The v0.4 theorem hardcoded β = L = 1/2 and a global Lipschitz
defect; the certificate channel needs the constants supplied by the
producer and the defect only on the ball where the iteration lives.
Hypotheses, all quantitative and all checkable from rational data:

* `hleft`/`hright` — `inv` is a two-sided inverse of the derivative;
* `hbound` — the inverse is bounded by `β`;
* `hlip` — the deviation from linearity is `L`-Lipschitz **on the
  closed ball** `‖x - x₀‖ ≤ R`;
* `hsmall` — the residual at the base point is at most `r`;
* `hq`/`hR` — the contraction budget: `βL < 1` and the total
  displacement budget `βr/(1 - βL)` fits in the ball.

Conclusion: an exact zero within the ball.  The Newton map contracts
with `βL`, moves `x₀` by at most `βr`, and the geometric tail of the
iteration stays inside `βr/(1 - βL) ≤ R` — so the induction never
leaves the region where `hlip` applies. -/
theorem newton_kantorovich_local (M : C1MapAt E F) (inv : F →ₗ[ℝ] E)
    {β L r R : ℝ} (hβ : 0 ≤ β) (hL : 0 ≤ L) (hq : β * L < 1) (hr0 : 0 ≤ r)
    (hleft : ∀ v : E, inv (M.deriv v) = v)
    (hright : ∀ w : F, M.deriv (inv w) = w)
    (hbound : ∀ y : F, ‖inv y‖ ≤ β * ‖y‖)
    (hlip : ∀ x x' : E, ‖x - M.x₀‖ ≤ R → ‖x' - M.x₀‖ ≤ R →
      ‖M.toFun x - M.toFun x' - M.deriv (x - x')‖ ≤ L * ‖x - x'‖)
    (hsmall : ‖M.toFun M.x₀‖ ≤ r)
    (hR : β * r / (1 - β * L) ≤ R) :
    ∃ x : E, M.toFun x = 0 ∧ ‖x - M.x₀‖ ≤ R := by
  have hone : (0 : ℝ) < 1 - β * L := by linarith
  have hq0 : (0 : ℝ) ≤ β * L := mul_nonneg hβ hL
  have hβr0 : (0 : ℝ) ≤ β * r := mul_nonneg hβ hr0
  have hS0 : (0 : ℝ) ≤ β * r / (1 - β * L) := div_nonneg hβr0 hone.le
  -- the Newton map contracts on the closed ball, with constant β·L
  have hcontr : ∀ x x' : E, ‖x - M.x₀‖ ≤ R → ‖x' - M.x₀‖ ≤ R →
      ‖(x - inv (M.toFun x)) - (x' - inv (M.toFun x'))‖ ≤ β * L * ‖x - x'‖ := by
    intro x x' hx hx'
    have h1 : inv (M.deriv (x - x')) = x - x' := hleft (x - x')
    have ealg : (x - inv (M.toFun x)) - (x' - inv (M.toFun x'))
        = inv (M.deriv (x - x') - (M.toFun x - M.toFun x')) := by
      rw [map_sub, h1, map_sub inv (M.toFun x) (M.toFun x')]
      abel
    have hlip2 : ‖M.deriv (x - x') - (M.toFun x - M.toFun x')‖ ≤ L * ‖x - x'‖ := by
      rw [norm_sub_rev]
      exact hlip x x' hx hx'
    rw [ealg]
    calc ‖inv (M.deriv (x - x') - (M.toFun x - M.toFun x'))‖
        ≤ β * ‖M.deriv (x - x') - (M.toFun x - M.toFun x')‖ := hbound _
      _ ≤ β * (L * ‖x - x'‖) := mul_le_mul_of_nonneg_left hlip2 hβ
      _ = β * L * ‖x - x'‖ := by ring
  -- the Newton iteration
  set seq : ℕ → E := fun n => Nat.rec M.x₀ (fun _ s => s - inv (M.toFun s)) n with hseqdef
  -- first-step displacement
  have hd0 : ‖(M.x₀ - inv (M.toFun M.x₀)) - M.x₀‖ ≤ β * r := by
    have hnorm : (M.x₀ - inv (M.toFun M.x₀)) - M.x₀ = -(inv (M.toFun M.x₀)) := by abel
    rw [hnorm, norm_neg]
    calc ‖inv (M.toFun M.x₀)‖ ≤ β * ‖M.toFun M.x₀‖ := hbound _
      _ ≤ β * r := mul_le_mul_of_nonneg_left hsmall hβ
  -- telescoping identities (two forms: to the base point, and shifted)
  have htele : ∀ n : ℕ,
      seq n - M.x₀ = ∑ j ∈ Finset.range n, (seq (j + 1) - seq j) := by
    intro n
    induction n with
    | zero => simp [hseqdef]
    | succ i ih =>
        rw [Finset.sum_range_succ, ← ih]
        abel
  have hshift : ∀ (j n : ℕ),
      seq (n + j) - seq n = ∑ k ∈ Finset.range j, (seq (n + k + 1) - seq (n + k)) := by
    intro j
    induction j with
    | zero => intro n; simp
    | succ i ih =>
        intro n
        have h1 : n + (i + 1) = (n + i) + 1 := by omega
        rw [h1, Finset.sum_range_succ, ← ih n]
        abel
  -- geometric sums in product form (no division)
  have hgeom : ∀ n : ℕ,
      (∑ j ∈ Finset.range n, (β * L) ^ j) * (1 - β * L) = 1 - (β * L) ^ n := by
    intro n
    induction n with
    | zero => simp
    | succ i ih =>
        rw [Finset.sum_range_succ, add_mul, ih, pow_succ]
        ring
  have hsum_le : ∀ n : ℕ, ∑ j ∈ Finset.range n, (β * L) ^ j ≤ 1 / (1 - β * L) := by
    intro n
    rw [le_div_iff₀ hone]
    have hg := hgeom n
    have hpow : (0 : ℝ) ≤ (β * L) ^ n := pow_nonneg hq0 n
    linarith
  -- the main induction: position and per-step decay, ball-aware
  have hmain : ∀ m : ℕ, ‖seq m - M.x₀‖ ≤ β * r / (1 - β * L) ∧
      ∀ j ≤ m, ‖seq (j + 1) - seq j‖ ≤ (β * L) ^ j * (β * r) := by
    intro m
    induction m with
    | zero =>
        have hz : ‖seq 0 - M.x₀‖ = 0 := by simp [hseqdef]
        refine ⟨le_trans (le_of_eq hz) hS0, ?_⟩
        intro j hj
        have hj0 : j = 0 := Nat.le_zero.mp hj
        subst hj0
        show ‖seq 1 - seq 0‖ ≤ (β * L) ^ 0 * (β * r)
        rw [pow_zero, one_mul]
        exact hd0
    | succ i ih =>
        obtain ⟨hpos_i, hstep_i⟩ := ih
        have hball_i : ‖seq i - M.x₀‖ ≤ R := le_trans hpos_i hR
        have hpos_i1 : ‖seq (i + 1) - M.x₀‖ ≤ β * r / (1 - β * L) := by
          rw [htele (i + 1)]
          calc ‖∑ j ∈ Finset.range (i + 1), (seq (j + 1) - seq j)‖
              ≤ ∑ j ∈ Finset.range (i + 1), ‖seq (j + 1) - seq j‖ := norm_sum_le _ _
            _ ≤ ∑ j ∈ Finset.range (i + 1), (β * L) ^ j * (β * r) :=
                Finset.sum_le_sum fun j hj =>
                  hstep_i j (Nat.lt_succ_iff.mp (Finset.mem_range.mp hj))
            _ = β * r * ∑ j ∈ Finset.range (i + 1), (β * L) ^ j := by
                rw [← Finset.sum_mul]
                ring
            _ ≤ β * r * (1 / (1 - β * L)) :=
                mul_le_mul_of_nonneg_left (hsum_le (i + 1)) hβr0
            _ = β * r / (1 - β * L) := by field_simp
        have hball_i1 : ‖seq (i + 1) - M.x₀‖ ≤ R := le_trans hpos_i1 hR
        refine ⟨hpos_i1, ?_⟩
        intro j hj
        rcases Nat.lt_or_ge j (i + 1) with hlt | hge
        · exact hstep_i j (Nat.lt_succ_iff.mp hlt)
        · have hj1 : j = i + 1 := Nat.le_antisymm hj hge
          subst hj1
          have heq : seq (i + 1 + 1) - seq (i + 1)
              = (seq (i + 1) - inv (M.toFun (seq (i + 1))))
                - (seq i - inv (M.toFun (seq i))) := rfl
          rw [heq]
          calc ‖(seq (i + 1) - inv (M.toFun (seq (i + 1))))
                  - (seq i - inv (M.toFun (seq i)))‖
              ≤ β * L * ‖seq (i + 1) - seq i‖ := hcontr _ _ hball_i1 hball_i
            _ ≤ β * L * ((β * L) ^ i * (β * r)) :=
                mul_le_mul_of_nonneg_left (hstep_i i (le_refl i)) hq0
            _ = (β * L) ^ (i + 1) * (β * r) := by rw [pow_succ]; ring
  -- the tail bound: geometric decay, uniformly in the starting index
  have hpow_small : ∀ ε > 0, ∃ N : ℕ, ∀ b ≥ N, (β * L) ^ b * (β * r / (1 - β * L)) < ε := by
    intro ε hε
    rcases eq_or_ne (β * L) 0 with hzero | hpos
    · refine ⟨1, fun b hb => ?_⟩
      have hb1 : (0 : ℕ) < b := hb
      rw [hzero, zero_pow (Nat.ne_of_gt hb1), zero_mul]
      exact hε
    · rcases eq_or_ne (β * r) 0 with hbr0 | hbrpos
      · -- degenerate budget: the tail is identically zero
        refine ⟨1, fun b _ => ?_⟩
        have hz : β * r / (1 - β * L) = 0 := by
          rw [hbr0]
          exact zero_div _
        rw [hz, mul_zero]
        exact hε
      · have hbpos : (0 : ℝ) < β * r := lt_of_le_of_ne hβr0 hbrpos.symm
        have hone2 : (0 : ℝ) < 1 + β * r := by linarith
        have hA : (0 : ℝ) < ε * (1 - β * L) / (1 + β * r) :=
          div_pos (mul_pos hε hone) hone2
        obtain ⟨N, hN⟩ := exists_pow_lt_of_lt_one hA (by linarith : (β * L : ℝ) < 1)
        refine ⟨N, fun b hb => ?_⟩
        have hCge : (0 : ℝ) ≤ β * r / (1 - β * L) := hS0
        have hCpos : (0 : ℝ) < β * r / (1 - β * L) := div_pos hbpos hone
        have hle : (β * L) ^ b ≤ (β * L) ^ N := by
          have hex : b = N + (b - N) := by omega
          rw [hex, pow_add]
          exact mul_le_of_le_one_right (pow_nonneg hq0 N)
            (pow_le_one₀ hq0 (by linarith : (β * L : ℝ) ≤ 1))
        have hsimpl : ε * (1 - β * L) / (1 + β * r) * (β * r / (1 - β * L))
            = ε * β * r / (1 + β * r) := by
          field_simp
          ring
        have h2 : (β * L) ^ N * (β * r / (1 - β * L)) < ε * β * r / (1 + β * r) := by
          rw [← hsimpl]
          exact mul_lt_mul_of_pos_right hN hCpos
        have h3 : ε * β * r / (1 + β * r) < ε := by
          have hlt : β * r < 1 + β * r := by linarith
          have hmul : β * r * ε < (1 + β * r) * ε := mul_lt_mul_of_pos_right hlt hε
          rw [div_lt_iff₀ hone2]
          linarith
        calc (β * L) ^ b * (β * r / (1 - β * L))
            ≤ (β * L) ^ N * (β * r / (1 - β * L)) :=
              mul_le_mul_of_nonneg_right hle hCge
          _ < ε * β * r / (1 + β * r) := h2
          _ < ε := h3
  -- the iteration is Cauchy
  have hcauchy : CauchySeq seq := by
    rw [Metric.cauchySeq_iff]
    intro ε hε
    obtain ⟨N, hN⟩ := hpow_small ε hε
    have hsplit : ∀ (a b : ℕ), b ≤ a → seq a - seq b
        = ∑ j ∈ Finset.range (a - b), (seq (b + j + 1) - seq (b + j)) := by
      intro a b hb
      have h : b + (a - b) = a := by omega
      have hs := hshift (a - b) b
      rw [h] at hs
      exact hs
    refine ⟨N + 1, fun a ha b hb => ?_⟩
    rw [dist_eq_norm]
    rcases le_total b a with hab | hab
    · rw [hsplit a b hab]
      calc ‖∑ j ∈ Finset.range (a - b), (seq (b + j + 1) - seq (b + j))‖
          ≤ ∑ j ∈ Finset.range (a - b), ‖seq (b + j + 1) - seq (b + j)‖ := norm_sum_le _ _
        _ ≤ ∑ j ∈ Finset.range (a - b), (β * L) ^ (b + j) * (β * r) :=
              Finset.sum_le_sum fun j _ => (hmain (b + j)).2 (b + j) (le_refl _)
        _ = β * r * ((β * L) ^ b * ∑ j ∈ Finset.range (a - b), (β * L) ^ j) := by
              have hsum : ∑ j ∈ Finset.range (a - b), (β * L) ^ (b + j) * (β * r)
                  = β * r * ((β * L) ^ b * ∑ j ∈ Finset.range (a - b), (β * L) ^ j) := by
                simp_rw [Finset.mul_sum, pow_add]
                refine Finset.sum_congr rfl fun j _ => ?_
                ring
              rw [hsum]
        _ ≤ β * r * ((β * L) ^ b * (1 / (1 - β * L))) :=
              mul_le_mul_of_nonneg_left
                (mul_le_mul_of_nonneg_left (hsum_le (a - b)) (pow_nonneg hq0 b)) hβr0
        _ = (β * L) ^ b * (β * r / (1 - β * L)) := by field_simp; ring
        _ < ε := hN b (by omega)
    · rw [norm_sub_rev, hsplit b a hab]
      calc ‖∑ j ∈ Finset.range (b - a), (seq (a + j + 1) - seq (a + j))‖
          ≤ ∑ j ∈ Finset.range (b - a), ‖seq (a + j + 1) - seq (a + j)‖ := norm_sum_le _ _
        _ ≤ ∑ j ∈ Finset.range (b - a), (β * L) ^ (a + j) * (β * r) :=
              Finset.sum_le_sum fun j _ => (hmain (a + j)).2 (a + j) (le_refl _)
        _ = β * r * ((β * L) ^ a * ∑ j ∈ Finset.range (b - a), (β * L) ^ j) := by
              have hsum : ∑ j ∈ Finset.range (b - a), (β * L) ^ (a + j) * (β * r)
                  = β * r * ((β * L) ^ a * ∑ j ∈ Finset.range (b - a), (β * L) ^ j) := by
                simp_rw [Finset.mul_sum, pow_add]
                refine Finset.sum_congr rfl fun j _ => ?_
                ring
              rw [hsum]
        _ ≤ β * r * ((β * L) ^ a * (1 / (1 - β * L))) :=
              mul_le_mul_of_nonneg_left
                (mul_le_mul_of_nonneg_left (hsum_le (b - a)) (pow_nonneg hq0 a)) hβr0
        _ = (β * L) ^ a * (β * r / (1 - β * L)) := by field_simp; ring
        _ < ε := hN a (by omega)
  -- the limit, its position, and the fixed-point equation
  obtain ⟨xstar, hxstar⟩ := cauchySeq_tendsto_of_complete hcauchy
  have hxpos : ‖xstar - M.x₀‖ ≤ β * r / (1 - β * L) :=
    le_of_tendsto (Filter.Tendsto.norm (hxstar.sub tendsto_const_nhds))
      (Filter.Eventually.of_forall fun m => (hmain m).1)
  have hball_x : ‖xstar - M.x₀‖ ≤ R := le_trans hxpos hR
  have hfix : xstar - inv (M.toFun xstar) = xstar := by
    have hd : Filter.Tendsto
        (fun n => (seq n - inv (M.toFun (seq n))) - (xstar - inv (M.toFun xstar)))
        atTop (nhds 0) := by
      rw [tendsto_zero_iff_norm_tendsto_zero]
      have hle : ∀ n : ℕ, ‖(seq n - inv (M.toFun (seq n))) - (xstar - inv (M.toFun xstar))‖
          ≤ β * L * ‖seq n - xstar‖ :=
        fun n => hcontr _ _ (le_trans (hmain n).1 hR) hball_x
      have hnorm : Filter.Tendsto (fun n => ‖seq n - xstar‖) atTop (nhds 0) := by
        have hsub : Filter.Tendsto (fun n => seq n - xstar) atTop (nhds (xstar - xstar)) :=
          hxstar.sub tendsto_const_nhds
        have hzz : xstar - xstar = 0 := sub_self xstar
        rw [hzz] at hsub
        have hn := hsub.norm
        rwa [norm_zero] at hn
      exact squeeze_zero (fun n => norm_nonneg _) hle
        (by simpa [mul_zero] using hnorm.const_mul (β * L))
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
  exact ⟨xstar, hzero, hball_x⟩

end Choptuik.Bridge
