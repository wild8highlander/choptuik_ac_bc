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

import Mathlib

namespace Choptuik.Stability

open Matrix Module

/-- **The Gershgorin disc theorem.**  Every complex eigenvalue of a
square matrix lies in one of the discs:  `|λ - A i i| ≤ Σ_{j ≠ i} |A i j|`. -/
theorem gershgorin_disc {n : Type*} [Fintype n] [DecidableEq n]
    (A : Matrix n n ℂ) {lam : ℂ}
    (hlam : Module.End.HasEigenvalue (Matrix.mulVecLin A) lam) :
    ∃ i : n, Complex.abs (lam - A i i)
      ≤ ∑ j ∈ Finset.univ.erase i, Complex.abs (A i j) := by
  obtain ⟨v, ⟨hv, hvne⟩⟩ := Module.End.HasEigenvalue.exists_hasEigenvector hlam
  have hmul : A *ᵥ v = lam • v := by
    have := hv
    simpa [Matrix.mulVecLin] using this
  set i : n := Finset.univ.argmax (fun k => Complex.abs (v k))
    (Finset.univ_nonempty) with hi
  have hmax : ∀ j : n, Complex.abs (v j) ≤ Complex.abs (v i) :=
    fun j => Finset.le_argmax_of_mem (fun k => Complex.abs (v k)) (Finset.mem_univ _)
  have hvine : (0 : ℝ) < Complex.abs (v i) := by
    rcases lt_or_le (0 : ℝ) (Complex.abs (v i)) with h | h
    · exact h
    · exfalso
      have hz : v i = 0 :=
        le_antisymm (by rw [Complex.abs_zero]; exact h) (Complex.abs_nonneg _)
      have hall : v = 0 := by
        funext j
        by_contra hc
        exact absurd (hmax j) (by rw [hz, Complex.abs_zero] at *
          exact lt_irrefl 0 (Complex.abs_pos.mpr hc))
      exact hvne hall
  have hrow : (A *ᵥ v) i = ∑ j ∈ Finset.univ, A i j * v j := by
    show dotProduct (A i) v = _
    simp [Matrix.mulVec, dotProduct]
  have hsplit : ∑ j ∈ Finset.univ, A i j * v j
      = A i i * v i + ∑ j ∈ Finset.univ.erase i, A i j * v j :=
    (Finset.sum_erase_add Finset.univ (fun j => A i j * v j) i
      (Finset.mem_univ _)).symm
  have hkey : (lam - A i i) * v i = ∑ j ∈ Finset.univ.erase i, A i j * v j := by
    have h2 := congrFun hmul i
    rw [hrow, hsplit, smul_eq_mul] at h2
    have h3 : lam * v i - A i i * v i = (lam - A i i) * v i := by ring
    rw [← h3]
    linarith
  have habs : Complex.abs (lam - A i i) * Complex.abs (v i)
      ≤ ∑ j ∈ Finset.univ.erase i, Complex.abs (A i j) * Complex.abs (v i) := by
    have h1 : Complex.abs ((lam - A i i) * v i)
        ≤ ∑ j ∈ Finset.univ.erase i, Complex.abs (A i j * v j) := by
      rw [Complex.abs_mul, hkey]
      exact norm_sum_le _ _
    have h2 : ∑ j ∈ Finset.univ.erase i, Complex.abs (A i j * v j)
        ≤ ∑ j ∈ Finset.univ.erase i, Complex.abs (A i j) * Complex.abs (v i) :=
      Finset.sum_le_sum fun j _ => by
        rw [Complex.abs_mul]
        exact mul_le_mul_of_nonneg_left (hmax j) (Complex.abs_nonneg _)
    exact le_trans h1 h2
  have hfinal : Complex.abs (lam - A i i)
      ≤ ∑ j ∈ Finset.univ.erase i, Complex.abs (A i j) := by
    have h1 : Complex.abs (lam - A i i) * Complex.abs (v i)
        ≤ (∑ j ∈ Finset.univ.erase i, Complex.abs (A i j)) * Complex.abs (v i) := by
      rw [Finset.mul_sum]
      exact Finset.sum_le_sum fun j _ => mul_le_mul_of_nonneg_right
        (Complex.abs_nonneg _) (Complex.abs_nonneg (v i))
    exact le_of_mul_le_mul_right h1 hvine
  exact ⟨i, hfinal⟩
end Choptuik.Stability
