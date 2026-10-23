# Glossary — Critical Collapse for Proof Assistants

| Term | Meaning |
|---|---|
| **Critical collapse** | gravitational collapse of a massless scalar field exactly at the black-hole threshold parameter `p = p*` (Choptuik 1993) |
| **DSS** | *discrete self-similarity*: shifting log-time by Δ equals rescaling areal radius by `e^{-Δ}` up to amplitude `e^{κΔ}` |
| **Echoing period Δ** | the log-time period of a DSS solution; numerically `Δ ≈ ln 2 ≈ 0.693` |
| **Log time τ** | `τ = -ln(T - t)` — near-singularity time coordinate in which echoing is periodic |
| **γ (critical exponent)** | black-hole mass scaling exponent, `M_BH ∝ \|p − p*\|^γ`; `γ = 1/λ₀ ≈ 0.374` |
| **λ₀** | the unique unstable eigenvalue of the operator linearized around the critical solution |
| **Echo spacing** | imaginary parts of the perturbation family are spaced by `2π/Δ ≈ 9.06` — the spectral echo |
| **Codimension-one attractor** | the critical solution attracts all nearby evolutions except along one direction (the growing mode) |
| **Isotropic singularity** | an end where curvature invariants diverge but Weyl components stay finite — conformally compactifiable (gap G3) |
| **Mass aspect** | the double-null quantity whose nonzero limit at null infinity signals a black hole |
| **I (interval)** | closed real interval `[lo, hi]`; outward-rounded operations make enclosures *sound* (gap G5) |
| **Certificate principle** | if a property holds on an interval enclosure, it holds of any value inside it — the numerics→proof bridge |
| **Blocker gap** | a gap (G1: existence; G2: stability) without which no external claim of the programme can be machine-checked |
| **sorry (Lean)** | explicit proof placeholder; every `sorry` in `lean/Choptuik/**` is a ledger entry in `blueprint/gap_registry.csv` |
| **mathlib** | the Lean mathematical library — topology, functional analysis, manifolds; the substrate of the formalization |
| **ZeroMQ bridge** | REQ/REP JSON channel letting Lean drive the Python numerical service (see `bridge/protocol.md`) |
