# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Author:** Ishak Khamzatovich Isaev (Исаев Исхак Хамзатович) — aslan08_05@mail.ru
**Repository:** https://github.com/wild8highlander/choptuik_ac_bc

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
