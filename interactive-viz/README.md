# interactive-viz

Client-side interactive dashboard for exploring and verifying the framework
in the browser. It is the fourth independent implementation of the
mathematics: every quantity shown — Klein quartic invariants, spinor phases,
Dirac eigenvalue, unified formula, QNM predictions, the enhanced K3 /
Tyukovsky / Einstein GR module — is recomputed live in TypeScript
(`src/lib/compute.ts`) rather than fetched from a backend, so parameter
changes update charts and verification badges instantly.

## What is inside

| Path | Contents |
|------|----------|
| `package.json` | Next.js + React + TypeScript project; scripts `dev`, `build`, `start`, `lint`, `typecheck`, `test` (delegates to typecheck), `check-all`, `clean` |
| `src/app/` | App Router pages: `page.tsx` (home), `verify/`, `simulate/`, `hypothesis/`, `qnm/`, `surfaces/`, `structures/`, `enhanced/` |
| `src/lib/compute.ts` | All mathematical computations, client-side (constants: genus 3, automorphism order 168, λ₁ = 3.838, spinor phases π/2, π/3, π/7, …) |
| `src/lib/simulation.ts` | Sweep and convergence routines powering the simulate page |
| `src/lib/types.ts` | Shared TypeScript types (Klein curve, spinor phases, K3, Tyukovsky, Einstein QNM, verification entries) |
| `src/components/` | Dashboard widgets: `live-chart.tsx` (recharts), `metric-card.tsx`, `parameter-slider.tsx`, `sidebar.tsx`, `verification-status.tsx`, plus `ui/` primitives (button, card, slider, tabs, table, …) |
| `tailwind.config.ts`, `tsconfig.json`, `postcss.config.mjs`, `.eslintrc.json` | Build and lint configuration |
| `next.config.ts`, `next-env.d.ts` | Next.js configuration |

## Pages

| Route | What it shows |
|-------|---------------|
| `/` | Overview dashboard with metric cards and live charts |
| `/verify` | Verification suite run in the browser with pass/fail status per claim |
| `/simulate` | Parameter sweeps (δ_C, λ₁) and convergence plots |
| `/hypothesis` | Custom spinor-structure and group-configuration testing |
| `/qnm` | LIGO/Virgo quasi-normal-mode event comparison |
| `/surfaces` | Riemann surface catalogue (Bolza, Klein, Bring, Macbeath) |
| `/structures` | The 64 spinor structures from δ_A, δ_B, δ_C |
| `/enhanced` | Extended module: K3 surface, Tyukovsky equations, Einstein GR QNM corrections |

## How to run

```bash
cd interactive-viz
npm install          # or: bun install
npm run dev          # dev server (port 3000; forwarded by .devcontainer)
```

Quality gates and production build:

```bash
npm run lint         # eslint
npm run typecheck    # tsc --noEmit
npm run check-all    # lint + typecheck + build
npm run build        # production build
npm run start        # serve the production build
```

The `docker-compose` service in `../docker/` runs this app with a bare Node
image (`npm install && npm run dev`) and mounts the source, exposing port
3000; the dev container forwards the same port automatically.

## Notes

- All computation is client-side: `mathjs` supplies extended-precision-ish
  helpers, `recharts` renders the charts; no API keys, no backend calls, so
  the dashboard works from a static deployment.
- There is no separate test framework configured — `npm run test` currently
  performs the TypeScript check (`tsc --noEmit`), as stated in
  `package.json`.
- Verification statuses shown in the UI are computed from the same reference
  constants as the Python/Julia/Java stacks (e.g. Δ_bC = 3.438710,
  b_Ch = 0.376510), keeping the four implementations comparable.
- `tsconfig.tsbuildinfo` is a build cache and safe to delete.
