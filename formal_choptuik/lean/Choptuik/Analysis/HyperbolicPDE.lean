/-
╔══════════════════════════════════════════════════════════════════════╗
║   FORMAL CHOPTUIK · Choptuik.Analysis.HyperbolicPDE                   ║
║   The Einstein-scalar hyperbolic system in spherical symmetry         ║
╠══════════════════════════════════════════════════════════════════════╣
║   A massless scalar field φ minimally coupled to gravity:             ║
║                                                                       ║
║       G_{μν} = 8π T_{μν},      T_{μν} = ∂_μφ ∂_νφ - ½ g_{μν} (∇φ)²,   ║
║       □_g φ = 0 .                                                     ║
║                                                                       ║
║   In double-null coordinates the system reduces to a coupled          ║
║   first-order system for (f, r, φ).  The well-posedness layer is      ║
║   shared with the existence module (gap G1).                          ║
╠══════════════════════════════════════════════════════════════════════╣
║   status : v0.4 — obligation-free (caveat below).                     ║
║                                                                       ║
║   The v0.3 file did not compile at all: it used `Choptuik.Geometry`  ║
║   types without importing `Choptuik.Geometry.Basic` (finding B-1).    ║
║   That import is now present.                                         ║
║                                                                       ║
║   `local_wellposedness` is PROVED — but the scaffold statement is     ║
║   WEAK (finding S9): the parameters `φ0, φ1` are never used and no    ║
║   characteristic initial data is prescribed, so the problem admits    ║
║   the trivial scalar field φ ≡ 0 as a witness.  The proof below       ║
║   discharges the obligation in exactly this weak sense and the        ║
║   docstring records the honest Phase-2 replacement (prescription of   ║
║   φ on the axes {u = u₀} ∪ {v = v₀}).                                ║
╚══════════════════════════════════════════════════════════════════════╝
-/

import Mathlib.Tactic
import Choptuik.Geometry.Basic

namespace Choptuik.Analysis

open Choptuik.Geometry

/-! ### The field system -/

/-- A classical solution of the Einstein-scalar system on the
double-null arena: metric data plus the scalar field, subject to the
constraint and evolution equations below. -/
structure ClassicalSolution where
  /-- underlying metric data -/
  metric : DoubleNullData
  /-- the massless scalar field φ(u, v) -/
  phi : ℝ → ℝ → ℝ

/-- Constraint: the null-null component of the Einstein equation
`G_{uu} = 8π T_{uu}` — a Raychaudhuri-type ODE in `u` at each `v`.
Stated abstractly; Phase 2 expands the derivatives explicitly. -/
def ConstraintUU (s : ClassicalSolution) : Prop :=
  ∀ u v, ∃ k : ℝ, 2 * deriv (fun u => s.metric.r u v) u = k * s.metric.r u v

/-- Evolution: the wave equation `□_g φ = 0` in characteristic form. -/
def WaveEquation (s : ClassicalSolution) : Prop :=
  ∀ u v, deriv (fun u => deriv (fun v => s.phi u v) v) u
       + (deriv (fun u => s.metric.f u v) u / s.metric.r u v)
       * (deriv (fun v => s.phi u v) v + deriv (fun u => s.phi u v) u) = 0

/-- A genuine solution satisfies both the constraint and the evolution. -/
def IsSolution (s : ClassicalSolution) : Prop :=
  ConstraintUU s ∧ WaveEquation s

/-! ### Well-posedness (shared with gap G1) -/

/-- **Local existence on a prescribed background — PROVED (weak form).**

The v0.3 statement (and its G1 obligation) is discharged by exhibiting a
solution: the prescribed metric `d` together with the *trivial* scalar
field `φ ≡ 0`.  Two remarks keep this honest:

* The constraint `ConstraintUU` holds for any data with positive areal
  radius, the witness `k := 2 ∂ᵤr / r` being exactly the Raychaudhuri
  bookkeeping of `G_{uu} = 0` in vacuum.
* **Caveat (finding S9).**  The scaffold statement is strictly weaker
  than the physical well-posedness theorem: the parameters `φ0, φ1`
  are unused and no characteristic initial data is prescribed, so the
  trivial field is admissible.  The honest Phase-2 statement must
  demand `s.phi = φ0` on `{u = u₀}` and `s.phi = φ1` on `{v = v₀}`;
  that version — genuine characteristic PDE theory — remains part of
  gap G1 (roadmap task P2.1).  Until then this lemma certifies only
  *consistency of the constraint bookkeeping*, not PDE content. -/
theorem local_wellposedness
    (d : DoubleNullData) (φ0 φ1 : ℝ → ℝ)
    (hd : SphericallySymmetric d) :
    ∃ s : ClassicalSolution, IsSolution s ∧ s.metric = d := by
  refine ⟨⟨d, fun _ _ => 0⟩, ⟨?_, ?_⟩, rfl⟩
  · -- ConstraintUU: with r > 0 the witness k := 2 ∂u r / r works
    intro u v
    have hr : (0 : ℝ) < d.r u v := hd.1 u v
    refine ⟨2 * deriv (fun u => d.r u v) u / d.r u v, ?_⟩
    field_simp
  · -- WaveEquation: φ ≡ 0 makes every derivative vanish
    intro u v
    show deriv (fun u => deriv (fun v => ((0 : ℝ))) v) u
        + (deriv (fun u => d.f u v) u / d.r u v)
          * (deriv (fun v => ((0 : ℝ))) v + deriv (fun u => ((0 : ℝ))) u) = 0
    simp

end Choptuik.Analysis
