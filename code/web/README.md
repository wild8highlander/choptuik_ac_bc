# Choptuik–QCD Bridge — Web Application

Interactive 3D/4D visualization of the 9-section Choptuik–QCD bridge monograph.

**Author**: Ishak Khamzatovich Isaev · [ORCID 0009-0003-7299-0701](https://orcid.org/0009-0003-7299-0701)
**Repository**: [wild8highlander/choptuik_ac_bc](https://github.com/wild8highlander/choptuik_ac_bc)

---

## Where the code lives

The web app is **embedded inside the existing Next.js 16 project** at
`/home/z/my-project/` (the scaffolded dev server runs on port 3000). The
`/home/z/my-project/choptuik_ac_bc/code/web/` directory holds:

* `output/` — generated report files (TXT/CSV/MD/PDF/HTML/DOCX/JSON)
* `README.md` — this file

Source code:

| Path | Purpose |
| --- | --- |
| `src/app/page.tsx` | Single-page app entry (Home / Section N / About) |
| `src/app/layout.tsx` | Root layout with sonner toaster |
| `src/app/api/run/route.ts` | `POST /api/run` — Python engine dispatch |
| `src/app/api/report/route.ts` | `POST /api/report` + `GET /api/report?file=` |
| `src/app/api/figures/[section]/route.ts` | `GET /api/figures/N?variant=3d\|4d` |
| `src/lib/qcd/constants.ts` | Physical constants (mirrors `qcd_bridge_engine.py`) |
| `src/lib/qcd/types.ts` | Shared TypeScript types |
| `src/lib/qcd/i18n.ts` | EN / RU translations + `useTranslation` hook |
| `src/lib/qcd/linalg.ts` | Mulberry32 PRNG, Box–Muller, Jacobi eigensolver |
| `src/lib/qcd/compute.ts` | JS port of all 9 engine sections |
| `src/lib/qcd/figures.ts` | Plotly figure builders for the 9 sections |
| `src/lib/qcd/configStore.ts` | Zustand store (config + last result) |
| `src/lib/qcd/nav.ts` | Tiny SPA nav store (`?view=home\|section:N\|about`) |
| `src/components/layout/AppShell.tsx` | Sidebar + header + sticky footer |
| `src/components/layout/LanguageToggle.tsx` | EN / RU pill toggle |
| `src/components/qcd/PlotlyChart.tsx` | Dynamic-import Plotly wrapper |
| `src/components/qcd/SectionViz.tsx` | Chart + stat tiles + table + static fig |
| `src/components/qcd/SectionView.tsx` | Section pager + ParamPanel + SectionViz + ReportPanel |
| `src/components/qcd/HomeView.tsx` | 9 section overview cards |
| `src/components/qcd/HomeComposite.tsx` | Home + ParamPanel + ReportPanel |
| `src/components/qcd/AboutView.tsx` | Author bio, ORCID, GitHub, monograph |
| `src/components/qcd/ParamPanel.tsx` | Sliders for κ_T, N, n_flavors, seed, sections |
| `src/components/qcd/ReportPanel.tsx` | 7 report format download buttons |

Python bridge:

| Path | Purpose |
| --- | --- |
| `choptuik_ac_bc/code/python/qcd_bridge_engine.py` | Canonical 9-section engine |
| `choptuik_ac_bc/code/python/report_engine.py` | 7-format report writer |
| `choptuik_ac_bc/code/python/web_runner.py` | stdin/stdout bridge for `/api/run` and `/api/report` |
| `choptuik_ac_bc/qcd_bridge/figures/fig_sN_*_3d.png` | Static 3D/4D figure previews |

---

## How to run

The dev server is already running on port 3000 of the host. From a fresh
checkout, the steps are:

```bash
# 1. Install JS deps
cd /home/z/my-project
bun install        # or: npm install

# 2. Verify Python (the venv at /home/z/.venv already has numpy)
python3 -c "import numpy; print(numpy.__version__)"

# 3. Run the dev server
bun run dev        # http://localhost:3000

# 4. (optional) Lint + production build
bun run lint
bun run build
```

The app is also reachable through the Caddy gateway; from the preview panel
use **“Open in New Tab”** or the platform-supplied preview link.

---

## Architecture

```
                 ┌────────────────────────────┐
                 │   Browser (single page /)  │
                 │                            │
   ┌─────────────┴─────────────┐  ┌───────────┴────────────┐
   │ Zustand configStore       │  │ useTranslation (EN/RU) │
   │ + useNav (?view=…)        │  └────────────────────────┘
   └─────────────┬─────────────┘
                 │  live preview (no network)
                 ▼
   ┌────────────────────────────────────────────────────┐
   │  src/lib/qcd/compute.ts  +  src/lib/qcd/figures.ts │
   │  (JS port of all 9 engine sections → Plotly)       │
   └────────────────────┬───────────────────────────────┘
                        │  on user click "Run via Python"
                        ▼
                 POST /api/run  ──►  python3 web_runner.py run
                                        (stdin JSON → stdout JSON)
                                        ▼
                                  qcd_bridge_engine.run_all
                                        ▼
                                  QCDResult JSON → store
```

Report generation:

```
   POST /api/report (format=pdf|docx|txt|csv|md|html|json)
            │
            ▼
   python3 web_runner.py report --output-dir /web/output --format <fmt>
            │
            ▼
   report_engine.ReportEngine.generate(result, formats=[fmt])
            │
            ▼
   /web/output/report.<fmt>      ←── GET /api/report?file=report.<fmt>
```

---

## The 9 sections

| § | Title | Live preview | Python source of truth |
| --- | --- | --- | --- |
| 1 | O_chi operator (28×28) | heatmap + 3D eigenvalue ribbon | `build_Ochi`, `eigvalsh` |
| 2 | RMT universality sweep | 3D scatter (κ_T, BF, ⟨λ⟩) | `kappa_T_sweep` |
| 3 | Spectral staircase | staircase + Wigner + spacing PDF | `folded_spacings` |
| 4 | N-scaling of ⟨λ⟩ → 0 | log-log 3D scatter + bars | `N_scaling_test` |
| 5 | τ_relax dynamics | 3D decay curve, τ and 5τ markers | `tau_relax_dynamics` |
| 6 | κ_T physical estimate | 3D lattice confidence ribbon | `kappa_T_physical_estimate` |
| 7 | Cabibbo angle coincidence | 3D bar chart pred vs meas | `cabibbo_coincidence` |
| 8 | CP 8-step chain | 3D bar chart of 8 steps | `cp_solution_chain` |
| 9 | Jet wake bridge | χ_eff(Λ, δ) surface + anchor | `jet_wake_bridge` |

For each section the user can:

* **Live 3D** — Plotly chart recomputed in the browser from the same formulas
  (mulberry32 PRNG + Jacobi eigensolver + Bayes factor histogram).
* **Static 3D / 4D PNG** — the canonical Python-generated figures served from
  `/api/figures/N?variant=3d|4d`.
* **Run via Python** — dispatches `qcd_bridge_engine.run_all` to get the
  canonical numeric values from NumPy/LAPACK.
* **Download reports** — TXT / CSV / MD / PDF / HTML / DOCX / JSON.

---

## i18n

All UI text is translated to English and Russian in
`src/lib/qcd/i18n.ts`. The language toggle in the header swaps instantly
(no network round-trip) and the choice is persisted in `localStorage` under
`qcd-bridge-lang`. Reports are also localised (the Python `ReportEngine`
honours `language: "en" | "ru"` in the config payload).

---

## License

Isaev Proprietary — see the [monograph](https://github.com/wild8highlander/choptuik_ac_bc).
