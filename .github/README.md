# .github

Repository automation and community templates: GitHub Actions workflows that
re-verify the computations on every change, issue/PR/discussion templates
centred on verification results, and repository configuration (funding,
labelling, dependency updates, link checking).

## What is inside

| Path | Purpose |
|------|---------|
| `workflows/ci.yml` | Full Python test suite with coverage to Codecov; runs on every push and PR, no path filters; matrix Python 3.10/3.11/3.12 × ubuntu/macos/windows |
| `workflows/lint.yml` | Code-quality checks (ruff, mypy, black, prettier) on every push and PR |
| `workflows/pages.yml` | Builds and deploys the MkDocs site (`docs-site/`) to GitHub Pages; also manually dispatchable |
| `workflows/periodic-verify.yml` | Scheduled full verification every Monday 06:00 UTC (`python run.py --mode verify --non-interactive`) with deviation checks |
| `workflows/verify-audit-transfer.yml` | Re-runs the `audit_transfer/` verification core when that folder changes, plus manual dispatch |
| `workflows/release.yml` | Builds, signs with Sigstore and publishes a GitHub Release on version-tag pushes |
| `workflows/scorecard.yml` | OpenSSF Scorecard security analysis |
| `workflows/link-check.yml` | Markdown link checking (config in `mlc_config.json`) |
| `workflows/labeler.yml`, `labeler/` | Automatic PR labelling by path (`config.yml`) and by title (`title-labels.yml`) |
| `workflows/stale.yml`, `workflows/greeting.yml` | Stale-issue management and newcomer greetings |
| `dependabot.yml` | Automated dependency updates |
| `ISSUE_TEMPLATE/` | `bug_report`, `feature_request`, `new_surface` (markdown) and `bug_report`, `feature_request`, `research_question` (YAML forms), plus a dedicated `verification_discrepancy` template for reporting failed verifications |
| `DISCUSSION_TEMPLATE/` | `verification`, `new_result`, `q_a` discussion templates |
| `PULL_REQUEST_TEMPLATE.md` | PR checklist |
| `FUNDING.yml` | GitHub Sponsors (`wild8highlander`) and Zenodo/DOI links |
| `config.yml` | Contact links (mathematical discussion, documentation site); blank issues disabled |
| `mlc_config.json` | Ignore list for the markdown link checker |

### Workflow triggers

| Workflow | Trigger |
|----------|---------|
| CI | push / pull_request, plus manual dispatch |
| Lint | push / pull_request |
| Pages | push touching `docs-site/**` or `python/src/**`, plus manual dispatch |
| Verify on Schedule | weekly cron (Monday 06:00 UTC), plus manual dispatch |
| Audit-transfer verification | push touching `audit_transfer/**`, plus manual dispatch |
| Release | version-tag push |
| OpenSSF Scorecard | scheduled / branch protection events |
| Markdown Link Check | scheduled / manual |
| Auto Label, Stale, Greeting | pull-request and issue activity |

## How it works

The workflows are the continuous-verification backbone: any push or PR
re-runs the Python test suite and lint gates; a weekly schedule re-runs the
full verification to catch environment drift; changes to `audit_transfer/`
trigger their own verification workflow; and the documentation site is
rebuilt whenever its sources or the documented Python package change. The
release workflow fires only on tag pushes and produces signed release
artifacts.

## Notes

- The verification workflows call the real entry points (e.g.
  `python run.py --mode verify --non-interactive` from `python/`, and the
  `audit_transfer/python/run_all.py` orchestrator), so a green checkmark
  means the numbers were reproduced, not merely that the code compiles.
- The `verification_discrepancy` issue template exists specifically for
  reporting a failed or irreproducible verification result; please use it
  rather than a plain bug report for numeric mismatches.
- Workflow names as shown in the Actions tab: CI, Lint, Pages, Verify on
  Schedule, Release, OpenSSF Scorecard, Markdown Link Check, Auto Label,
  Stale Issues & PRs, Greeting.
- Codecov configuration lives at the repository root (`codecov.yml`), not in
  this folder.
