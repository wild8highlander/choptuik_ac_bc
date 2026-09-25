# INSTALL & PUSH GUIDE — from zero to GitHub on Android (Termux)

**Account:** `wild8highlander` · **Repo:** `choptuik_ac_bc` · **Folder:** `einstein_direct/`

This guide takes you from a bare Android phone to a pushed, up-to-date
`einstein_direct/` folder in your GitHub repo. No prior Linux experience is
assumed. Total time: 20–40 minutes (mostly waiting for installs).

---

## 0. What is in this archive

```
choptuik_einstein_direct_v4/
├── README.md                  ← this overview (start here)
├── INSTALL_AND_PUSH.md        ← this file (Termux step-by-step)
├── einstein_direct/           ← THE MODULE (code + results + reports + big README)
│   ├── README_EN.md           ← the long detailed English README (14 sections)
│   ├── README.md              ← short RU pointer
│   ├── sympy_derivation.py    ← Hilbert action → Einstein equations (machine-verified)
│   ├── solver.py              ← double-null characteristic solver (+ v3.2 spinor closure)
│   ├── zoom_solver.py         ← multi-zoom regridding machine
│   ├── zoom_campaign.py       ← v2 protocol campaign
│   ├── zoom_campaign_v3.py    ← v3.2 protocol campaign (spinor diagnostics)
│   ├── spinor_analysis.py     ← π/15 & π/30 spinor module (parity A/B, R1–R4)
│   ├── spinor_figures.py      ← spinor figures (RU/EN)
│   ├── choptuik_scaling.py    ← fixed-grid bisection A* + mass scaling
│   ├── roberts_test.py        ← exact-solution convergence test
│   ├── figures.py             ← publication figures RU/EN
│   ├── report_ru.pdf/.tex     ← 7-page RU report
│   ├── report_en.pdf/.tex     ← 7-page EN report
│   ├── tests/                 ← 5 regression tests (pytest)
│   ├── results/               ← all JSON results
│   └── figures/fig_ru, fig_en ← 300 dpi PNG figures
└── termux/                    ← helper scripts (see §5)
    ├── 01_termux_install.sh   ← installs everything into Termux
    ├── 02_termux_run.sh       ← runs tests + campaigns (full/quick)
    ├── 03_push_to_github.sh   ← syncs into the repo clone and pushes
    ├── choptuik_push.sh       ← same as 03 (alias kept for compatibility)
    └── install_shortcut.sh    ← optional: adds a `choptuik` command
```

Everything is plain Python (numpy/scipy/sympy/pytest) — no GPU, no docker,
no root. A phone with 2 GB RAM is enough.

---

## 1. Install Termux (once)

1. Install **Termux from F-Droid**: open
   `https://f-droid.org/packages/com.termux/` in your Android browser and
   download the APK. **Do not** use the Play Store build (outdated, broken
   packages).
2. Open Termux. Allow the notification permission if asked.
3. Update the package index:

```bash
pkg update -y && pkg upgrade -y
```

> If `pkg` is unknown, run `apt update && apt install -y proot` first, or
> reinstall Termux from F-Droid.

## 2. Install the toolchain (once)

The automated way (recommended):

```bash
# copy the archive to the phone, then in Termux:
cd ~/storage/downloads        # or wherever you put it
unzip choptuik_einstein_direct_v4.zip -d ~/
bash ~/choptuik_einstein_direct_v4/termux/01_termux_install.sh
```

The manual way (what the script does):

```bash
pkg install -y python git clang libjpeg-turbo libffi
pip install --upgrade pip
pip install numpy scipy sympy pytest
```

Notes:
- If `pip install numpy` tries to compile forever, use the Termux packages
  instead: `pkg install -y python-numpy python-scipy` and then
  `pip install sympy pytest`.
- `clang` and `libjpeg-turbo` are only needed if pip builds wheels.

## 3. Get the code into the repo clone (once)

```bash
cd ~
git clone https://github.com/wild8highlander/choptuik_ac_bc.git
# sync this version of the module into the clone (03 script does exactly this):
bash ~/choptuik_einstein_direct_v4/termux/03_push_to_github.sh --status
```

## 4. Authenticate with GitHub (once)

Two options.

**Option A — GitHub CLI (easiest):**

```bash
pkg install -y gh
gh auth login
# choose: GitHub.com → HTTPS → Login with a web browser (or paste a token)
```

**Option B — Personal Access Token (PAT):**

1. On any device: GitHub → Settings → Developer settings →
   Personal access tokens → **Generate new token (classic)**.
2. Tick the `repo` scope. Copy the token.
3. In Termux the push script will ask for it once and store it:

```bash
git config --global credential.helper store
# the next push asks: Username: wild8highlander, Password: <paste the PAT>
```

The `03_push_to_github.sh` script handles this automatically and never
echoes the token.

## 5. Run and push

```bash
bash ~/choptuik_einstein_direct_v4/termux/02_termux_run.sh          # full: tests + campaigns
bash ~/choptuik_einstein_direct_v4/termux/02_termux_run.sh --quick  # ~15 min reduced
bash ~/choptuik_einstein_direct_v4/termux/03_push_to_github.sh      # sync + commit + push
bash ~/choptuik_einstein_direct_v4/termux/03_push_to_github.sh "my commit message"
```

What the push script does: finds `~/choptuik_ac_bc` (or clones it), copies
`einstein_direct/` from this archive into the clone, `git add`s it, commits
with a timestamped message, and pushes to `main`. Re-run it any time you
want to publish the latest results.

**Expected runtimes on a phone** (A53-class): validation 1–2 s · derivation
3–5 s · Roberts test 20–60 s · fixed-grid campaign 30–90 min · zoom v2/v3
campaigns 20–60 min · spinor module 10–30 min. Use `--quick` first.

## 6. Troubleshooting

| Symptom | Fix |
|---|---|
| `pip` fails building numpy/scipy | `pkg install python-numpy python-scipy` |
| `git push` asks for password forever | you pasted the GitHub *password*; you need a **PAT** (§4B) |
| `gh: command not found` | `pkg install gh` (or use option B) |
| `unzip: command not found` | `pkg install unzip` |
| Phone sleeps and kills the run | `termux-wake-lock` before long runs (`pkg install termux-api` if needed) |
| `Storage permission denied` | `termux-setup-storage`, then re-open Termux |

## 7. What to check after pushing

Open `https://github.com/wild8highlander/choptuik_ac_bc/tree/main/einstein_direct`
and verify: `README_EN.md` (the long one), `results/spinor_analysis.json`,
`results/zoom_campaign_v3.json`, `figures/fig_en/fig_spinor.png`.

Then read `einstein_direct/README_EN.md` sections **10** (v3.2 spinor center
closure) and **11** (the π/15, π/30 analysis: relations R1–R4 and the honest
data-depth limits) — these are the new results of this session.
