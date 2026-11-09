# docs-site

MkDocs Material documentation site for the framework — the source of
<https://wild8highlander.github.io/choptuik_ac_bc/>. It contains the API
reference (generated with mkdocstrings from the Python package), the
mathematical background pages, tutorials, and development documentation.
Deployment to GitHub Pages is automated by the `pages.yml` workflow.

## What is inside

| Path | Contents |
|------|----------|
| `mkdocs.yml` | Material theme configuration: light/dark palettes, sticky navigation tabs, search, MathJax via `pymdownx.arithmatex`, code copy buttons, tabs, tooltips; repo links and edit URI |
| `requirements.txt` | Site dependencies: `mkdocs`, `mkdocs-material`, `mkdocstrings`, `mkdocstrings-python`, `mkdocs-autorefs`, `pymdown-extensions`, `mike` (versioned-docs plugin) |
| `docs/index.md` | Landing page of the site |
| `docs/api/` | API reference: `core/` (choptyuk formula, Dirac operator, Klein curve, spinor phases, surfaces, QNM, hypothesis, enhanced verification), `verification/` (`verify-all`, `verify-enhanced`), `simulation/` (`simulator`), `visualization/` (`plots`), `reporting/` (`report-writer`) |
| `docs/mathematics/` | Background essays: Klein quartic, spinor phases, Dirac operator, formula, K3 surfaces, Klein quartic quartic curve companions, enhanced verification |
| `docs/tutorials/` | `quick-start`, `verification`, `custom-parameters`, `interactive-menu`, `ligo-analysis` |
| `docs/development/` | `contributing`, `testing`, `ci-cd`, `release` |
| `docs/changelog.md` | Project changelog page |
| `docs/stylesheets/extra.css`, `docs/javascripts/mathjax.js` | Custom styling and MathJax bootstrap |
| `overrides/main.html` | Material theme override template |

### Navigation structure

| Tab | Pages |
|-----|-------|
| Home | `docs/index.md` |
| Tutorials | `quick-start`, `verification`, `custom-parameters`, `interactive-menu`, `ligo-analysis` |
| Mathematics | Klein quartic, spinor phases, Dirac operator, formula, K3 surfaces, enhanced verification |
| API | `core/` (8 pages), `verification/`, `simulation/`, `visualization/`, `reporting/` |
| Development | `contributing`, `testing`, `ci-cd`, `release` |

## How to run

```bash
cd docs-site
python3 -m pip install -r requirements.txt

mkdocs serve    # live-reload preview at http://localhost:8000
mkdocs build    # static build into site/
```

The Pages workflow (`.github/workflows/pages.yml`) builds and deploys the
site automatically on pushes that touch `docs-site/**` or `python/src/**`,
and can be triggered manually via `workflow_dispatch`.

## Notes

- API pages use mkdocstrings with the Python package as object inventory —
  keep `python/src/` importable (its dependencies are in
  `python/requirements.txt`) when building locally.
- Mathematical notation relies on `pymdownx.arithmatex` (generic mode) plus
  the bundled `mathjax.js`; admonitions, footnotes, tabs and details blocks
  are enabled in `mkdocs.yml`.
- `mike` is present for versioned documentation deployments from the release
  workflow.
- Content language is English; the theme language is set to `en` in
  `mkdocs.yml`.
- The site is rebuilt on every push that touches the documented Python
  package (`python/src/**`), so the API pages cannot silently drift from the
  code.
- Local build output goes to `site/` (generated, not tracked); the
  `overrides/` directory only contains `main.html`, the single theme
  override in use.
