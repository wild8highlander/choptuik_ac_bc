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
║   status : SCAFFOLD — interface + soundness statements (G5)           ║
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

/-- **Soundness of addition** (proved — the definition is exact on ℝ). -/
theorem add_sound (A B : Interval) (x y : ℝ)
    (hx : Interval.mem x A) (hy : Interval.mem y B) :
    Interval.mem (x + y) (A.add B) := by
  obtain ⟨hxa, hxb⟩ := hx
  obtain ⟨hya, hyb⟩ := hy
  exact ⟨by linarith, by linarith⟩

/-- **Soundness of multiplication** (gap G5, Phase 1): the extremal-product
enclosure contains every pointwise product. -/
theorem mul_sound (A B : Interval) (x y : ℝ)
    (hx : Interval.mem x A) (hy : Interval.mem y B) :
    Interval.mem (x * y) (A.mul B) := by
  sorry  -- G5: case analysis on the signs of the four corner products

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
