# qcd_bridge

Generated and committed artifacts of the Choptuik–QCD bridge verification
campaign: the 3D/4D figures, the 4D animations, the run configurations and
the multi-format reports produced by the three independent engines (Python,
Java, Julia). The computational code itself lives in `../code/` — this folder
is the evidence trail that the engines' outputs are archived and comparable.

## What is inside

| Path | Contents |
|------|----------|
| `configs/` | Run configurations consumed by `code/python/run.py --mode custom --config …`: `verify_all.json` (all 9 sections, κ_T sweep values, N values, seed 42), `verify_section_3_8.json`, `verify_custom.json` |
| `figures/` | Per-section figures `fig_s1…fig_s9` in 3D and 4D variants, each as PNG (600 DPI) + vector PDF + SVG, plus `figures_manifest.json` recording generation parameters and statuses |
| `animations/` | Animated MP4 + GIF per section (`fig_s1…fig_s9_*_4d_anim.*`), 18 files, plus `animations_manifest.json` |
| `reports/` | Python-engine reports in seven formats: `report.{txt,csv,md,pdf,html,docx,json}` |
| `reports_java/` | The same seven report formats produced by the independent Java engine (`code/java/qcd_bridge_engine.java`) for cross-implementation comparison |

## How to use

The artifacts are regenerable from the engines:

```bash
# full verification of all 9 sections (writes reports/ and console summary)
python3 code/python/run.py --mode verify_all --non-interactive

# config-driven run
python3 code/python/run.py --mode custom --config qcd_bridge/configs/verify_all.json

# regenerate all static figures and animations
python3 code/python/run.py --mode figures

# Java engine reports (into reports_java/)
javac -cp jama.jar code/java/qcd_bridge_engine.java && java -cp .:jama.jar code/java/qcd_bridge_engine

# Julia engine reports (into reports_julia/)
julia code/julia/qcd_bridge_engine.jl
```

Committed reports embed the full execution log after the results block, so
each file records the config (mode, sections, κ_T, N, seed) that produced
it.

### Config files

| Config | Mode | Purpose |
|--------|------|---------|
| `configs/verify_all.json` | `custom` | Full verification: sections 1–9, κ_T sweep over 13 values, N ∈ {10, 28, 50, 100, 200, 500, 1000}, κ_T = 8.45, N = 28, six flavours, seed 42, all seven report formats |
| `configs/verify_section_3_8.json` | `custom` | Focused run of sections 3 and 8 |
| `configs/verify_custom.json` | `custom` | Template for fully custom parameter sets |

## Notes

- The manifests (`figures_manifest.json`, `animations_manifest.json`) store
  per-figure elapsed times and parameters (e.g. N values and realisation
  counts for the N-scaling section), making the figure provenance explicit.
- The committed `reports/` show the reference run with the monograph
  parameters: κ_T = 8.45, N = 28, six flavours, seed 42; the O_chi spectrum
  (28×28) with trace ≈ 28 and ⟨λ⟩ ≈ 1 is the leading consistency check.
- Java reports in `reports_java/` should agree with `reports/` on every
  deterministic quantity; any divergence is a verification finding, not a
  display artifact.
- A Julia engine writes to `reports_julia/` on first run (not committed).
- The nine sections and their meaning are documented in `../code/README.md`
  and in the manuscripts under `../monograph/` and `../docs/qcd_bridge/`.
