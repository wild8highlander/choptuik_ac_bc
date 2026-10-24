--- repo_choptuik/formal_choptuik/README.md	2026-10-24 02:43:32.999413622 +0000
+++ download/formal_choptuik_README/README.md	2026-10-24 02:53:29.621640248 +0000
@@ -15,10 +15,10 @@
 </p>
 
 <p align="center">
-  <a href="#-status"><img alt="status" src="https://img.shields.io/badge/status-v0.4·0_obligations·axiom_clean-8FB7A4?style=flat-square"></a>
-  <a href="lean/"><img alt="Lean 4" src="https://img.shields.io/badge/Lean_4-+mathlib-9B8CDE?logo=lean&logoColor=white&style=flat-square"></a>
+  <a href="#results-at-a-glance-v041"><img alt="status" src="https://img.shields.io/badge/status-v0.4.1·sorry_free·axiom_clean-8FB7A4?style=flat-square"></a>
+  <a href="lean/"><img alt="Lean 4" src="https://img.shields.io/badge/Lean_4-v4.21·mathlib_pinned-9B8CDE?logo=lean&logoColor=white&style=flat-square"></a>
   <a href="python/"><img alt="Python" src="https://img.shields.io/badge/Python-3.10+-4CC9F0?logo=python&logoColor=white&style=flat-square"></a>
-  <a href="python/tests/"><img alt="tests" src="https://img.shields.io/badge/pytest-14/14_passing-8FB7A4?style=flat-square"></a>
+  <a href="python/tests/"><img alt="tests" src="https://img.shields.io/badge/pytest-65/65_passing-8FB7A4?style=flat-square"></a>
   <a href="#reproducibility"><img alt="seed" src="https://img.shields.io/badge/seed-1993·deterministic-E8B44A?style=flat-square"></a>
   <a href="blueprint/gap_registry.csv"><img alt="gaps" src="https://img.shields.io/badge/gap_registry-G1..G6-E86A6A?style=flat-square"></a>
   <a href="monographs/"><img alt="monographs" src="https://img.shields.io/badge/monographs-2×(RU·EN·DOCX·PDF)-B08A3E?style=flat-square"></a>
@@ -63,11 +63,12 @@
 skeleton** (`lean/`), a **deterministic numerical service** (`python/`), a
 **typed bridge** between them (`bridge/`), the **obligation ledger** and
 tooling decision record (`blueprint/`), the **three-phase roadmap**
-(`roadmap/`), and two **research monographs** in four languages-formats
+(`roadmap/`), and two **research monographs**, each in {RU, EN} × {DOCX, PDF}
 (`monographs/`).
 
 ## Table of contents
 
+- [Results at a glance](#results-at-a-glance-v041)
 - [Folder map](#folder-map)
 - [Animations](#animations)
 - [Key figures](#key-figures)
@@ -82,21 +83,57 @@
 
 ---
 
+## Results at a glance (v0.4.1)
+
+An audited inventory of the committed tree — every number below was counted
+from the files as they stand, not promised:
+
+| Layer | Committed state |
+|---|---|
+| **Lean theory** (`lean/`) | 12 modules + root re-export + `AxiomAudit.lean`; Lean `v4.21.0`, mathlib pinned `v4.21.0`; **0 `sorry`**, **0 project axioms**; all **33 audited headline theorems — 21 theory + 12 bridge** — print `[propext, Classical.choice, Quot.sound]` and nothing else |
+| **Bridge** (`bridge/`) | protocol **v1.1, 7 methods**; **certificate channel live**: 4 kinds (`spectrum`, `newton`, `scaling`, `interval`) → committed JSONs → `Choptuik.Bridge.Generated` (exact rationals, `norm_num`) → discharged into the spectral / Newton–Kantorovich / interval headlines |
+| **Python service** (`python/`) | **65 pytests — 17 service + 18 certificate + 30 client** (ZMQ round-trip, fuzz, timeouts); ZMQ REP on `tcp://127.0.0.1:5557`; certificate producer `certify.py` with `emit` / `check` |
+| **Data** (`data/`) | **7 deterministic CSVs**, 12,890 rows total, seed 1993 |
+| **Figures & animations** | **8 PNG figures @ 300 dpi** (dark/light × en/ru) + **4 GIFs** (24–72 frames) |
+| **Monographs** (`monographs/`) | **8 renditions** — 2 volumes × {RU, EN} × {DOCX, PDF}, 16–20 pages each |
+| **Governance** | gap ledger G1–G6 with per-gap status (2 resolved, 3 partial, bridge live); roadmap with 17 tasks and a 9-milestone ledger; CI template enforcing axiom audit + data byte-identity |
+
+Calibrated constants of the committed build — locked by the tests against the
+committed CSVs:
+
+| Quantity | Committed value | Cross-check |
+|---|---|---|
+| λ₀ — single unstable mode | 2.6745 | `single_unstable: True` in `data/spectrum/eigenvalues.csv` |
+| γ = 1/λ₀ | 0.373902 | least-squares fit 0.373880, rms 2.1·10⁻³ |
+| Δ — echoing period | 0.693147 = ln 2 | recovered from the raw amplitude series, error 2.0·10⁻¹⁰ |
+| echo spacing 2π/Δ | 9.064720 | max deviation across the spectrum 2.0·10⁻¹⁰ |
+
+> [!NOTE]
+> These constants verify the **calibrated mode model and the workflow**
+> (determinism, strict enclosures, certificate discipline) — not the full
+> Einstein–scalar system, which is precisely what the roadmap formalizes.
+
+---
+
 ## Folder map
 
 | Folder | Contents | Entry point |
 |---|---|---|
 | [`lean/`](lean/) | Lean 4 theory: `Choptuik.{Geometry,Analysis,Existence,Stability,Scaling,Bridge}` + lakefile | [`lean/README.md`](lean/README.md) |
 | [`python/`](python/) | numerical service (ZMQ v1.1), certificate producer, 65 pytests | [`python/README.md`](python/README.md) |
-| [`bridge/`](bridge/) | protocol v1.1 + certificate artifacts + example client | [`bridge/README.md`](bridge/README.md) |
+| [`bridge/`](bridge/) | protocol v1.1 (7 methods) + 4 committed certificate JSONs + example client | [`bridge/README.md`](bridge/README.md) |
 | [`blueprint/`](blueprint/) | technical spec, axiomatic base, gap registry, tooling verdict, module map | [`blueprint/README.md`](blueprint/README.md) |
-| [`roadmap/`](roadmap/) | three phases with tasks, acceptance criteria, milestones | [`roadmap/README.md`](roadmap/README.md) |
+| [`roadmap/`](roadmap/) | three phases with 17 tasks, acceptance criteria, milestone ledger | [`roadmap/README.md`](roadmap/README.md) |
 | [`monographs/`](monographs/) | 2 monographs × {RU, EN} × {DOCX, PDF} | [`monographs/README.md`](monographs/README.md) |
 | [`figures/`](figures/) | 8 publication-grade figures (300 dpi) | [`figures/README.md`](figures/README.md) |
-| [`assets/`](assets/) | animated SVG logos/banners + 4 GIFs | [`assets/README.md`](assets/README.md) |
-| [`data/`](data/) | deterministic CSVs behind every figure | [`data/README.md`](data/README.md) |
-| [`docs/`](docs/) | references, glossary | [`docs/README.md`](docs/README.md) |
-| [`ci/`](ci/) | GitHub Actions template for `lake build` + pytest | [`ci/README.md`](ci/README.md) |
+| [`assets/`](assets/) | 2 logos + 8 animated SVG banners + 4 GIFs | [`assets/README.md`](assets/README.md) |
+| [`data/`](data/) | 7 deterministic CSVs (~12.9k rows) behind every figure | [`data/README.md`](data/README.md) |
+| [`docs/`](docs/) | references (10 sources), glossary (17 terms) | [`docs/README.md`](docs/README.md) |
+| [`ci/`](ci/) | GitHub Actions template: `lake build` + axiom audit, pytest, byte-identical data regen | [`ci/README.md`](ci/README.md) |
+
+Root files: [`CITATION.cff`](CITATION.cff) · [`CONTRIBUTING.md`](CONTRIBUTING.md)
+(house rules: sorry-as-ledger-entry, no new axioms, paired protocol tests,
+no hand-edited regenerables).
 
 ---
 
@@ -147,16 +184,16 @@
 
 ## Gap registry at a glance
 
-| ID | Gap | Severity | Phase | Strategy |
-|---|---|---|---|---|
-| **G1** | Existence of the critical solution | 🔴 Blocker | II | Newton in a Banach space + compact inverse + IFT |
-| **G2** | Stability spectrum of the linearized operator | 🔴 Blocker | III | spectral theory ⇒ unique unstable mode, γ = 1/λ₀ |
-| **G3** | Isotropic strong singularity, conformal compactification | 🟠 High | II–III | null-geodesic criterion + compactification layer |
-| **G4** | Lean⇄Python typed bridge | 🟠 High | I | certificate channel (v0.4.1: live) + ZMQ v1.1, regression-locked |
-| **G5** | Verified interval arithmetic | 🟡 Medium | I | outward rounding, soundness proofs, certificates |
-| **G6** | Axiomatic base declaration | 🟢 Low | I | three standard axioms, CI-enforced |
+| ID | Gap | Severity | Phase | Strategy | Status (v0.4.1) |
+|---|---|---|---|---|---|
+| **G1** | Existence of the critical solution | 🔴 Blocker | II | Newton in a Banach space + compact inverse + IFT | 🟠 partial: scaffold existence + uniqueness and the Newton–Kantorovich core proved; RT certificate pending |
+| **G2** | Stability spectrum of the linearized operator | 🔴 Blocker | III | spectral theory ⇒ unique unstable mode, γ = 1/λ₀ | 🟠 partial: spectral core proved from the certificate hypothesis; scaling law proved in log-log form |
+| **G3** | Isotropic strong singularity, conformal compactification | 🟠 High | II–III | null-geodesic criterion + compactification layer | 🟠 partial: conditional core proved (coercivity + Weyl certificates); compactification layer pending |
+| **G4** | Lean⇄Python typed bridge | 🟠 High | I | certificate channel + ZMQ v1.1, regression-locked | 🟢 live: 4 certificate kinds emitted, Lean-checked and discharged; FFI/ZMQ Lean client stays illustrative by design |
+| **G5** | Verified interval arithmetic | 🟡 Medium | I | outward rounding, soundness proofs, certificates | ✅ resolved (v0.4): `add_sound`, `mul_sound`, `certificate_principle` proved |
+| **G6** | Axiomatic base declaration | 🟢 Low | I | three standard axioms, CI-enforced | ✅ resolved (v0.4): axiom audit clean; v0.3 `F_ref` axioms removed |
 
-Full ledger with dependencies and acceptance criteria:
+Full ledger with dependencies, acceptance criteria and per-gap status:
 [`blueprint/gap_registry.csv`](blueprint/gap_registry.csv) ·
 axiom policy: [`blueprint/axiomatic_base.md`](blueprint/axiomatic_base.md).
 
@@ -174,10 +211,14 @@
 | **II — Existence** | 6–18 | machine-checked `critical_solution_exists` | **G1** |
 | **III — Stability** | 18–27 | `unique_unstable_mode`, γ = 1/λ₀, echoing, universality | **G2** |
 
-Task tables, acceptance criteria and risks per phase:
+Task tables (17 tasks: P1.1–P1.6 · P2.1–P2.6 · P3.1–P3.5), acceptance
+criteria and risks per phase:
 [`roadmap/phase1_foundation.md`](roadmap/phase1_foundation.md) ·
 [`phase2_existence.md`](roadmap/phase2_existence.md) ·
 [`phase3_stability.md`](roadmap/phase3_stability.md).
+Machine-readable milestone ledger (9 entries — M1.1 environment done,
+M1.2 interval certificates delivered with v0.4, M1.3 bridge live at v1.1 in
+v0.4.1, the rest open): [`roadmap/milestones.csv`](roadmap/milestones.csv).
 
 ---
 
@@ -192,7 +233,7 @@
 | **I** | *From Code to Machine-Checked Proof: a Formalization Roadmap for Choptuik Critical Phenomena* | [`ru/…Roadmap_RU.docx/.pdf`](monographs/ru/) · [`en/…Roadmap_EN.docx/.pdf`](monographs/en/) |
 | **II** | *Gap Analysis and Proof-Assistant Selection for the Choptuik Formalization Programme* | [`ru/…Gaps_RU.docx/.pdf`](monographs/ru/) · [`en/…Gaps_EN.docx/.pdf`](monographs/en/) |
 
-Each volume: 20–30 pages, cover, table of contents, embedded figures,
+Each volume: 16–20 pages, cover, table of contents, embedded figures,
 references.  Details and reading order: [`monographs/README.md`](monographs/README.md).
 
 ---
@@ -213,10 +254,14 @@
 ├── Stability
 │   ├── Linearization    perturbation modes, linearized operator
 │   └── Spectrum         unique_unstable_mode, γ = 1/λ₀, scaling law           G2
-└── Scaling              universality + echoing formula                        G2
+├── Scaling              universality + echoing formula                        G2
+└── Bridge               certificate channel Lean⇄Python (v0.4.1: live)        G4
+    ├── Certificates     robustness layer: certificate checks ⇒ physics
+    ├── Generated        exact rational data, norm_num-checked (auto-generated)
+    └── Discharge        discharge into the spectral / NK / interval headlines
 ```
 
-Build it:
+Build it (toolchain `leanprover/lean4:v4.21.0`, mathlib pinned `v4.21.0`):
 
 ```bash
 cd lean
@@ -240,15 +285,20 @@
 ```bash
 cd python
 pip install -r requirements.txt
-python -m pytest tests/ -v            # 14 protocol/physics tests
+python -m pytest tests/ -v            # 65 tests: 17 service + 18 certify + 30 client
 python choptuik_service/server.py     # ZMQ REP on tcp://127.0.0.1:5557
 python scripts/generate_data.py       # -> data/*.csv        (seed 1993)
 python scripts/generate_figures.py    # -> figures/*.png
 python scripts/generate_animations.py # -> assets/gifs/*.gif
+
+# the proof-grade certificate channel (gap G4):
+python -m choptuik_service.certify emit   # -> bridge/certificates/*.json + Generated.lean
+python -m choptuik_service.certify check  # verify the committed artifacts
 ```
 
 Protocol endpoints (`ping`, `spectrum`, `scaling_fit`, `echo_period`,
-`evolve`, `interval_bound`): [`bridge/protocol.md`](bridge/protocol.md).
+`evolve`, `interval_bound`, `certificate` — 7 methods, v1.1):
+[`bridge/protocol.md`](bridge/protocol.md).
 
 ---
 
@@ -260,10 +310,11 @@
 | Rule | Value |
 |---|---|
 | seed | `1993` (the Choptuik year) |
-| stack | numpy + matplotlib + Pillow, no hidden state |
+| stack | numpy + matplotlib + Pillow (+ pytest; pyzmq optional for the live bridge), no hidden state |
 | entry points | `python/scripts/generate_{data,figures,animations,architecture}.py` |
-| figures variants | `--theme dark|light  --lang en|ru` |
-| tests | `pytest tests/` — 14 green |
+| figures variants | `--theme dark\|light  --lang en\|ru` |
+| certificates | `python -m choptuik_service.certify emit` — byte-stable on any conforming LAPACK |
+| tests | `pytest tests/` — 65 collected (30 client + 18 certificate + 17 service) |
 
 ---
 
