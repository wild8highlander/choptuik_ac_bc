/-
╔══════════════════════════════════════════════════════════════════════╗
║   FORMAL CHOPTUIK · Choptuik.Analysis.Interval                        ║
║   Interval arithmetic for strict numerical certificates (gap G5)      ║
╠══════════════════════════════════════════════════════════════════════╣
║   The computer-assisted proof of the existence of the Choptuik        ║
║   critical spacetime (Reiterer & Trubowitz) certifies its numerics    ║
║   with exact integer-arithmetic error bounds.  The Lean twin of       ║
║   that discipline is a verified interval library; this module fixes   ║
║   the interface and proves the two *soundness* laws that matter.      ║
╠══════════════════════════════════════════════════════════════════════╣
║   status : v0.4 — gap G5 CLOSED.                                      ║
║                                                                       ║
║   * `mul_sound` is PROVED (the v0.3 gap-G5 obligation is discharged   ║
║     case analysis on the two factors; milestone M1.2 is met).         ║
║   * `add_sound` is PROVED — the v0.3 "proof" did not even compile     ║
║     (linarith cannot see through the opaque `Interval.add`            ║
║     projections; the v0.4 proof unfolds the definitions first).       ║
╚══════════════════════════════════════════════════════════════════════╝
-/

import Mathlib.Tactic

namespace Choptuik.Analysis

/-! ### The interval type -/

/-- A closed real interval `[lo, hi]`. -/
structure Interval where
  /-- lower bound -/
  lo : ℝ
  /-- upper bound -/
  hi : ℝ

/-- Membership in an interval. -/
def Interval.mem (x : ℝ) (I : Interval) : Prop :=
  I.lo ≤ x ∧ x ≤ I.hi

/-- Point constructor: `[x, x]`. -/
def Interval.point (x : ℝ) : Interval := ⟨x, x⟩

/-! ### Rounded operations -/

/-- Outward-rounded addition. -/
def Interval.add (A B : Interval) : Interval := ⟨A.lo + B.lo, A.hi + B.hi⟩

/-- Outward-rounded multiplication (extremal products). -/
def Interval.mul (A B : Interval) : Interval :=
  ⟨min (min (A.lo * B.lo) (A.lo * B.hi)) (min (A.hi * B.lo) (A.hi * B.hi)),
   max (max (A.lo * B.lo) (A.lo * B.hi)) (max (A.hi * B.lo) (A.hi * B.hi))⟩

/-! ### Soundness -/

/-- **Soundness of addition** (PROVED — the definition is exact on ℝ). -/
theorem add_sound (A B : Interval) (x y : ℝ)
    (hx : Interval.mem x A) (hy : Interval.mem y B) :
    Interval.mem (x + y) (A.add B) := by
  obtain ⟨hxa, hxb⟩ := hx
  obtain ⟨hya, hyb⟩ := hy
  simp only [Interval.mem, Interval.add]
  exact ⟨by linarith, by linarith⟩

/-! ### The one-dimensional enclosures behind `mul_sound` -/

/-- For a fixed factor `t`, the products of the two bound points with `t`
enclose `x * t` whenever `x` lies between them.  (Case analysis on the
sign of `t`; monotone multiplication for `t ≥ 0`, antitone for `t ≤ 0`.) -/
private theorem bound_mul_left {a b x t : ℝ} (ha : a ≤ x) (hb : x ≤ b) :
    min (a * t) (b * t) ≤ x * t ∧ x * t ≤ max (a * t) (b * t) := by
  rcases le_or_gt 0 t with ht | ht
  · exact ⟨min_le_iff.mpr (Or.inl (mul_le_mul_of_nonneg_right ha ht)),
      le_max_iff.mpr (Or.inr (mul_le_mul_of_nonneg_right hb ht))⟩
  · exact ⟨min_le_iff.mpr (Or.inr (mul_le_mul_of_nonpos_right hb ht.le)),
      le_max_iff.mpr (Or.inl (mul_le_mul_of_nonpos_right ha ht.le))⟩

/-- For a fixed factor `x`, the products of `x` with the two bound points
enclose `x * y` whenever `y` lies between them. -/
private theorem bound_mul_right {c d x y : ℝ} (hc : c ≤ y) (hd : y ≤ d) :
    min (x * c) (x * d) ≤ x * y ∧ x * y ≤ max (x * c) (x * d) := by
  rcases le_or_gt 0 x with hx | hx
  · exact ⟨min_le_iff.mpr (Or.inl (mul_le_mul_of_nonneg_left hc hx)),
      le_max_iff.mpr (Or.inr (mul_le_mul_of_nonneg_left hd hx))⟩
  · exact ⟨min_le_iff.mpr (Or.inr (mul_le_mul_of_nonpos_left hd hx.le)),
      le_max_iff.mpr (Or.inl (mul_le_mul_of_nonpos_left hc hx.le))⟩

/-- The row-grouped and column-grouped minima of four products coincide
(min is associative and commutative). -/
private theorem min_four_comm (a b c d : ℝ) :
    min (min (a * c) (a * d)) (min (b * c) (b * d))
      = min (min (a * c) (b * c)) (min (a * d) (b * d)) := by
  rw [min_assoc, min_assoc, min_left_comm (a * d) (b * c) (b * d)]

/-- The row-grouped and column-grouped maxima of four products coincide. -/
private theorem max_four_comm (a b c d : ℝ) :
    max (max (a * c) (a * d)) (max (b * c) (b * d))
      = max (max (a * c) (b * c)) (max (a * d) (b * d)) := by
  rw [max_assoc, max_assoc, max_left_comm (a * d) (b * c) (b * d)]

/-- **Soundness of multiplication (gap G5) — PROVED.**  The extremal-product
enclosure contains every pointwise product.  Strategy: enclose `x * y`
between `x * B.lo` and `x * B.hi` (case on the sign of `x`), then enclose
each of those between the corresponding column products (case on the sign
of `B.lo` / `B.hi`), and finally regroup the four corners. -/
theorem mul_sound (A B : Interval) (x y : ℝ)
    (hx : Interval.mem x A) (hy : Interval.mem y B) :
    Interval.mem (x * y) (A.mul B) := by
  obtain ⟨hxa, hxb⟩ := hx
  obtain ⟨hya, hyb⟩ := hy
  simp only [Interval.mem, Interval.mul]
  constructor
  · -- lower bound
    have h1 := bound_mul_left (t := B.lo) hxa hxb   -- min (a·c) (b·c) ≤ x·c
    have h2 := bound_mul_left (t := B.hi) hxa hxb   -- min (a·d) (b·d) ≤ x·d
    have h3 := bound_mul_right (x := x) hya hyb   -- min (x·c) (x·d) ≤ x·y
    rw [min_four_comm]
    exact le_trans (min_le_min h1.1 h2.1) h3.1
  · -- upper bound
    have h1 := bound_mul_left (t := B.lo) hxa hxb
    have h2 := bound_mul_left (t := B.hi) hxa hxb
    have h3 := bound_mul_right (x := x) hya hyb
    rw [max_four_comm]
    exact le_trans h3.2 (max_le (le_max_of_le_left h1.2) (le_max_of_le_right h2.2))

/-- **The certificate principle**: if a claim `P z` holds for all `z` in an
enclosure `I` and the true value lies in `I`, then `P` holds of the true
value.  Trivial logically — but it is exactly the bridge between
numerics and proof that the Python service relies on. -/
theorem certificate_principle {P : ℝ → Prop}
    (I : Interval) (hI : ∀ z, Interval.mem z I → P z)
    (x : ℝ) (hx : Interval.mem x I) :
    P x :=
  hI x hx

end Choptuik.Analysis
