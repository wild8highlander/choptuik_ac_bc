# Publishing this archive to GitHub (operator runbook)

The archive is a git-ready repository. Recommended settings:

1. **Create the repository** `Quark_Hawking_Bridge` (public) and push:

   ```bash
   git init -b main
   git add -A && git commit -m "QHB Unified v2.3.0"
   git remote add origin git@github.com:wild8highlander/Quark_Hawking_Bridge.git
   git push -u origin main
   ```

   (or clone from the shipped bundle: `git clone QHB_Unified_v2.3.0.bundle qhb`)

2. **Description** (suggested):
   *Confinement via false-vacuum escape, vortex anchor ω=3/(2π), branch laws,
   cooling scenario and five convergence ladders — with a Lean 4/Mathlib layer,
   machine-verified numbers and a falsification-first discipline.*

3. **Topics**: `mathematical-physics`, `confinement`, `quantum-field-theory`,
   `lean4`, `mathlib`, `reproducible-research`, `strangelets`, `nuclearites`,
   `hawking-radiation`, `research-monograph`

4. **Settings → General**
   - ☑ Releases: create `v2.3.0` tag → `release.yml` builds zip + SHA256SUMS.
   - Social preview: upload `.github/images/social-preview.png` (1280×640).

5. **Settings → Branches**: protect `main` — require PR + `ci` and
   `lean (mathlib-verify)` status checks.

6. **Settings → Pages**: Source = GitHub Actions (deploys `docs/` landing).

7. **Discussions**: enable Ideas category for claim audits.

## What the workflows do

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | push/PR | JSON integrity, master numbers, canon tests, release consistency |
| `lean.yml` | push/PR touching `monolith/lean` | full Mathlib build of `QHB_Theorems.lean` + `QHB_T19_Mathlib.lean` + axiom audit |
| `pages.yml` | push to main | deploy animated landing from `docs/` |
| `release.yml` | tag `v*` | Iron-QA gate → zip + SHA256SUMS → GitHub Release |
