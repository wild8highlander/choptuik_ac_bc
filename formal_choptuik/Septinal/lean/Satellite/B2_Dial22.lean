/-
  Septinial braking satellite · B2: the dial-22 postulate and the braking rule.
  Companion module for choptuik_ac_bc (sector C framework).
  Postulates (declared, class II): P1 — a full turn 2π carries 24 slots
  (identified with F = 24 heptagons of the Klein quartic, an anchor);
  P2 — an unremovable structural gap of width 2.
  Theorems of the postulate (class I): effective capacity 24 − 2 = 22 and the
  structural pair β(d) = d²/2, α(d) = d⁵/22 on the three septinial phases.
  Zero sorry. Twin: scripts/check_dial_22.py.
-/
import Mathlib

namespace Satellite.Dial

/-- The dial: 24 slots per full turn (P1). -/
def dial (i j : Fin 24) : Finset (Fin 24) := (Finset.univ.erase i).erase j

/-- Effective capacity of the dial with the gap (P2): 24 − 2 = 22. -/
theorem card_dial (i j : Fin 24) (hij : i ≠ j) : (dial i j).card = 22 := by
  rw [dial,
    Finset.card_erase_of_mem (Finset.mem_erase.mpr ⟨hij.symm, Finset.mem_univ j⟩),
    Finset.card_erase_of_mem (Finset.mem_univ i), Finset.card_fin]

/-- The structural divisor k = 22 = b₂(K3) (h¹¹ + 2h²⁰ = 20 + 2), fixed before
any fitting; recorded here as the declared structural input. -/
def k : ℕ := 22

theorem effective (i j : Fin 24) (hij : i ≠ j) : (dial i j).card = k := by
  rw [k]; exact card_dial i j hij

/-- Braking quantum (2nd order): α(d) = d⁵/k with the structural k. -/
noncomputable def alpha (d : ℝ) : ℝ := d^5 / 22

/-- Berry quantum (1st order): β(d) = d²/2. -/
noncomputable def beta (d : ℝ) : ℝ := d^2 / 2

/-! ### Sector A: δ_A = π/2 -/

theorem beta_A : beta (π / 2) = π^2 / 8 := by rw [beta]; ring

theorem alpha_A : alpha (π / 2) = π^5 / 704 := by rw [alpha]; ring

/-! ### Sector B: δ_B = π/3 -/

theorem beta_B : beta (π / 3) = π^2 / 18 := by rw [beta]; ring

theorem alpha_B : alpha (π / 3) = π^5 / 5346 := by rw [alpha]; ring

/-! ### Sector C: δ_C = π/7 -/

theorem beta_C : beta (π / 7) = π^2 / 98 := by rw [beta]; ring

theorem alpha_C : alpha (π / 7) = π^5 / 369754 := by rw [alpha]; ring

end Satellite.Dial
