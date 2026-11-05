/-
  Septinial braking satellite · B2b: the dial's chirality (P3).
  Companion module for choptuik_ac_bc (sector C framework).
  Postulate P3a (declared): the dial is an oriented cycle — the mirror order is
  the other chirality.  Postulate P3b (declared): the gap of 2 splits one
  blocked slot per half-turn arc: {0, 12} antipodal.
  Theorems of the postulate (class I): the chiral split 22 = 11 + 11 and the
  reflection x ↦ 24 − x swapping the sectors (chirality = the choice of
  orientation, not of counting).  Zero sorry.  Twin: scripts/check_dial_22.py.
-/
import Mathlib

namespace Satellite.Chiral

/-- Left sector: slots 1 … 11 (before the blocked slot 12). -/
def Left : Finset (Fin 24) := Finset.univ.filter fun x => 1 ≤ x.val ∧ x.val ≤ 11

/-- Right sector: slots 13 … 23 (after the blocked slot 12). -/
def Right : Finset (Fin 24) := Finset.univ.filter fun x => 13 ≤ x.val ∧ x.val ≤ 23

/-- The blocked antipodal pair (P3b). -/
def blocked : Finset (Fin 24) := Finset.univ.filter fun x => x.val = 0 ∨ x.val = 12

theorem card_left : Left.card = 11 := by decide

theorem card_right : Right.card = 11 := by decide

theorem disjoint_left_right : Disjoint Left Right := by
  rw [Finset.disjoint_left]
  rintro ⟨v, hv⟩ hxL hxR
  simp only [Left, Right, Finset.mem_filter, Finset.mem_univ] at hxL hxR
  omega

/-- The chiral split: 22 = 11 + 11 effective slots under the P3b gap. -/
theorem chiral_split : (Left ∪ Right).card = 22 := by
  rw [Finset.card_union_of_disjoint disjoint_left_right, card_left, card_right]

/-- The dial is covered by the two sectors plus the antipodal gap (P3b). -/
theorem cover : Left ∪ Right ∪ blocked = (Finset.univ : Finset (Fin 24)) := by decide

/-- The reflection x ↦ 24 − x of the oriented cycle. -/
def refl (x : Fin 24) : Fin 24 := ⟨(24 - x.val) % 24, by omega⟩

theorem refl_involutive (x : Fin 24) : refl (refl x) = x := by
  apply Fin.ext
  simp only [refl, Fin.val_mk]
  show (24 - (24 - x.val) % 24) % 24 = x.val
  omega

/-- Reflection swaps the left sector into the right one. -/
theorem refl_left_to_right : ∀ x ∈ Left, refl x ∈ Right := by
  rintro ⟨v, hv⟩ hxL
  simp only [Left, Finset.mem_filter, Finset.mem_univ, true_and] at hxL
  simp only [Right, Finset.mem_filter, Finset.mem_univ, true_and, refl, Fin.val_mk]
  omega

/-- Reflection swaps the right sector into the left one. -/
theorem refl_right_to_left : ∀ x ∈ Right, refl x ∈ Left := by
  rintro ⟨v, hv⟩ hxR
  simp only [Right, Finset.mem_filter, Finset.mem_univ, true_and] at hxR
  simp only [Left, Finset.mem_filter, Finset.mem_univ, true_and, refl, Fin.val_mk]
  omega

/-- Reflection fixes the blocked pair setwise. -/
theorem refl_blocked : ∀ x ∈ blocked, refl x ∈ blocked := by
  rintro ⟨v, hv⟩ hxb
  simp only [blocked, Finset.mem_filter, Finset.mem_univ, true_and] at hxb ⊢
  simp only [refl, Fin.val_mk]
  rcases hxb with h | h
  · left; omega
  · right; omega

/-- Chirality is the choice of orientation: the reflection is a bijection of the
dial that exchanges the two sectors, so the split 11 + 11 is orientation-
invariant as a *count*; which half is "left" is the orientation (P3a). -/
theorem refl_bijective : Function.Bijective refl :=
  Function.bijective_iff_has_inverse.mpr ⟨refl, fun x => refl_involutive x,
    fun x => refl_involutive x⟩

end Satellite.Chiral
