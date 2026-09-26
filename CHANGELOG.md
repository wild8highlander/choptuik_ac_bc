# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Author:** Ishak Khamzatovich Isaev (Исаев Исхак Хамзатович) — aslan08_05@mail.ru
**Repository:** https://github.com/wild8highlander/choptuik_ac_bc

## [2.10.0] - 2026-09-26

### Added
- **einstein_direct v11 (`sympy_spinor_corrections.py`)** — the three repo
  spinor corrections (b-C Berry `pi^2/98`, a-C braking `(pi/7)^5/22`,
  a-B `(pi/3)^5/22`) embedded into the corrected tower as channel couplings
  (C1: (k/2)rs^2, C2: (k/2)rt^2, TH: (k/2)st):
  - doors audit: SC/UV/Mdef are coupling-free (no "error" to repair);
    channel map is exact;
  - NEW machine theorems: ring consistency (C1 residuals vanish iff
    kappa_C1 = kappa_C2) and branch consistency (UV/Mdef branches share the
    positive root iff kappa_C2 = kappa_TH) — a holonomy correction is
    admissible ONLY as a uniform renormalization kappa -> kappa_hol;
    asymmetric embedding demonstrated lethal (C1 residual 0.386);
  - EXACT corrected family `tau*(kappa) = 27/(2 kappa)` with the
    holonomy-invariant station ladder (R3h = 3/2, W2h = 9, R5h = 183/40,
    M5h = -105/4, M3*/R1* = 9/2, clock 1/3) and the moving ring
    `W2h/T0h^2 = 2 kappa/3`;
  - book closure study: kappa_req = 27/(2 e^{kappa_obs}) = 1.9016; uniform
    additive Berry screening kappa = 2 - bC moves the book from -2.57% to
    +0.062% of kappa_obs(gamma_lit) (observation, convention open);
    multiplicative monograph-sign moves away (-7.43%);
  - pi/30 tests: phantom Im lambda near the ladder (2.6-3.5%), no exact
    identity; session-14 pencil protocol reproduced (4 genuine lambda = 0
    modes + 12 phantoms).
- Results: `einstein_direct/results/spinor_corrections.json`;
  README_EN section 22, README.md RU section.

## [2.2.1] - 2026-09-11

### Fixed
- **Lemma Ш.3 (i) upgraded to a sharp theorem** (in `audit_transfer/`):
  the v1.0 "one-line" proof of the floor `F ≥ n/2` contained an invalid
  estimate — the trinomial `t₁² + t₂² + (t₁+t₂+n)²` has minimum `n²/3`
  (at `t₁ = t₂ = −n/3`), not `n²/2`. Replaced by the **sharp trace
  theorem `F ≥ 5n/7` for all n** with full equality characterization
  (`X_i X_i* = (4/7)I`), proved via the identity `F = G(P,Q)`, strict
  convexity of `G` and Haar averaging; the v1.0 open question on the
  global minimum `5n/7` for `n ≥ 2` is now closed. Numerics (Python and
  Julia) re-verified: identity residual ≤ 4·10⁻¹², Haar bound never
  violated, L-BFGS minima = 5n/7 to 1.3·10⁻¹⁴.

### Added
- **Standalone article** `audit_transfer/lemma_article/
  Lemma_SH3_Ustojchivost.pdf` (RU, 10 pp.): the sharp trace theorem,
  the equality construction `√(4/7)·I`, permutation models `F = 2n`,
  and the bridge lemma Ш.3(iii) with `η(ε) = C·ε^{1/2}`; LaTeX/Tectonic
  sources included.
- **Monograph PDFs rebuilt from the corrected DOCX**:
  `Choptyuk_Monograph_RU_Final.pdf` (60 pp.) and `..._EN_Final.pdf`
  (59 pp.), ERRATA appendix included. Embedded figures are downsampled
  to 2600 px (long side) in the PDF rendering only; the DOCX sources
  remain full-resolution.
- **CI workflow** `.github/workflows/verify-audit-transfer.yml`:
  auto-runs the Python and Julia verification suites on changes to
  `audit_transfer/`, weekly and on demand; uploads JSON artifacts and
  cross-checks Python ↔ Julia (tolerance 1e-9). Existing workflows were
  not modified.
- **DSI-4 observation** (in `audit_transfer/`, documented, not claimed
  as proof): the integer combination `c_K3 = 3³/(2²·|PSL(2,7)|) =
  27/672 = 0.040178571` reproduces the measured `0.040177576` to
  **+0.0025%** — three orders of magnitude tighter than all structural
  candidates (`b_Ch(22)`: +0.82%; braking RG: +0.45%; `1/25`: −0.44%).

### Changed
- `audit_transfer/README.md`, appendix PDF (`Audit_i_Perenos_
  Prilozhenie.pdf`, 11 pp., v2.0), figures and JSON results updated to
  the sharp theorem; push scripts and PUSH_INSTRUCTIONS extended to the
  new files.

## [2.2.0] - 2026-09-11

### Added
- **`audit_transfer/` — editorial verification appendix (v1.0)**: a
  dedicated folder with a full machine verification of the framework
  (Python core + independent Julia port, stdlib only, deterministic,
  zero fitted parameters):
  - **Task 1 — Monograph audit**: corrections b-C and a-C reproduced at
    machine precision; catalog of seven typographical errors E1–E7
    (sign of A in the printed (2,3,7) matrices; the δ_C⁶/2 series member;
    two shifted-exponent labels in Table B.4.1; Bring/Bolza/torus table
    values; the V.4 δ⁵/22 column) — located by code and fixed in the
    RU monograph DOCX (+ Errata appendix), with a backup of the originals
    in `docs/monograph/_originals_backup/`.
  - **Task 2 — DSI closure of c_K3 = 0.04018**: the last empirical input
    is derived at leading order from the discrete scale invariance with
    λ = 22 = b₂(K3) as the framework's own constant
    b_Ch(22) = 1 − cos(2π/22) = 0.0405070 (+0.82%); the braking-coupled
    amplitude RG map gives b_Ch(22(1+γ)) = 0.04036 (+0.45%); the 0.8%
    residual is reproduced numerically as the finite-window systematics.
    The c_K3 caveat in `docs/qcd_bridge/choptyuk_qcd_bridge.tex` is
    upgraded accordingly.
  - **Task 3 — Stability lemma Ш.3**: the uniform trace theorem
    F(X₁,X₂) ≥ n/2 (proved); sharpness — exact construction 5n/7 with
    the n = 1 global minimum proved and L-BFGS numerics to 10⁻¹⁴;
    permutation models give F = 2n (the obstruction *increases* on the
    sofic side); the soficity→matrices bridge stated as an explicit
    lemma with universal η(ε) = C·ε^{1/2}.
- Four publication-quality figures + deterministic JSON results in
  `audit_transfer/figures/` and `audit_transfer/results/`.
- PDF appendix "Аудит и перенос" (11 pp., Russian, LaTeX/Tectonic) with
  full statements and proofs: `audit_transfer/appendix/`.

### Changed
- README.md: new "Audit & Transfer Appendix" section + project-structure
  entry (cosmetic; licence untouched).

## [2.1.0] - 2026-08-10

### Added
- **§14: Jet diffusion wake bridge** in the QCD-bridge monograph
  (`docs/monograph/qcd_bridge/choptyuk_qcd_bridge.tex`).  This new
  section closes the gap between the abstract GUE level-repulsion
  argument for $\bar\theta_{\mathrm{QCD}}$ suppression and the first
  direct experimental observation of the jet diffusion wake in PbPb
  collisions by the CMS collaboration (CMS HIN-25-012,
  arXiv:2602.19431, accepted by PRL on 25 June 2026, $>5\sigma$ in
  0--30% central collisions at $\sqrt{s_{NN}} = 5.02$ TeV).
- Python: `scripts/qcd_bridge/jet_wake_4d_psl27.py` — the
  4D-PSL(2,7)/Hg-199 mass-ratio model
  $\frac{m(k)}{m_0} = \delta_C^k e^{-a_C k} |\cos(b_C k \pi/2)|
  \ln(1+c_C k)$ producing the full scale bridge:
  - $k = 23 \to 2.15\times 10^{-9} \sim 10^{-10}$ (Strong CP)
  - $k = 28 \to 5\sigma$ CMS threshold ($28-23 = 5$)
  - $k = 45 \to 4.65\times 10^{-18}$ (quark scale, exact hit!)
  - $k = 48 = 2\cdot 24 \to$ full thermalisation
- Figure: `docs/monograph/qcd_bridge/figures/fig_jet_wake_bridge.png`
  (two-panel: full mass-ratio curve + zoom on $10^{-10}\to 10^{-18}$).
- JSON: `scripts/qcd_bridge/jet_wake_bridge_results.json` with the full
  numerical report (PSL(2,7) topology, QGP observables, special
  k-points, main claims, external references).
- Bibliography: five new entries (CMS HIN-25-012, CMS sound-speed 2024,
  Casalderrey-Solana--Shuryak--Teaney Mach cone, Son-Starinets AdS/CFT
  viscosity, PSI nEDM Hg-199).

### Verified external numbers
- CMS HIN-25-012: arXiv:2602.19431, PRL accepted 25 Jun 2026
- CMS QGP sound speed: $(c_s/c)^2 = 0.241 \pm 0.016$ (16 Feb 2024)
- $\sin^2(\pi/7) = 0.1883$ (Klein heptagon) and $\sin^2(\pi/6) = 0.2500$
  (heptagon neighbour) bracket the CMS measurement within $0.6\sigma$
  of the $\pi/6$ value.
- $|\mathrm{PSL}(2,7)| = 168 = 12 \cdot 14$ matches the dijet-pair
  count ($12 = 24/2$) against the $1i_{13/2}$ shell dimension of
  ${}^{199}\mathrm{Hg}$ ($14 = 2(2j+1)|_{j=13/2}$), the PSI nEDM
  co-magnetometer.

### Honest limitations (stated in §14)
- The parameters $a_C, b_C, c_C$ remain inputs; they are not derived
  from QCD.
- The identification $k \leftrightarrow \mathrm{PSL}(2,7)/C_7$ step is
  a discrete book-keeping device, not a continuous-time evolution.
- The $k=45 \to 10^{-18}$ match is a dimensional coincidence at the
  one-significant-digit level.
- The $5\sigma$ coincidence is conditional on the same model
  parameters; it is a bridge, not an independent prediction.
- Falsifiable prediction: the QGP sound speed should lie in the band
  $[\sin^2(\pi/7), \sin^2(\pi/6)] = [0.188, 0.250]$.  CMS measures
  $0.241 \pm 0.016$.  The next-generation sPHENIX and ALICE 3
  measurements of $(c_s/c)^2$ will sharpen this test.

### Changed
- `docs/monograph/qcd_bridge/choptyuk_qcd_bridge.tex`: +299 lines
  (new §14 with 7 subsections, 1 figure, 1 table, 5 new bibitems).
- `docs/monograph/qcd_bridge/choptyuk_qcd_bridge.pdf`: rebuilt by
  tectonic (915 KiB, compiles cleanly).
- `docs/monograph/qcd_bridge/README.md`: added new §14 description and
  the jet-wake bridge value table.
- `README.md`: added "Jet Diffusion Wake Bridge (v2.1.0)" subsection
  with the scale-bridge table and reproduce instructions.
- Project `worklog.md`: appended Task ID jet-wake-bridge with full
  provenance.

## [2.0.0] - 2026-08-08

### Added
- Enhanced monograph: full EN/RU versions (PDF + DOCX + LaTeX) with 5 new sections
  - §7: 4D spin manifold extension (conformal invariance of δ_eff, Seiberg-Witten compatibility)
  - §8: Kähler surface corrections (Dolbeault correspondence, K3 hyperkähler, I₇ elliptic fibration)
  - §9: Tyukovsky equation adaptation (δ_corr = δ₀ + δ_C²/2 − δ_C⁵/22, zero free parameters)
  - §10: Einstein GR application (QNM correction ω^corr ≈ 0.999916·ω)
  - §11: Comprehensive criticism response (stability, universality, b₂=22 uniqueness)
- Python: `enhanced_verification` module with KleinQuartic, K3Surface, QNMPredictor, TyukovskyAdapter, CriticismResponse classes
- Python: enhanced QNM properties (qnm_correction, qnm_factor, corrected_frequency) on QNMPredictor
- Python: enhanced ChoptyukFormula properties (imaginary_correction, kahler_correction, tyukovsky_correction, einstein_qnm_correction)
- Python: 5 new test methods for enhanced verification
- Julia: `enhanced_verification.jl` module with K3Surface, TyukovskyAdapter structs
- Julia: new functions (imaginary_correction, kahler_correction, tyukovsky_correction, einstein_qnm_correction, einstein_qnm_factor, corrected_qnm_frequency)
- Julia: 9 new test sets for enhanced verification
- Java: K3Surface, TyukovskyEquation, EinsteinQNMCorrection model classes
- Java: EnhancedController REST API (/api/enhanced/k3, /api/enhanced/tyukovsky, /api/enhanced/einstein-qnm, /api/enhanced/verify)
- Java: Enhanced methods on ChoptyukFormula (imaginaryCorrection, kahlerCorrection, tyukovskyCorrection, einsteinQNMCorrection)
- TypeScript/Next.js: Enhanced verification types (K3SurfaceData, TyukovskyData, EinsteinQNMData, EnhancedVerificationResult)
- TypeScript/Next.js: 10 new computation functions (imaginaryCorrection, kahlerCorrection, tyukovskyCorrectedExponent, einsteinQNMCorrection, einsteinQNMFactor, correctedQNMFrequency, b2UniquenessCheck, runEnhancedVerification, etc.)
- Next.js: New /enhanced page with K3 surface, Tyukovsky, Einstein GR, b₂ uniqueness dashboard
- Next.js: Sidebar updated with "Enhanced (4D)" navigation item
- Visualizations: 10 new publication-quality figures (2D: 3, 3D: 4, 4D: 3) at 600 DPI
  - Spinor phases diagram, QNM corrections, 64-structure heatmap
  - Braking surface γ(δ_C, k), Choptyuk invariant landscape, K3 Betti numbers, Klein quartic embedding
  - 4D spinor phase space slices, Tyukovsky phase portrait, Einstein GR QNM detectability
- Verification: enhanced_results.json with all numerical verification data
- CI: enhanced verification step in ci.yml with numerical constant validation

### Changed
- CITATION.cff version: 1.2.0 → 2.0.0
- Python pyproject.toml version: 1.1.0 → 2.0.0
- README: added Enhanced Verification section with new mathematical results
- README: updated project structure to include enhanced files

## [1.2.0] - 2026-08-07

### Added
- Python: modern `pyproject.toml` with ruff, mypy, pytest, coverage configuration
- Python: comprehensive pytest test suite (test_choptyuk.py) with 20+ tests
- Julia: test suite (runtests.jl) with Test.jl
- Jupyter notebook: interactive verification with plots (notebooks/choptyuk_verification.ipynb)
- README: Mermaid architecture diagram showing project structure
- README: Codecov badge
- CI: pytest + coverage + Codecov upload in ci.yml
- CI: Julia Pkg.test() in ci.yml
- Discussions: Welcome and Release Announcement discussions created
- CITATION.cff: updated to v1.1.0 with 2026-08-07 date
- .zenodo.json: updated to v1.1.0 with 2026 year

### Changed
- CITATION.cff version: 1.0.0 → 1.1.0
- .zenodo.json version: 1.0.0 → 1.1.0

### Fixed
- Scorecard workflow: moved `id-token: write` from top-level to job-level permissions
- Scorecard workflow: fixed `permissions: read-all` as top-level default
- README: removed duplicate DOI badge
- README: updated Zenodo DOI badge with placeholder for actual DOI

## [1.1.0] - 2026-08-07

### Changed
- License changed from MIT to Isaev Proprietary License
- Full authorship retention and attribution requirements
- Commercial use and redistribution prohibited without written permission

### Fixed
- Julia Project.toml: removed deprecated [targets] section
- Java SimulationService: added missing java.time.Instant import
- Java PlotService: fixed ambiguous List import (java.awt.List vs java.util.List)
- Python: fixed 157+ ruff linting errors (style, imports, type hints)
- CI workflow: generated package-lock.json for npm caching
- Greeting workflow: fixed actions/first-interaction version compatibility
- Labeler workflow: added required enable-versioned-regex input
- DOI badge: updated from pending placeholder to Zenodo search link
- License badge: changed from MIT to Isaev Proprietary

## [1.0.0] - 2024-01-01

### Added
- Complete verification of all monograph results
- Python implementation with interactive CLI menu
- Julia implementation with interactive REPL menu
- Java Spring Boot web application with REST API
- Next.js interactive visualization dashboard
- Multi-format report generation (DOCX, PDF, TXT, MD, CSV, HTML, JSON)
- High-resolution plot generation (600 DPI PNG + PDF/SVG)
- 64 spinor structure enumeration and analysis
- Bolza, Bring, and Macbeath surface comparisons
- LIGO/Virgo QNM predictions for GW150914, GW170104, GW170814, GW190521
- Custom hypothesis testing configuration
- Arbitrary-precision parameter customization
- Complete execution logging in all reports
- CI/CD pipeline with GitHub Actions
- Original monograph documents (EN/RU, DOCX/PDF)

## [2.3.0] - 2026-09-25 (einstein_direct v5)

### Added
- **Machine-derived center hierarchy** (`einstein_direct/sympy_center.py`):
  Taylor/spinor (even-odd) expansion of the regular center in double-null
  coordinates with center drift chi; center ODEs O1-O5 + gauge relation
  derived and machine-verified by SymPy (incl. two corrections to the hand
  derivation: +W2 in O3, factor 2 in O5); numeric verification of the
  measurement pipeline (Heun residuals O2 1.1e-3, O1 2.8e-2).
- **Central Taylor patch v5** (`solver.py`, closure="taylor"): ODE-evolved
  internal boundary data t0/d0 (Choptuik-1993 style), offset-aware projection
  of the even (p+q) parasite (the E-mode explosion source), full-radius zone
  (factor-2 cell fix), sanitized ring fits, center-outward t-march on zoom
  stages, closure dispatch in both march modes.
- **Zoom campaign v5** (`zoom_campaign_v5.py`): eps ladder with post-processed
  M(eps) and gamma fit; honest verdicts. Depth record z = 7.19 (chaos-sensitive;
  single-thread BLAS required); percent-level gamma/Delta still NOT achieved —
  the wall moved outside the patch zone (mirror-parity breaking of the raw
  march) and AH capture remains fragile (v6 roadmap documented).
- **Spinor ladder** (`spinor_ladder.py`): the pi/15, pi/30 phase ladder
  (quantum pi/30, echo = 7 quanta), mode-growth scaling fits, echo-harmonics
  fitter, numeric O1/O3 residuals along zoom chains.

## [2.5.0] - 2026-09-25 (einstein_direct v6.1: depth-wall channels closed)

### Fixed
- **The j≈19-20 death channel CLOSED (7 principled fixes, all traced to
  measured mechanisms — see einstein_direct/README_EN.md §17.1):**
  annulus t-aliasing wiring (parent mutation + discarded re-march + broken
  t-sandwich); d_edge positive-feedback cap (second derivative of
  interpolated edge data, noise ~1/dv^2, alpha^2 sign flip per row); AH
  trapping filter (|2m/r - 1| < 0.5 — no more false M_frozen ~ 1e-10 stops);
  P2 early-accept (restart-row O-fit no longer discarded; the P2 = 0
  self-lock broken); zone-rebuild gate + E0_free rate gate (no junk-pair
  injection; t0 x2/row loop blocked); cross mode t := mirror(s) (the exact
  CSS relation resolves the march/projection battle); two-sided r-ring fit
  + axis gate (the one-sided fit biased x* by ~10 du and poisoned every
  mirror pair).

### Changed
- Zoom stages end by v-exhaustion, not death: eps = 1e-2/1e-3 reach
  z = 9.10/9.35 (record; v6 died at z = 3.83). P2 unlocked: 40-181 tau-rows
  per stable run (v6: 1), z_cont up to 7.9.
- **Thorne link seen in discrete data (first time): M3/(R1 t0^2) = 0.6687
  vs exact 2/3 = 0.6667 (0.3%) at eps = 1e-2** (v6 empirical median ~ 1.6 =
  junk level); |d0*s| -> 4e-5.
- BLAS pinned to 1 thread in campaign/probe modules (reproducibility).

### Added
- `sympy_center_o6_nsolve.py` + `results/center_o6_nsolve.json`: the O6+
  fixed point built from RAW purified z-coefficients (lesson: the solved
  N-levels divide by dR1 -> poles/zoo at the fixed point). Machine-exact
  verdict: the O1-O5 subsystem derives D0*=0, P2h*=T0/3, W2h*=(4/3)tau,
  R3h*=(2/9)tau as equations (one free amplitude); UV[xi^3] forces
  T0^2 = 9/4, Mdef[xi^5] forces T0^2 = 9/16, together only trivial R3 = 0 —
  **the truncated tower has NO exact CSS fixed point; the W2/R3/P4 source
  dynamics never freezes** (the quantitative form of the +0.44 kappa
  deficit localization).
- `probe_v6_channel.py`: per-row death-tracing probe (fields, tower state,
  annulus gates, d_edge) — the debugging instrument behind §17.1.

### Honest
- **tau* NOT measured (percent level not reached):** W2/t0^2 -> 0 (target
  4/3) — the (d-c) ring signal is buried under the d-field junk floor;
  tau_row is an off-manifold proxy. Near-critical eps (3e-4, 1e-4, 3e-3)
  still die at zoom 1 (chaos-sensitive 2m/r trigger). Next cycle (v7):
  source-dynamics measurement (W2/R3/P4), near-critical branch.

## [2.4.0] - 2026-09-25 (einstein_direct v6-fundamentals)

### Added
- **Convergence and repulsion from first principles**
  (`einstein_direct/center_modes.py` -> `results/center_modes.json`,
  `figures/fig_{ru,en}/fig_modes.png`):
  - Thorne/MTW mass route, machine-verified from the Hilbert-derived system
    (residuals 0): null flux laws `m_v = -2 r^2 p t^2 / alpha^2`,
    `m_u = -2 r^2 q s^2 / alpha^2`; central mass-slope link
    `M3 = 2 R1 t0^2 / (3 (1-chi)^2)` (exact at every y); center gauge
    `(1-chi^2) R1^2 = A0` from `m(0) = 0`; hoop radius `xi_AH = sqrt(R1/(2 M3))`.
  - Log-time tower: machine reduction of the verified O1-O5 (s-purity
    O1:2, O2:1, O3:2, O5:4, O4:2); CSS fixed point closed to ONE amplitude
    parameter tau by the Thorne link (without it - two free moduli).
  - Exact spectrum of the closed tower: `{0, -1, -1, -2, -3}` at tau->0
    (integer convergence exponents of the stable modes); exactly one growing
    root `lambda+(tau)` in the codim-1 window `0 < tau <= 27/80` (exact:
    `char(0,tau) = 8 tau (80 tau - 27)/27`); `lambda+(27/80) = 1.5091`;
    exact point `lambda+ = 2 at tau = 1/2` (`char(2) ~ (2 tau - 1)(8 tau - 45)`);
    second growing mode beyond 27/80 (the blow-up channel).
  - Anchors (no fitting): kappa_obs = Delta_sp/gamma = 1.947 (b_Ch) / 1.960
    (gamma_lit) vs lambda+(27/80) = 1.509 -> deficit +0.44..+0.45 in kappa =
    the quantitative contribution required from the deeper tower levels (O6+)
    for percent-level gamma.
  - Empirics: the Thorne link as a strict center-quality metric on regular
    runs (M3/M3_pred ~ 1.6 median = the xi-junk/1/r-mode level in m);
    xi_AH (hoop) median 4.83 on the v5 chain (O(1) in xi-units, as CSS
    predicts); honest t0-transient diagnostics after zoom restarts.

## [2.6.0] - 2026-09-26 (einstein_direct v8: the Poincare hexagonal transformation cycle)

### Added
- `sympy_hexcycle.py` + `results/hexcycle.json`: the dynamical answer to the
  O6 incompatibility verdict (UV[xi^3] -> T0^2 = 9/4 vs Mdef[xi^5] ->
  T0^2 = 9/16): a six-station transformation cycle (pyramid -> cone ->
  truncated cone -> parabolic pivot -> bowl -> log closure -> pyramid) on a
  C6 shape dial, driven by the Poincare quasi-velocity equations;
  15/15 symbolic identities verified (branch squares, hexagon geometry,
  both books).
- Two books of the cycle: the amplitude book kappa_cyc = ln(64/9) = 1.9617
  (+0.085% vs the kappa_obs anchor; the tower deficit +0.451 filled to
  100.4%); the echo clock Delta_cyc = 6 ln(16/9) = 12 ln(4/3) =
  24 ln(2/sqrt3) = 3.4522 (inside Choptuik's 3.44 +/- 0.02 corridor).
- Exact hexagon geometry: the ring step 4/3 = (2/sqrt3)^2 = 1/sqrt(tau5);
  gamma_cyc = Delta_sp/kappa_cyc = 0.3737 (-0.085% vs 0.374).
- Limit cycle = DSS: the return map lands on the pyramid exactly (max-norm
  error 0); the scale drops by e^Delta ~ 31.6 per cycle — a structural
  explanation of why Choptuik observed discrete, not continuous,
  self-similarity.
- `hexcycle_figures.py`: RU/EN figures, 300 dpi (wheel, dynamics, honest
  closure); reports `hexcycle_report_ru.pdf` / `hexcycle_report_en.pdf`
  (tectonic, zero overfull).
- README_EN section 18; RU README v8 section.

## [2.7.0] - 2026-09-26 (einstein_direct v8-campaign: checking kappa = ln(64/9) and W2/t0^2 -> 4/3)

### Fixed
- **Clock bug of v5-v6.1 found and pinned** (`solver.py`, flag
  `tay_ode_fix`): `tay["v_prev"]` was overwritten in the chi section
  BEFORE `dv_ode` was computed, so `dv_ode == 0` after the first row of
  every stage — the O1/O3 center ODEs were dead; t0/d0 lived only through
  the relax channels. This is the mechanical cause of the frozen tau book
  of the v6.1 campaign (tau* = 3.3e-20, lambda_drift pinned at the grid
  edge). Legacy behavior preserved bit-for-bit (flag default off;
  z = 9.10/9.35 reproduced exactly). The blind pred branch of O1 is now
  data-gated in the fixed mode (three runaway mechanisms documented:
  blind ODE with self-referential P2; Riccati clock s'=-1 in stage-v;
  width clock).

### Added
- **Measurement instrumentation** (`_tay_diag_v8`): raw pre-gate fits per
  row (W2_raw + gate reason, P2_raw, d0_field, dc-pair, dv_ode, t0/d0
  branch tags). The E/O gate freeze mechanics identified: the max-res
  metric is crushed by the zone-edge dynamic range (~1000), so the gates
  fail on essentially all deep rows and the P2/W2 relays freeze at their
  stage-1 values — the v6.1 tau book was a frozen artifact.
- **v8 campaign** (`grid_machine_v8.py`, `results/grid_machine_v8.json`):
  eps ladder {1e-4..1e-2} on the stable v6.1 dynamics + live-tower probe;
  fresh tau book tau_fresh = E0_free^4/(9 P2_raw^2) on raw fits; two
  clocks (z_cont_fresh and the geometric z_fine built from the CSS clock
  equation s'=-1 + the zoom ladder); echo fits (models A/B, nested
  least squares, bootstrap); W2 channels (raw fit, dc-pair, d0-clock,
  relay); Q-peak geometric echo.
- **Honest verdicts**: kappa = ln(64/9) — BLOCKED (the unstable-mode
  departure does not grow inside the deep window; lambda_fit at the grid
  edge; channel needs P4 dynamics and/or reliable M(eps) via AH capture,
  which still never nucleates). Delta — INDICATIVE: model B Delta =
  0.73 (-0.4% vs Delta_sp = 7pi/30 = 0.7330), model A 0.77 (+5.0%); the
  Q-peak geometric echo Delta = 1.732 +/- 0.451 (zoom-ladder clock;
  Delta_cyc/Delta_Q ~ 2.0 — the pyramid doubling of the hexcycle book,
  indicative). W2/t0^2 -> 4/3 — BLOCKED: the raw (d-c) signal sits
  ~1e13 t0^2 above the target under the d-junk floor in ALL channels
  (raw, dc-pair, d0-clock); inside the live tower W2 is enforced by the
  machine-verified CSS equation W2* = kappa t0^2 - M3*/R1 (4/3 at chi=0 —
  the hexcycle ring), the deviation is not resolvable at this floor.
- **Live-tower refusal documented** (independent confirmation of the
  O6 source-dynamics verdict, now at the dynamical level): all three
  clock closures blow up t0 within 1-2 stages (z = 3.45 vs legacy 9.10);
  the E0_free anchor is poisoned by the zone rebuild (E_zone[0] = t0).
  The center book on this grid is always series-mediated — the v5 wall
  reopened at the P4 level.
- **Figures** `fig_tau_v8` / `fig_w2_v8` (RU/EN, 300 dpi): the tau book
  with the model-B fit, the clock-mismatch regression (slope 0.71), the
  W2 floor vs the 4/3 target, the live-vs-legacy t0 record.

## [2.8.0] - 2026-09-26 (einstein_direct: P4 closure — the cycle in Einstein/Hilbert equations)

### Added
- `sympy_p4_einstein_hilbert.py` + `results/p4_einstein_hilbert.json`:
  - fresh 4D verification of the double-null Einstein-scalar system with exact
    factors (`G_uu - kappa T_uu = -(2/r) C1-form`, `G_uv = -(2/r)(UV + r(TH-st))`,
    `T_uv == 0`, Hilbert identity `nabla T = (box Phi) nabla Phi`);
  - the ring `W2h/T0h^2 = 4/3` and the clock `P2h/T0h = 1/3` DERIVED from the
    O1-O5 core (machine chain, not postulates);
  - P4-A: dynamic-source fixed points (V1 CSS-frame, V2 full, V3 prolongation);
  - P4-B: pure d-field ring parity `(d-c) = omega_xi = 2 W2 xi`, exact even-junk
    extractor, v8 dc-pair asymmetry demo (leak 0.92, odd/even 0.28).

### Fixed
- AUDIT of the session-8 O6 fixed point: `W2''/R3''/P4''/R5'` were silently zeroed
  by the z-substitution (only `P2''` had a table). With corrected adiabatic tables
  `(5 dF + 6 F)/S^(p+1)`: the UV[xi^3] and Mdef[xi^5] branches merge into a single
  root `tau* = 27/4` — the frozen CSS point EXISTS; the 9/4-vs-9/16 incompatibility
  and the `kappa_cyc = ln(64/9)` two-book construction built on it were artifacts.
  Ring `4/3`, DSS picture and v8 Delta-signals unaffected.

### Verdict
- Prolongation (O7) closes adiabatic source dynamics: only the frozen point
  `tau* = 27/4` survives (all flows 0); genuine source dynamics requires second-order
  flows — the limit cycle (DSS). `lambda+(27/4) ~ 8` (off-grid): the truncated-tower
  point is not the critical attractor by spectrum.

## [2.9.0] - 2026-09-26 (einstein_direct: v9 mirror pairs + exact spectrum at tau* + monodromy books)

### Added
- `grid_machine_v9.py` + `results/grid_machine_v9.json`:
  - `solver._mirror_probe_v9` (flag `tay_diag_v9`, measurement-only): strict
    mirror ring pairs (xi, -xi) via per-side cubic interpolation into mirror
    targets, P4-B extractor `[(d-c)(+xi)-(d-c)(-xi)]/(4 xi)`, full ring dump,
    PLUS channel B — the junk-free series `c_ser = (r_uu + (kappa/2) r s^2)/(2 p)`
    from the C1 form;
  - campaign verdict (honest): even junk is side-symmetric to 3.2e-8..3.8e-7
    and cancels EXACTLY; the odd marsh junk is chaotic (row fits res ~ 0.4-0.6)
    with a linear-in-xi component degenerate with the signal -> `W2/t0^2 -> 4/3`
    stays BLOCKED at the instrumentation level (O6+ dynamics required);
  - channel A floor `|W2_pair|/t0^2`: 1.4 (eps=1e-3) .. 2.3e+2 (eps=1e-2)
    against the 4/3 target; channel B input `R3/t0^2 ~ 1e3..1e5` (junk).
- `sympy_spectrum_tau_star.py` + `results/spectrum_tau_star.json`:
  - [S1] OLD core quintic at `tau = 27/4` (exact substitution): real roots
    `{-11.5870, -6.6349, -0.5909, +2.3994, +9.4134}` -> `lambda+_old = 9.4134160947`
    (the session-11 interpolation ~7.99 was low; an artifact of frozen sources);
  - [S2] CORRECTED tower pencil `M(lam) = J_a + lam J_v P` (18 eq on 9 amps +
    8 flows, flow->amp projection P since M5h has no flow): exact
    `char(lam) = det(M^T M) = lam^4 * Q12(lam)` via exact rational interpolation
    (25 pts, Q(sqrt 3)); real rank-drop set = {0} only; `dim ker J_a = 1`;
    ALL complex roots verified as PHANTOMS (complex-lambda SVD, full rank);
  - [S3] C1 route to the ring: `c_lin = -[(3/2)R3 + (kappa/2)R1 E0^2]/[(1+chi)R1]`,
    at CSS inputs `W2 = (4/3) t0^2` exactly — third machine route to the ring 4/3;
  - [S4] monodromy books: `kappa_book = ln(27/4) = 3 ln3 - 2 ln2 = 4 ln(3/2) +
    ln(4/3)` = 1.9095425 (-2.57% vs kappa_obs(gamma_lit)); station ladder of the
    corrected chain (`W2h/R3h = 6`, `P2h = sin(pi/3)`, `R5h = 183/40`,
    `M5h = -105/4`, `P4h = 153 sqrt(3)/10`); amplitude monodromy around the
    6-station loop = 1 EXACTLY (return to the pyramid); old books
    `ln(64/9)` / `6 ln(16/9)` marked artifacts.

### Changed
- README_EN (sections 21), README.md (v9 section).

### Verdict
- The corrected tower point `tau* = 27/4` is spectrally INERT: an isolated
  algebraic vertex of the constraint landscape, not an exponential repeller
  (the old-core `lambda+ = 9.41` was a frozen-sources artifact). The cycle
  dynamics lives in the limit cycle (DSS), not at the vertex; gamma cannot be
  derived from the point. Surviving books: ring 4/3 (three machine routes),
  DSS picture, v8 Delta-signals.
