/-
  Septinial braking satellite · C3: the symmetry-breaking cascade of the dial
  (principle P4: full symmetry is degenerate; the gap is what breaks it).
  Theorem content: among the 24 rotations of the oriented 24-cycle exactly the
  two {0, 12} preserve the antipodal gap; among the 24 reflections exactly the
  two {0, 12} do; the four survivors close into the Klein four-group (a name
  coincidence).  The orientation (P3a) keeps only the two rotations: the Z₂
  tail of the cascade 48 → 4 → 2.  Brute-force twin: scripts/check_dial_22.py
  (S6).  Zero sorry.
-/
import Mathlib

namespace Satellite.Cascade

/-- The antipodal gap (P3b): blocked slots {0, 12}. -/
def gap : Finset (Fin 24) := {0, 12}

/-- Rotation of the 24-cycle by k slots. -/
def Rot (k : Fin 24) : Fin 24 → Fin 24 := fun x => x + k

/-- Reflection x ↦ c − x of the 24-cycle. -/
def Rfl (c : Fin 24) : Fin 24 → Fin 24 :=
  fun x => ⟨(c.val + 24 - x.val) % 24, by omega⟩

/-- A map preserves the gap setwise. -/
def Preserves (f : Fin 24 → Fin 24) : Prop := ∀ x ∈ gap, f x ∈ gap

/-! ### Rotations: exactly 2 of 24 preserve the gap -/

theorem rot_preserves_iff (k : Fin 24) : Preserves (Rot k) ↔ k = 0 ∨ k = 12 := by
  constructor
  · intro h
    have h0 := h 0 (by simp [gap])
    simp only [Rot, Fin.zero_add, gap, Finset.mem_insert, Finset.mem_singleton] at h0
    exact h0
  · intro h x hx
    rcases Finset.mem_insert.mp hx with rfl | hx
    · rcases h with rfl | rfl <;> decide
    · rcases Finset.mem_singleton.mp hx with rfl
      rcases h with rfl | rfl <;> decide

/-! ### Reflections: exactly 2 of 24 preserve the gap -/

theorem refl_zero (c : Fin 24) : Rfl c 0 = c := by
  apply Fin.ext
  simp only [Rfl, Fin.val_mk]
  show (c.val + 24 - 0) % 24 = c.val
  omega

theorem refl_preserves_iff (c : Fin 24) : Preserves (Rfl c) ↔ c = 0 ∨ c = 12 := by
  constructor
  · intro h
    have h0 := h 0 (by simp [gap])
    rw [refl_zero] at h0
    simp only [gap, Finset.mem_insert, Finset.mem_singleton] at h0
    exact h0
  · intro h x hx
    rcases Finset.mem_insert.mp hx with rfl | hx
    · rw [refl_zero]; rcases h with rfl | rfl <;> decide
    · rcases Finset.mem_singleton.mp hx with rfl
      rcases h with rfl | rfl <;> decide

/-! ### The four survivors close into the Klein four-group V₄ -/

theorem rot12_rot12 : Rot 12 ∘ Rot 12 = id := by
  funext x
  apply Fin.ext
  simp only [Function.comp, Rot, Fin.val_add, Fin.val_mk, Fin.val_zero]
  show ((x.val + 12) % 24 + 12) % 24 = x.val
  omega

theorem rfl0_rfl0 : Rfl 0 ∘ Rfl 0 = id := by
  funext x
  apply Fin.ext
  simp only [Function.comp, Rfl, Fin.val_mk]
  show (0 + 24 - (0 + 24 - x.val) % 24) % 24 = x.val
  omega

theorem rfl12_rfl12 : Rfl 12 ∘ Rfl 12 = id := by
  funext x
  apply Fin.ext
  simp only [Function.comp, Rfl, Fin.val_mk]
  show (12 + 24 - (12 + 24 - x.val) % 24) % 24 = x.val
  omega

theorem rot12_rfl0 : Rot 12 ∘ Rfl 0 = Rfl 12 := by
  funext x
  apply Fin.ext
  simp only [Function.comp, Rot, Rfl, Fin.val_mk, Fin.val_add]
  show ((0 + 24 - x.val) % 24 + 12) % 24 = (12 + 24 - x.val) % 24
  omega

theorem rfl0_rot12 : Rfl 0 ∘ Rot 12 = Rfl 12 := by
  funext x
  apply Fin.ext
  simp only [Function.comp, Rot, Rfl, Fin.val_mk, Fin.val_add]
  show (0 + 24 - (x.val + 12) % 24) % 24 = (12 + 24 - x.val) % 24
  omega

/-- The two survivors of each kind commute: the punctured dial's symmetry group
is abelian (V₄ — the Klein four-group; the name is a coincidence). -/
theorem survivors_commute : Rot 12 ∘ Rfl 0 = Rfl 0 ∘ Rot 12 := by
  rw [rot12_rfl0, rfl0_rot12]

/-! ### The cascade reading (P4) -/

/-- Of the 24 rotations exactly two preserve the gap (set form). -/
theorem exactly_two_rotations :
    {k : Fin 24 | Preserves (Rot k)} = {0, 12} := by
  ext k
  simp [rot_preserves_iff]

/-- Of the 24 reflections exactly two preserve the gap (set form). -/
theorem exactly_two_reflections :
    {c : Fin 24 | Preserves (Rfl c)} = {0, 12} := by
  ext c
  simp [refl_preserves_iff]

/-- The surviving rotation swaps the two sectors: the pair {L, R} is symmetric
under rot12, but every reflection of the punctured dial reverses the cycle
order, so once the orientation is fixed (P3a) the reflections die — the Z₂
tail of the cascade.  The order-reversal content is carried by the sector-swap
theorems of Satellite.Chiral; the full 48 → 4 → 2 count is brute-forced in
scripts/check_dial_22.py (S6). -/
theorem rot12_val (x : Fin 24) : (Rot 12 x).val = (x.val + 12) % 24 := rfl

end Satellite.Cascade
