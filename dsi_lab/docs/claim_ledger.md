# Claim ledger — DSI laboratory

Every surface claim of the package, its status, and the address of the
evidence. Statuses: **proved** (exact), **verified** (machine-precision,
seeded), **refuted** (kept as honest negative), **hypothesis** (labeled
assumption), **open** (no claim made).

| # | claim | status | evidence |
|---|-------|--------|----------|
| 1 | Sharp trace theorem: F ≥ 5n/7, e ≥ 5/7 for all n | proved + verified | `exp1_sh3.json` `theorem_big_n` (gap ≤ 5.92e-8, n = 7..12); Lean `scaled_permutation_minimum` |
| 2 | Scaled-permutation defect 7t² − 8t + 3, minimum exactly 5/7 at t = 4/7 | proved | Lean `scaled_permutation_minimum`; `exp1_sh3.json` `permutations.scaled_1p` |
| 3 | Two-parameter scalar family reproduces h(u,v) at a = b = √(4/7) | verified | `exp1_sh3.json` `permutations.scaled_2p` |
| 4 | Trimmed Kunz tree: F = n + 2 exactly (k = 2..10) | proved + verified | `exp1_sh3.json` `tree.truncation`; `exp7_e1_threshold.json` `theorem_B.tree` |
| 5 | Weighted tree: `F = (n−1)[(c₁²−1)² + (c₂²−1)²] + n + 2`; no weighting beats the trim | proved + verified | `exp1_sh3.json` `tree.weighted`; Lean `weighted_tree_549_49` |
| 6 | Theorem A: partial isometries ⇒ e ≥ 1 (identity F = 3n−2p−2q+3r at 5.9e-16) | proved + verified | `exp7_e1_threshold.json` `theorem_A`; Lean axiom-anchored |
| 7 | Theorem B: projections with P+Q ≤ I ⇒ F = n + 2·rank(I−P−Q) | proved + verified | `exp7_e1_threshold.json` `theorem_B` |
| 8 | Theorem C: unitary pairs ⇒ F = 2n exactly | proved + verified | `exp7_e1_threshold.json` `theorem_C` |
| 9 | Corollary D: inf e = 1 on the class; 5/7 unreachable; Ш.3(iii) dead for isometric transports | proved | derived from #6; Lean `corollary_D_class_closure` |
| 10 | Sofic √ε-law (e → 0 like C·ε^{1/2}) | **refuted** | `exp1_sh3.json` `hamming` (defect flat in ε) |
| 11 | DSI-4: c_K3 = 27/672 = 9/224 within +0.0025 % of the measured value | verified observation | `exp2_dsi4.json` `arithmetic` |
| 12 | 9/224 is a convergent of CF(c_K3), rank #1 exclusivity for q ≤ 2000 | verified | `exp2_dsi4.json` `convergents` |
| 13 | Census uniqueness: 9/224 unique among 7-smooth denominators in budget | proved + verified | `exp6_census_224.json` `census_filter`; Lean CF layer |
| 14 | {7,3} census: V=56, E=84, F=24, 7F=3V=2E=168, χ = −4 | proved | `exp6_census_224.json` `census`; Lean `census_*` (sorry-free) |
| 15 | Degeneracy theorem: branches I/II coincide only at g = 3; branch III separates at g = 7 | proved | `exp6_census_224.json` `genus` |
| 16 | Finding D1: repo row (g=14, n=11) impossible; corrected group PSL(2,13); Δ_Ch(π/13) = 3.3672 | proved (correction) | `exp3_hurwitz.json` `repo_audit`, `tower`, `curve` |
| 17 | Corrected Hurwitz tower passes 84(g−1)=\|G\|, n\|\|G\|, hyperbolicity | verified | `exp3_hurwitz.json` `tower.checks` |
| 18 | b₂ pattern (2b+2) on non-Klein Hurwitz surfaces | **hypothesis** | labeled in `exp3_hurwitz.json` `framework` |
| 19 | QNM catalogue: 10 events; overtone detectability 0.84σ at Cosmic Explorer | verified | `exp4_qnm.json` `catalog`, `predictions` |
| 20 | Falsifiable law: \|Δf_n\|/f_n = 8.3857e-5 | verified, falsifiable | `exp4_qnm.json` `overtones` |
| 21 | Finding E1: tr(Q_K3 ⊕ M_F) = 32 requires centering ⟨λ⟩ | verified (correction) | `exp5_qcd.json` `nscaling.trace_core` |
| 22 | \|⟨λ⟩\| scaling ~ 1/√N with slope −0.99 on the centered tower | verified | `exp5_qcd.json` `nscaling.rows`, `slope_centered` |
| 23 | κ_T-sweep: BF(GUE) up to 1165 against Poisson | verified | `exp5_qcd.json` `kappa_sweep` |
| 24 | V_T as the T-violation model (Gaussian hermitian, scale b_C) | **hypothesis** | labeled in `exp5_qcd.json` `kappa_sweep` notes |
| 25 | DSI-4 derivation from the DSI renormalization | **open** | — |
| 26 | Ш.3(iii) via non-isometric transports | **open** | — |
| 27 | Cross-language core (10 checks) byte-identical in C/C++/JS | verified | `multilang/*/reference_output.txt` |

## Ledger discipline

A status can only move one step at a time (open → hypothesis → verified
→ proved), and a refutation never leaves the ledger — the package keeps
its falsified rows visible. If a fresh run disagrees with a committed
verdict beyond the tolerance of [`methods.md`](methods.md), the correct
action is to *add* a row (a finding), not to edit an old one.
