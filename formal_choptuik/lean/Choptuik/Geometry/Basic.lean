/-
╔══════════════════════════════════════════════════════════════════════╗
║   FORMAL CHOPTUIK · Choptuik.Geometry.Basic                           ║
║   Spherical symmetry and the double-null arena of critical collapse   ║
╠══════════════════════════════════════════════════════════════════════╣
║   The critical solution of Choptuik lives on a spherically            ║
║   symmetric spacetime written in double-null coordinates              ║
║                                                                       ║
║       ds² = -e^{2f(u,v)} du dv + r(u,v)² dΩ² ,                        ║
║                                                                       ║
║   with u, v null coordinates and r the areal radius.  This module     ║
║   fixes the geometric arena used by every later module.               ║
╠══════════════════════════════════════════════════════════════════════╣
║   status : SCAFFOLD — signatures stable, proofs pending               ║
╚══════════════════════════════════════════════════════════════════════╝
-/

import Mathlib.Tactic

/-- The `Choptuik` namespace: every artifact of the formalization lives here. -/
namespace Choptuik.Geometry

/-! ### The double-null arena -/

/-- Double-null metric data: conformal factor `f` and areal radius `r`
as functions of the null coordinates `(u, v)`. -/
structure DoubleNullData where
  /-- conformal factor of the `du dv` term -/
  f : ℝ → ℝ → ℝ
  /-- areal radius (area of the symmetry sphere is 4π r²) -/
  r : ℝ → ℝ → ℝ

/-- The areal radius is strictly positive away from the axis of symmetry. -/
def ArealPositive (d : DoubleNullData) : Prop :=
  ∀ u v, d.r u v > 0

/-- Regularity assumption used throughout: the metric data are smooth.
The full formalization will use mathlib's `ContDiff ℝ ∞` on product spaces. -/
def SmoothData (d : DoubleNullData) : Prop :=
  ContDiff ℝ 3 d.f ∧ ContDiff ℝ 3 d.r

/-! ### Spherical symmetry -/

/-- Spherical symmetry package: positive areal radius plus smoothness.
A later layer (roadmap task P1.3) will replace this by an honest SO(3)
action and a reduction lemma to the `(u, v)` sector. -/
def SphericallySymmetric (d : DoubleNullData) : Prop :=
  ArealPositive d ∧ SmoothData d

/-! ### The mass aspect function -/

/-- Hawley-type mass aspect `m(u,v) := r/2 (1 + 2 ∂u∂v r - 2 ∂u r ∂v r)` —
the quantity whose nonzero limit encloses a black hole.  Defined here as
an abstract functional so the scaling module can state the mass scaling
law without depending on a differentiated metric calculus. -/
structure MassAspect where
  /-- value of the mass aspect on the arena -/
  m : DoubleNullData → ℝ → ℝ → ℝ

/-- A black hole has formed at advance `v` iff the mass aspect has a
strictly positive limit on future null infinity of that slice. -/
def BlackHoleFormed (M : MassAspect) (d : DoubleNullData) (v : ℝ) : Prop :=
  ∃ m₀ > 0, Tendsto (fun u => M.m d u v) atTop (nhds m₀)

end Choptuik.Geometry
