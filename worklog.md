# Work Log — choptuik_ac_bc Project Enhancement

---
Task ID: 1
Agent: main
Task: Set up MkDocs Material for GitHub Pages API documentation

Work Log:
- Created `docs-site/mkdocs.yml` with full Material theme configuration
- Configured MathJax 3 for LaTeX rendering, Mermaid diagram support, mkdocstrings for auto-API docs
- Created 30+ documentation pages across 5 sections: Home, Tutorials, Mathematics, API Reference, Development
- Set up navigation structure with tabs, sections, and search
- Added custom CSS for math blocks, admonitions, and verification badges
- Added `docs-site/requirements.txt` with all MkDocs dependencies
- Created `overrides/` directory for theme customization

Stage Summary:
- Full MkDocs Material documentation site ready at `docs-site/`
- Auto-generated API docs via mkdocstrings from Python docstrings
- MathJax 3 + Mermaid + Google-style docstrings configured
- Deployable via `mkdocs serve` (local) or `mike deploy` (production)

---
Task ID: 2
Agent: main
Task: Create GitHub Actions workflow for deploying MkDocs to GitHub Pages

Work Log:
- Created `.github/workflows/pages.yml` with proper permissions (contents:read, pages:write, id-token:write)
- Configured `upload-pages-artifact` + `deploy-pages` actions
- Set up concurrency group to prevent parallel deployments
- Added `workflow_dispatch` for manual rebuilds
- Trigger on pushes to main affecting `docs-site/` or `python/src/`

Stage Summary:
- `pages.yml` workflow deploys MkDocs to https://wild8highlander.github.io/choptuik_ac_bc/
- Proper GitHub Pages deployment with artifact upload pattern

---
Task ID: 3
Agent: main
Task: Configure Codecov for real coverage reporting

Work Log:
- Created `codecov.yml` with project/patch status thresholds (80% target)
- Configured component management: core, verification, simulation, visualization, reporting
- Added `CODECOV_TOKEN` secret reference in CI workflow
- Updated `ci.yml` with `codecov/codecov-action@v4` upload step
- Coverage runs on ubuntu-latest + Python 3.12 only (primary matrix cell)
- Added `make coverage` target to Makefile

Stage Summary:
- Codecov integration with component-level coverage tracking
- Coverage XML uploaded to Codecov on every push to main and every PR
- 80% coverage threshold enforced

---
Task ID: 4
Agent: main
Task: Add sigstore signing for release artifacts

Work Log:
- Added `sign` job to `.github/workflows/release.yml`
- Uses `id-token: write` permission for OIDC-based signing
- Signs all artifacts in `dist/` with `sigstore sign --bundle`
- Creates `.sigstore` bundle files for verification
- Added verification instructions in release body
- Added `make sign-release` target to Makefile

Stage Summary:
- Release artifacts are signed with sigstore (keyless, OIDC-based)
- `.sigstore` bundles uploaded as release assets
- Verification command provided in release notes

---
Task ID: 5
Agent: main
Task: Create GitHub Release workflow for v2.0.0

Work Log:
- Created `.github/workflows/release.yml` triggered on `v*` tags
- Jobs: build → test → sign → release → deploy-docs
- Build: creates sdist + wheel, verifies with twine
- Test: full test suite + verification before release
- Sign: sigstore signing of all distribution artifacts
- Release: creates GitHub Release with auto-extracted changelog notes
- Deploy-docs: deploys versioned documentation via mike
- Fixed version sync: `src/__init__.py` 1.0.0 → 2.0.0, `setup.py` 1.0.0 → 2.0.0

Stage Summary:
- Complete release pipeline: build → test → sign → release → docs deploy
- Tag `v2.0.0` triggers the full release workflow
- Version numbers synchronized across all files

---
Task ID: 6
Agent: main
Task: Update supporting files (Makefile, pre-commit, dependabot, issue templates)

Work Log:
- Updated Makefile with docs targets: docs-install, docs-build, docs-serve, docs-deploy, coverage, sign-release
- Created `.pre-commit-config.yaml` with ruff, mypy, prettier, markdownlint, shellcheck
- Created `.github/dependabot.yml` for pip, npm, maven, github-actions
- Created issue templates: bug_report.yml, feature_request.yml, research_question.yml
- Updated clean target to include `docs-site/site`
- Added `DOCS_DIR` variable to Makefile

Stage Summary:
- Makefile now supports `make docs`, `make coverage`, `make sign-release`
- Pre-commit hooks enforce code quality on every commit
- Dependabot monitors all ecosystems weekly
- Structured issue templates for bugs, features, and research questions

---
Task ID: 7
Agent: main
Task: Extend QCD bridge research with Higgs-scale formula derivation, CP-odd observables, and falsifiable EDM predictions

Work Log:
- Audited entire repository: confirmed formula a_C * (Lambda_QCD/M_H)^(5/2) appears ONLY in the qcd_bridge monograph (not in main monograph_enhanced_ru/en.tex which focus on delta_C^5/22 ~ 1/1200)
- Created scripts/qcd_bridge/qcd_observables_with_aC.py (560 lines):
  * Inserts Choptyuk phase theta_Ch = a_C * (Lambda/M_H)^(5/2) into QCD Lagrangian
  * Computes 6 CP-odd observables: d_n, d_p, d_Hg, d_Ra, d_e, d_D
  * Propagates uncertainties via Monte Carlo (200k samples)
  * Generates 4 visualizations: observables bar chart, sphaleron derivation, exponent sensitivity, MC histograms
- Investigated 4 theoretical candidates for the 5/2 exponent:
  * (i) Cohen-Kaplan-Nelson sphaleron rate Gamma_sph(T) ~ alpha_W^5 T^4 (M_H/T)^(5/2) -> structurally gives 5/2 ✓
  * (ii) Weinberg 3-gluon operator RGE: gamma_6/(2 b_0) = 5/14, not 5/2 ✗
  * (iii) HQET anomalous dim gamma_m ~ 0.09 (one-loop) -> too small ✗
  * (iv) EW-instanton split (Lambda/M_W)^(3/2) * (M_W/M_H) -> off by 100x ✗
- Wrote v2_section.tex: 350-line LaTeX section with derivation, Choptyuk-augmented Lagrangian, predictions, Monte Carlo, falsifiability analysis
- Inserted v2 section into choptyuk_qcd_bridge.tex via \input{v2_section}
- Added 7 new bibliography entries (Cohen-Kaplan-Nelson, Pospelov-Ritz, Hoferichter, Graner, ACME, n2EDM, SNS nEDM)
- Compiled monograph: 24 pages PDF (was 18 pages), 1.0 MB
- Copied 4 new figures into docs/monograph/qcd_bridge/figures/
- Updated README.md with stage 1/stage 2 split and reproduction instructions

Stage Summary:
- KEY PREDICTION: d_n^Ch = 2.4e-16 * theta_Ch ≈ 2.0e-26 e*cm
  * This is 13% ABOVE the current nEDM@PSI bound (1.8e-26)
  * Monte Carlo: P(d_n > 1.8e-26 e*cm) = 0.54 (coin flip)
  * Within 20-100x reach of next-gen SNS nEDM (2026-2027) and n2EDM@PSI (2027-2028)
- The 5/2 exponent is now structurally motivated (not derived) by sphaleron rate scaling
- Mercury paradox: prediction exceeds Hg bound by 340x, plausibly resolved via chromo-EDM decoupling but full calculation deferred
- Falsifiable: SNS nEDM sensitivity 1e-27 e*cm will either detect the bridge at ~20 sigma or exclude it
- Updated verdict: bridge is now a "falsifiable hypothesis with partial theoretical derivation" (was: pure numerology)

---
Task ID: 8
Agent: main
Task: Continue research with directions A/B/C/D and integrate verification into existing test suite

Work Log:
- Audited existing verification patterns: enhanced_verification.py uses @dataclass with @property, verify_all() orchestrator, test_choptyuk.py with 30 tests in 6 classes
- Created python/src/core/qcd_bridge_verification.py (870 lines):
  * 7 dataclasses: ChoptyukBridge, CPoddObservable, CPoddPredictions, MercuryParadox, LatticeThetaDependence, PQAxiomWithResidual, MonteCarloUncertainty, FalsifiabilityTimeline
  * Top-level verify_all() function returns complete results dictionary
  * CLI entry point with full pretty-printing of results
- (A) Mercury paradox resolution:
  * Honest 3-tier assessment: central c_Hg = 3e-17 (paradox ratio 343),
    1-sigma uncertainty (factor 100) gives |theta| < 2.5e-11,
    aggressive (with nuclear cancellation + chromo-EDM decoupling) gives |theta| < 2.5e-10
  * Status: MARGINALLY RESOLVED (requires aggressive cancellations)
  * Honest verdict: Mercury is NOT the decisive test; nEDM is.
- (B) Lattice theta-dependence (Vicari-Panagopoulos):
  * b_2 lattice = -0.0123, b_2 large-N = -1/108 ≈ -0.00926, ratio 1.33
  * Relative correction to chi_t at theta_Ch ~ 1e-22 (unobservable)
  * theta_Ch deep within linear regime of lattice theta-dep
- (D) PQ axion with residual:
  * Modified potential V_PQ^Ch = -chi_t/2 (theta - a/f_a - theta_Ch)^2
  * Residual theta_eff = theta_Ch, axion mass unchanged
  * Residual undetectable by haloscopes, detectable by EDMs
- (C) arXiv formatting:
  * Section structure with numbered equations
  * 5 new bibliography entries (Vicari-Panagopoulos, Dmitriev-Flambaum, de Vries, nEDM 2024)
- Created abd_section.tex (320 lines) consolidating A/B/D into Section VIII
- Updated choptyuk_qcd_bridge.tex to \input{abd_section}
- Compiled monograph: 28 pages PDF (was 24), 1.05 MB
- Added 28 new tests in TestQCDBridgeVerification class
- Updated verify_all.py VerificationSuite with include_qcd_bridge flag
- Updated __init__.py with 8 new exports
- All 58 tests pass in 0.47s

Stage Summary:
- KEY HONEST RESULTS:
  * Mercury paradox: MARGINALLY RESOLVED at aggressive end of theoretical uncertainty
  * Lattice consistency: full (relative correction ~1e-22, unobservable)
  * PQ residual: clean experimental signature distinguishing Choptyuk-augmented PQ
- Verification infrastructure:
  * 870-line qcd_bridge_verification.py module mirroring enhanced_verification.py pattern
  * 28 new tests integrated into existing test_choptyuk.py
  * Full test suite: 58 tests in 0.47s
  * verify_all.py orchestrator extended with QCD bridge section
- Monograph: 28 pages, arXiv-style, 33 bibliography entries
- Files added/modified:
  * python/src/core/qcd_bridge_verification.py (NEW, 870 lines)
  * python/src/core/__init__.py (MODIFIED, +8 exports)
  * python/src/verification/verify_all.py (MODIFIED, +QCD bridge integration)
  * python/tests/test_choptyuk.py (MODIFIED, +28 tests in TestQCDBridgeVerification)
  * docs/monograph/qcd_bridge/abd_section.tex (NEW, 320 lines)
  * docs/monograph/qcd_bridge/choptyuk_qcd_bridge.tex (MODIFIED, \input{abd_section})
  * docs/monograph/qcd_bridge/choptyuk_qcd_bridge.pdf (RECOMPILED, 28 pages)
  * docs/monograph/qcd_bridge/README.md (MODIFIED, stage 3 added)

---
Task ID: 9
Agent: main
Task: Stage 4 — Wave-function bridge: a_C as axion ground state (new theoretical tool)

Work Log:
- User asked for "other tools" to solve the strong CP puzzle, hypothesizing that
  a_C might be the axion wrapped in a wave function (weak interaction, slowing
  particles, shifting energy to small values).
- Created scripts/qcd_bridge/axion_wavefunction_bridge.py (1034 lines):
  * Numerov-method Schroedinger solver for the Choptyuk-augmented PQ potential
    V(q) = 1 - cos(q + theta_bare) + theta_Ch * q (dimensionless units)
  * Solves on a single cosine well with Dirichlet BCs at the barriers (N=8001)
  * Ground state energy E_0 = 0.652 chi_t (harmonic 0.5, +30% anharmonic correction)
  * Quantum width sigma_q = 0.888 (harmonic 0.707, +25%)
  * WKB instanton splitting: S_inst = 8 (analytic), S_phys = 10^10.7
    Delta E ~ 10^-8.5 GeV (exponentially suppressed)
  * Quantum-fluctuation consistency check:
    sigma_theta^qm = sqrt(chi_t / (2 f_a^4)) ~ 10^-26.4
    theta_Ch / sigma_theta^qm ~ 2*10^16 LARGER
    ==> theta_Ch is a CLASSICAL tilt, not a quantum fluctuation
  * Hubble-friction relaxation (analytic frozen+oscillation, Wantz-Aliaga 2010):
    T_osc = sqrt(m_a M_Pl / (1.66 sqrt(g_*))) = 68.6 GeV
    theta(t) frozen for T > T_osc, oscillates for T < T_osc
    amplitude decays as (T/T_osc)^(3/2); <theta> -> theta_Ch at late times
  * Witten-Veneziano cross-check (chi_t_YM ~ (200 MeV)^4 vs chi_t_QCD ~ (76 MeV)^4)
  * 4 figures: PQ potential + psi_0, relaxation history, instanton, theta hierarchy
- Added WaveFunctionBridge dataclass to python/src/core/qcd_bridge_verification.py:
  * 8 properties: axion_mass_eV, quantum_fluctuation_sigma_theta, ratio_theta_Ch_to_sigma,
    classical_theta_eff, hubble_T_osc, instanton_action, tunneling_splitting, verdict
  * Integrated into verify_all() with summary print
- Added 9 new tests in TestQCDBridgeVerification (total 67 tests, all pass in 0.48s)
- Added WaveFunctionBridge to __init__.py exports
- Created docs/monograph/qcd_bridge/wavefunction_section.tex (210 lines, § IX):
  * Subsection on Choptyuk-augmented PQ potential
  * Quantization: axion as quantum oscillator
  * Ground-state results (table + Figure 1)
  * Consistency check: quantum fluctuations vs classical tilt
  * Hubble-friction relaxation (Figure 2)
  * WKB instanton splitting (Figure 3)
  * Hierarchy of theta scales (Figure 4)
  * Honest verdict: what the bridge does and does NOT prove
- Updated choptyuk_qcd_bridge.tex to \input{wavefunction_section}
- Added 5 new bibliography entries (BMW 2015, DFSZ 1981, Wantz-Aliaga 2010,
  Hiramatsu 2012, Witten 1979)
- Compiled monograph: 34 pages PDF (was 28), 1.28 MB
- Copied 4 new figures into docs/monograph/qcd_bridge/figures/
- Updated README.md with Stage 4 description and 67-test count

Stage Summary:
- KEY FINDING: theta_Ch ~ 10^-10 is a CLASSICAL tilt of the PQ potential,
  NOT a quantum fluctuation.  Quantum zero-point fluctuations are ~10^16
  times smaller (sigma_theta ~ 10^-26).
- The physical "slowing" mechanism the user identified is Hubble-friction
  relaxation: the damping term 3H dot theta in the cosmological axion
  equation converts kinetic energy into cosmic expansion, relaxing theta
  to the Choptyuk-shifted minimum theta_Ch.
- The axion is a classical coherent field at f_a = 1e12 GeV (tunneling
  splitting ~10^-8.5 GeV, exponentially suppressed vs E_0 ~ 10^-5 GeV).
- Honest caveat: the wave-function analysis does NOT derive the 5/2
  exponent; it only confirms consistency IF the Higgs-bridge tilt is accepted.
- Files added/modified:
  * scripts/qcd_bridge/axion_wavefunction_bridge.py (NEW, 1034 lines)
  * scripts/qcd_bridge/figures_v3/ (NEW, 4 PNG figures)
  * scripts/qcd_bridge/wavefunction_bridge_results.json (NEW)
  * python/src/core/qcd_bridge_verification.py (MODIFIED, +WaveFunctionBridge, ~100 lines)
  * python/src/core/__init__.py (MODIFIED, +WaveFunctionBridge export)
  * python/tests/test_choptyuk.py (MODIFIED, +9 tests, total 67)
  * docs/monograph/qcd_bridge/wavefunction_section.tex (NEW, 210 lines)
  * docs/monograph/qcd_bridge/choptyuk_qcd_bridge.tex (MODIFIED, +\input{wavefunction_section}, +5 bib)
  * docs/monograph/qcd_bridge/choptyuk_qcd_bridge.pdf (RECOMPILED, 34 pages)
  * docs/monograph/qcd_bridge/figures/ (4 new PNG files added)
  * docs/monograph/qcd_bridge/README.md (MODIFIED, +Stage 4 description)
