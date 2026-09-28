# code/java

Independent Java implementation of the Choptuik–QCD bridge engine: a
line-by-line port of `../python/qcd_bridge_engine.py` covering all nine
monograph sections. Its purpose is verification by reimplementation — every
eigenvalue, Bayes factor and scaling exponent is recomputed with Java data
structures and compared against the canonical Python outputs.

## What is inside

| File | Contents |
|------|----------|
| `qcd_bridge_engine.java` | Single-file engine (~41 KB): constants, E8 Cartan matrices, K3 intersection form E8 ⊕ E8 ⊕ U ⊕ U ⊕ U, O_chi construction, RMT sweep, spectral staircase, N-scaling, τ_relax dynamics, κ_T estimate, Cabibbo coincidence, CP chain, jet wake bridge, plus TXT/MD/HTML/CSV/PDF/DOCX report writers |

## How to run

From the file's own header comments:

```bash
# compile (JAMA is only needed for optional matrix helpers)
javac -cp jama.jar qcd_bridge_engine.java

# run all 9 sections (default mode)
java -cp .:jama.jar qcd_bridge_engine

# run selected sections
java -cp .:jama.jar qcd_bridge_engine --section 1,3,5

# run with a custom kappa_T
java -cp .:jama.jar qcd_bridge_engine --custom 8.45
```

The `main` block writes a full report set — `report.json`, `report.txt`,
`report.md`, `report.html`, `report.csv`, `report.pdf`, `report.docx` — and
prints each output path plus the elapsed time.

## Verification content

The engine mirrors every section function of the Python original:

| § | Computation | Method |
|---|-------------|--------|
| 1 | O_chi operator (28×28) | K3 intersection form E8 ⊕ E8 ⊕ U ⊕ U ⊕ U built from explicit E8 Cartan matrices, fused with flavour and temporal blocks |
| 2 | RMT universality sweep | GUE vs Poisson ensembles across κ_T values, Bayes-factor classification |
| 3 | Spectral staircase | Folded spacings vs Wigner semicircle and Poisson baselines |
| 4 | N-scaling | ⟨λ⟩ → 0 as 1/√N artifact demonstration |
| 5 | τ_relax dynamics | Exponential damping on the CKM residual timescale |
| 6 | κ_T estimate | Lattice Dirac data bounds (2.62 lower, 8.45 best fit) |
| 7 | Cabibbo coincidence | sin²θ_C = 0.051 comparison |
| 8 | CP chain | 8-step solution sequence |
| 9 | Jet wake bridge | χ_eff(Λ, δ) surface with anchor point |

## Notes

- The committed outputs of this engine live in `../../qcd_bridge/reports_java/`
  (same seven formats as the Python reports in `../../qcd_bridge/reports/`),
  so the two implementations can be compared file by file.
- Random-matrix draws use a fixed-seed RNG (`new Random(42)`), matching the
  reproducibility policy of the other engines.
- Physical constants are duplicated from the Python engine on purpose
  (δ_C = π/7, N_HILBERT = 28, κ_T bounds 2.62/8.45, τ_relax = 5.0e-41 s,
  sin²θ_Cabibbo = 0.051) so that each file is self-contained and auditable.
- No build system is required: it is a single source file compiled with
  `javac`; the Spring Boot application in `../../java-webapp/` is the
  separate Klein-quartic web stack, not part of this engine.
