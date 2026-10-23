/-
╔══════════════════════════════════════════════════════════════════════╗
║   FORMAL CHOPTUIK · bridge/examples/LeanClient.lean                   ║
║   Illustrative Lean-side client of the numerical service              ║
╠══════════════════════════════════════════════════════════════════════╣
║   This file sketches how the Lean theory layer calls the Python       ║
║   numerical service through the bridge protocol:                      ║
║                                                                       ║
║     Lean 4 ──FFI (C ABI)──▶ ZeroMQ client ──tcp──▶ choptuik-service   ║
║                                                                       ║
║   It is an ILLUSTRATION of the integration pattern (see               ║
║   fraware/lean-python-bridge for a production ZeroMQ harness).        ║
║   Types are simplified; the Phase-1 milestone P1.5 hardens this       ║
║   into a typed client whose results feed the implicit function        ║
║   theorem of Choptuik.Existence.ImplicitFunction.                     ║
╚══════════════════════════════════════════════════════════════════════╝
-/

namespace Choptuik.Bridge.Example

/-! ### Request types (mirror of bridge/protocol.md) -/

/-- A bridge request, as a tagged value. -/
inductive Request where
  | ping
  | spectrum (nDecaying : Nat)
  | scalingFit (deltaP mass : List Float)
  | echoPeriod (tau amplitude : List Float)
  | evolve (seed : Nat) (taus : List Float)
  | intervalBound (coefficients : List Float) (lo hi : Float)

/-- A bridge response, as a tagged value. -/
inductive Response where
  | ok (payload : String)          -- raw JSON; typed views land in Phase 1
  | err (code message : String)

/-! ### Client-side contract -/

/-- One lock-step exchange over the REQ socket.  The FFI import is the
only trust boundary the Lean side adds; everything above it is typed. -/
axiom exchange : Request → IO Response

/-- Round-trip sanity: `ping` must answer with the protocol version. -/
axiom pingSucceeds : IO Bool

/-! ### How the theory consumes the service -/

/-- Sketch of the Phase-2 usage: the numeric profile from `evolve` is
packaged as the approximate solution around which the implicit function
theorem of `Choptuik.Existence` is applied. -/
def useServiceForExistence : IO String := do
  let rep ← exchange (.evolve 1993 [0.0, 0.5, 1.0])
  match rep with
  | .ok payload => pure s!"numeric seed received: {payload.take 64}…"
  | .err c m    => pure s!"service error [{c}]: {m}"

/-! ### Honesty note -/

-- The `axiom` declarations above are IO-side contracts of the scaffold.
-- They are confined to this example module and MUST NOT leak into
-- Choptuik.* theory modules: the proof layer only ever consumes
-- interval certificates, never raw floats.

end Choptuik.Bridge.Example
