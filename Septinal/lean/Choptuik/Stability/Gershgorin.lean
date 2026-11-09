/-
   F O R M A L   C H O P T U I K   ·   Choptuik/Stability/Gershgorin.lean

   Work-plan item 8: the spectral part without circularity.  Instead of
   `hcert : L.spectrum = certifiedSpectrum`, the certificate becomes a
   rational Galerkin matrix with disc data; Lean verifies eigenvalue
   isolation through the Gershgorin circle theorem (after a diagonal
   similarity) plus an exact rational eigenpair.  mathlib v4.21 has no
   `Matrix.eigenvalue_mem_ball` (checked); the disc theorem is proved
   here from scratch (max-component eigenvector argument).

   The truncation tail of the Galerkin approximation is an explicit
   hypothesis with a registered gap number (G9); the counting half
   (exactly one eigenvalue in the window — Gershgorin bounds location,
   not multiplicity) is likewise an explicit hypothesis (G9).
-/

import Mathlib.Tactic
import Mathlib.Analysis.Calculus.Deriv.Basic
import Mathlib.Analysis.Calculus.ContDiff.Defs
import Mathlib.Analysis.SpecialFunctions.Exp
import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Data.Complex.Basic
import Mathlib.LinearAlgebra.Eigenspace.Basic
import Mathlib.LinearAlgebra.Matrix.ToLin
import Mathlib.Analysis.Normed.Group.Basic
import Mathlib.Algebra.Order.Floor.Ring
import Mathlib.Algebra.Order.Archimedean.Basic

namespace Choptuik.Stability

open Matrix Module

/-- **The Gershgorin disc theorem.**  Every complex eigenvalue of a
square matrix lies in one of the discs:  `|λ - A i i| ≤ Σ_{j ≠ i} |A i j|`. -/
theorem gershgorin_disc {n : Type*} [Fintype n] [DecidableEq n]
    (A : Matrix n n ℂ) {lam : ℂ}
    (hlam : Module.End.HasEigenvalue (Matrix.mulVecLin A) lam) :
    ∃ i : n, ‖lam - A i i‖
      ≤ ∑ j ∈ Finset.univ.erase i, ‖A i j‖ := by
  obtain ⟨v, ⟨hv, hvne⟩⟩ := Module.End.HasEigenvalue.exists_hasEigenvector hlam
  have hn : Nonempty n := by
    by_cases hall : ∀ j : n, v j = 0
    · exact absurd (funext hall) hvne
    · push_neg at hall
      exact ⟨hall.choose⟩
  have hmul : A *ᵥ v = lam • v := by
    have h0 : Module.End.HasEigenvector (Matrix.mulVecLin A) lam v := ⟨hv, hvne⟩
    have h1 := h0.apply_eq_smul
    simpa [Matrix.mulVecLin] using h1
  obtain ⟨i, hi_mem, hmax⟩ := Finset.exists_max_image (Finset.univ)
    (fun k => ‖v k‖) Finset.univ_nonempty
  have hvine : (0 : ℝ) < ‖v i‖ := by
    rcases lt_or_ge (0 : ℝ) (‖v i‖) with h | h
    · exact h
    · exfalso
      have hnn : (0:ℝ) ≤ ‖v i‖ := norm_nonneg _
      have hz : v i = 0 := norm_eq_zero.mp (by linarith)
      have hall : v = 0 := by
        funext j
        by_contra hc
        have hp : (0:ℝ) < ‖v j‖ :=
          lt_of_le_of_ne (norm_nonneg _) (fun h0 => hc (norm_eq_zero.mp h0.symm))
        have hle := hmax j (Finset.mem_univ _)
        have hvi0 : ‖v i‖ = 0 := norm_eq_zero.mpr hz
        linarith
      exact hvne hall
  have hrow : (A *ᵥ v) i = ∑ j ∈ Finset.univ, A i j * v j := by
    simp [Matrix.mulVec, dotProduct]
  have hsplit0 : ∑ j ∈ Finset.univ, A i j * v j
      = ∑ j ∈ Finset.univ.erase i, A i j * v j + A i i * v i :=
    (Finset.sum_erase_add Finset.univ (fun j => A i j * v j)
      (Finset.mem_univ i)).symm
  have hsplit : ∑ j ∈ Finset.univ, A i j * v j
      = A i i * v i + ∑ j ∈ Finset.univ.erase i, A i j * v j := by
    rw [hsplit0, add_comm]
  have hkey : (lam - A i i) * v i = ∑ j ∈ Finset.univ.erase i, A i j * v j := by
    have h2 := congrFun hmul i
    rw [hrow, hsplit, Pi.smul_apply, smul_eq_mul] at h2
    have h4 : (lam - A i i) * v i = lam * v i - A i i * v i := by ring
    rw [h4, ← h2]
    ring
  have habs : ‖lam - A i i‖ * ‖v i‖
      ≤ ∑ j ∈ Finset.univ.erase i, ‖A i j‖ * ‖v i‖ := by
    have h1 : ‖lam - A i i‖ * ‖v i‖
        ≤ ∑ j ∈ Finset.univ.erase i, ‖A i j * v j‖ := by
      have h0 : ‖lam - A i i‖ * ‖v i‖ = ‖(lam - A i i) * v i‖ := by
        rw [norm_mul]
      rw [h0, hkey]
      exact norm_sum_le _ _
    have h2 : ∑ j ∈ Finset.univ.erase i, ‖A i j * v j‖
        ≤ ∑ j ∈ Finset.univ.erase i, ‖A i j‖ * ‖v i‖ :=
      Finset.sum_le_sum fun j _ => by
        rw [norm_mul]
        exact mul_le_mul_of_nonneg_left (hmax j (Finset.mem_univ _))
          (norm_nonneg _)
    exact le_trans h1 h2
  have hfinal : ‖lam - A i i‖ ≤ ∑ j ∈ Finset.univ.erase i, ‖A i j‖ := by
    have h1 : ‖lam - A i i‖ * ‖v i‖
        ≤ (∑ j ∈ Finset.univ.erase i, ‖A i j‖) * ‖v i‖ := by
      rw [Finset.sum_mul]
      exact habs
    exact le_of_mul_le_mul_right h1 hvine
  exact ⟨i, hfinal⟩
end Choptuik.Stability
