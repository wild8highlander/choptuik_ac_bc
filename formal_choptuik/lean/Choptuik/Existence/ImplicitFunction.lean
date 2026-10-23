/-
╔══════════════════════════════════════════════════════════════════════╗
║   FORMAL CHOPTUIK · Choptuik.Existence.ImplicitFunction               ║
║   The implicit function theorem route to the existence proof (G1)     ║
╠══════════════════════════════════════════════════════════════════════╣
║   Reiterer–Trubowitz prove existence of the critical solution by      ║
║   Newton's method in a Banach space of sequences with exponential     ║
║   decay: the residual map Φ vanishes at a small correction of the     ║
║   numeric profile because DΦ is an isomorphism (compact inverse).     ║
║   This module fixes the interface of that argument.  The mathlib      ║
║   anchors are `HasFDerivAt`, `ContinuousLinearEquiv` and the          ║
║   complete normed space API.                                          ║
╠══════════════════════════════════════════════════════════════════════╣
║   status : SCAFFOLD — interface of the Phase-2 centerpiece            ║
╚══════════════════════════════════════════════════════════════════════╝
-/

import Mathlib.Tactic

namespace Choptuik.Existence

/-! ### Abstract Banach-space layer -/

/-- Two complete normed spaces (the real mathlib spelling of "Banach"
pair used by the Newton argument: `E` = unknowns with exponential decay,
`F` = residuals). -/
variable {E F : Type*} [NormedAddCommGroup E] [NormedAddCommGroup F]
  [CompleteSpace E] [CompleteSpace F]

/-- A `C¹` map between Banach spaces, with the derivative at the base
point supplied explicitly (mathlib's `HasFDerivAt` in Phase 2). -/
structure C1MapAt (E F : Type) [NormedAddCommGroup E] [NormedAddCommGroup F] where
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

/-! ### The implicit function theorem route -/

/-- **IFT route to existence — gap G1, Phase 2.**
If `Φ` is `C¹` near `x₀` with residual `Φ x₀` small and `DΦ x₀` an
isomorphism, then there is a genuine zero of `Φ` near `x₀`.  Applied to
the Newton picture above: numeric profile + small correction = exact
critical solution. -/
theorem existence_via_implicit_function
    (M : C1MapAt E F)
    (hiso : DerivIsomorphism M)
    (hsmall : ‖M.toFun M.x₀‖ < 1) :
    ∃ x : E, M.toFun x = 0 ∧ ‖x - M.x₀‖ < 1 := by
  sorry  -- G1 centerpiece: mathlib IFT + quantitative bounds, Phase 2

/-- **Stability of the conclusion under perturbation of the data** —
the quantitative form needed to absorb strict interval bounds from the
Python service (`interval_bound` endpoint) into the proof. -/
theorem existence_persists_under_perturbation
    (M M' : C1MapAt E F)
    (hiso : DerivIsomorphism M)
    (hclose : ∀ x, ‖M'.toFun x - M.toFun x‖ < 0.001) :
    (∃ x : E, M.toFun x = 0) → ∃ x' : E, M'.toFun x' = 0 := by
  sorry  -- G5/G1 bridge: quantitative IFT with interval certificates

end Choptuik.Existence
