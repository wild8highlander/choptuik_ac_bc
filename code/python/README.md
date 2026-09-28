# code/python

Canonical Python engine for the Choptuik–QCD bridge: implements all nine
sections of the monograph, generates every 3D/4D figure and animation, writes
seven report formats, and serves as the numerical source of truth that the
Java and Julia ports (and the web dashboard) are checked against.

## What is inside

| File | Contents |
|------|----------|
| `qcd_bridge_engine.py` | Core engine (~26 KB): physical constants, E8 Cartan / K3 intersection form, O_chi construction and spectrum, RMT universality sweep, spectral staircase, N-scaling, τ_relax dynamics, κ_T physical estimate, Cabibbo coincidence, CP 8-step chain, jet wake bridge; `QCDBridgeConfig` + `run_all` |
| `report_engine.py` | `ReportEngine` writing TXT, CSV, MD, PDF, HTML, DOCX, JSON; structure: `[RESULTS]` first, then `[LOGS]` |
| `run.py` | CLI with modes `verify_all`, `verify_section`, `custom`, `interactive`, `figures`; bilingual UI (`--lang en|ru`) |
| `generate_figures_3d_4d.py` | Per-section 3D and 4D plots (PNG 600 DPI + vector PDF + SVG); writes the figures manifest |
| `generate_animations_4d.py` | Animated MP4 + GIF per section (4th dimension = time / sweep parameter / rotation) |
| `web_runner.py` | stdin/stdout bridge invoked by the web app's `/api/run` and `/api/report` routes |

## How to run

```bash
cd code/python

# full verification, all 9 sections
python run.py --mode verify_all --non-interactive

# specific sections
python run.py --mode verify_section --sections 1,3,5

# custom run driven by a JSON config (configs live in ../../qcd_bridge/configs/)
python run.py --mode custom --config ../../qcd_bridge/configs/verify_all.json

# regenerate figures and animations only
python run.py --mode figures

# interactive menu, Russian UI
python run.py --mode interactive --lang ru
```

Other CLI flags: `--output-dir` (default `reports`), `--formats`
(comma-separated report formats), `--kappa-T`, `--N`, `--seed` (default 42),
`--list-configs`. Config files shipped in `../../qcd_bridge/configs/`:
`verify_all.json`, `verify_section_3_8.json`, `verify_custom.json`.

Direct engine and bridge usage:

```bash
echo '{"mode":"custom","sections":[1,2]}' | python3 web_runner.py run
echo '{"mode":"custom","sections":[1,2,3],"format":"pdf"}' | \
    python3 web_runner.py report --output-dir /tmp/out
```

## Outputs

Everything is written into the shared `../../qcd_bridge/` tree:

| Target | Produced by | Contents |
|--------|-------------|----------|
| `qcd_bridge/figures/` | `generate_figures_3d_4d.py` | `fig_s1…fig_s9` in 3D and 4D variants, PNG/PDF/SVG + `figures_manifest.json` |
| `qcd_bridge/animations/` | `generate_animations_4d.py` | MP4 + GIF per section + `animations_manifest.json` |
| `qcd_bridge/reports/` | `run.py` / `report_engine.py` | `report.{txt,csv,md,pdf,html,docx,json}` |
| `qcd_bridge/reports_java/`, `reports_julia/` | Java / Julia ports | same formats from the cross-language runs |

## Notes

- Dependencies: `numpy` for the engine and `matplotlib` (with 3D toolkit)
  for figures; the report writer lazily imports `reportlab` / `python-docx`
  and degrades gracefully if they are absent (other formats still work).
- All randomness is seeded (`--seed 42` default) and the report embeds the
  full execution log, so any committed report can be traced back to its
  parameters.
- The TypeScript layer in `../web/src/lib/qcd/compute.ts` is a port of this
  engine's nine sections; `web_runner.py` is the dispatch path used by the
  web app when the user requests the canonical NumPy/LAPACK numbers.
