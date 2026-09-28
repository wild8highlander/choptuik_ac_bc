# code/web

Interactive single-page web application for the Choptuik–QCD bridge:
live 3D visualization of all nine monograph sections, a parameter panel,
and one-click report downloads in seven formats. The mathematics is ported
to TypeScript so charts recompute instantly in the browser; a "Run via
Python" button additionally dispatches the canonical NumPy engine
(`../python/qcd_bridge_engine.py`) for authoritative numbers.

## What is inside

| Path | Purpose |
|------|---------|
| `package.json` | Next.js + React + TypeScript project (Bun scripts); dependencies include Plotly, Zustand, Radix UI, Tailwind, next-intl |
| `next.config.ts`, `postcss.config.mjs`, `tailwind.config.ts`, `tsconfig.json` | Build configuration |
| `src/app/page.tsx`, `layout.tsx` | Single-page app entry (Home / Section N / About) and root layout with sonner toaster |
| `src/app/api/run/route.ts` | `POST /api/run` — dispatch to the Python engine via `web_runner.py` |
| `src/app/api/report/route.ts` | `POST /api/report` (generate) + `GET /api/report?file=` (download) |
| `src/app/api/figures/[section]/route.ts` | `GET /api/figures/N?variant=3d\|4d` — canonical Python-generated figures |
| `src/lib/qcd/constants.ts` | Physical constants mirroring `qcd_bridge_engine.py` |
| `src/lib/qcd/compute.ts` | TypeScript port of all nine engine sections |
| `src/lib/qcd/figures.ts` | Plotly figure builders for the nine sections |
| `src/lib/qcd/linalg.ts` | Mulberry32 PRNG, Box–Muller sampling, Jacobi eigensolver |
| `src/lib/qcd/i18n.ts` | EN/RU translations + `useTranslation` hook |
| `src/lib/qcd/configStore.ts`, `nav.ts`, `types.ts` | Zustand config store, SPA navigation, shared types |
| `src/components/qcd/…` | `HomeView`, `SectionView`, `SectionViz`, `ParamPanel`, `ReportPanel`, `PlotlyChart`, `AboutView`, `HomeComposite` |
| `src/components/layout/…` | `AppShell` (sidebar/header/footer), `LanguageToggle` (EN/RU) |
| `src/components/ui/…` | shadcn-style UI primitives |

## How to run

```bash
cd code/web
bun install            # or: npm install
bun run dev            # dev server on port 3000 (logs tee'd to dev.log)

bun run lint           # eslint
bun run build          # production build (standalone output)
bun run start          # serve the standalone build via bun
```

The dev server is also launched by the `interactive-viz` Compose pattern in
`../../docker/docker-compose.yml`, and port 3000 is forwarded by the dev
container configuration.

## The nine sections

| § | Title | Live preview | Python source of truth |
|---|-------|--------------|------------------------|
| 1 | O_chi operator (28×28) | heatmap + 3D eigenvalue ribbon | `build_Ochi` |
| 2 | RMT universality sweep | 3D scatter (κ_T, BF, ⟨λ⟩) | `kappa_T_sweep` |
| 3 | Spectral staircase | staircase + Wigner + spacing PDF | `folded_spacings` |
| 4 | N-scaling of ⟨λ⟩ → 0 | log-log 3D scatter + bars | `N_scaling_test` |
| 5 | τ_relax dynamics | 3D decay curve, τ and 5τ markers | `tau_relax_dynamics` |
| 6 | κ_T physical estimate | 3D lattice confidence ribbon | `kappa_T_physical_estimate` |
| 7 | Cabibbo angle coincidence | 3D bars, predicted vs measured | `cabibbo_coincidence` |
| 8 | CP 8-step chain | 3D bars of the 8 steps | `cp_solution_chain` |
| 9 | Jet wake bridge | χ_eff(Λ, δ) surface + anchor | `jet_wake_bridge` |

For each section the user can:

- **Live 3D** — Plotly chart recomputed in the browser from the same formulas
  (Mulberry32 PRNG + Jacobi eigensolver + Bayes-factor histogram).
- **Static 3D / 4D PNG** — canonical Python-generated figures served from
  `/api/figures/N?variant=3d|4d` (files in `../../qcd_bridge/figures/`).
- **Run via Python** — `POST /api/run` pipes the config to
  `python3 ../python/web_runner.py run` and returns the canonical
  NumPy/LAPACK results.
- **Download reports** — TXT / CSV / MD / PDF / HTML / DOCX / JSON via
  `POST /api/report` + `GET /api/report?file=report.<fmt>`.

## Internationalisation

All UI strings exist in English and Russian (`src/lib/qcd/i18n.ts`); the
header toggle switches instantly and persists the choice in `localStorage`
under `qcd-bridge-lang`. Python-generated reports are localised too — the
`ReportEngine` honours `language: "en" | "ru"` in the config payload.

## Notes

- The browser path never touches the network for computation; only the
  explicit "Run via Python", figure serving and report downloads hit the API
  routes.
- `src/lib/db.ts` and the Prisma scripts in `package.json` belong to the
  scaffolding this app was built into; the QCD-bridge features do not use a
  database.
- The tracked tree here is the app source; generated report files are written
  to an untracked `output/` directory at runtime.
