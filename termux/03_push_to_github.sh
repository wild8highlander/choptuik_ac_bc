#!/usr/bin/env bash
# ============================================================================
# 03_push_to_github.sh — sync einstein_direct/ into the GitHub repo and push
# Account: wild8highlander  Repo: choptuik_ac_bc (branch main)
#
# What it does:
#   1. Locates (or clones) the local repository copy
#   2. Syncs einstein_direct/ (and termux helper scripts) into it
#   3. Sets up a GitHub PAT once (credential store; never echoed)
#   4. Commits and pushes to main
#
# Usage:
#   bash 03_push_to_github.sh                    # sync + commit + push
#   bash 03_push_to_github.sh "custom message"   # own commit message
#   bash 03_push_to_github.sh --status           # only show git status
# ============================================================================
set -u
GITHUB_USER="wild8highlander"
REPO_NAME="choptuik_ac_bc"
REPO_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}.git"
BRANCH="main"
REPO_DIR="${HOME}/${REPO_NAME}"

step() { printf "==> %s\n" "$*"; }
ok()   { printf "  [OK] %s\n" "$*"; }
warn() { printf "  [WARN] %s\n" "$*"; }
err()  { printf "  [ERROR] %s\n" "$*"; }

HERE="$(cd "$(dirname "$0")" && pwd)"
SRC_ED=""
for cand in "$HERE/einstein_direct" "$HERE/../einstein_direct"; do
  [ -f "$cand/solver.py" ] && SRC_ED="$cand" && break
done
[ -z "$SRC_ED" ] && { err "einstein_direct/ source folder not found next to this script"; exit 1; }

# ─── 1. repository ──────────────────────────────────────────────────────────
if [ -d "$REPO_DIR/.git" ]; then
  ok "repo found: $REPO_DIR"
else
  step "Cloning $REPO_URL into $REPO_DIR"
  git clone "$REPO_URL" "$REPO_DIR" || { err "clone failed (need PAT? see below)"; exit 1; }
fi
cd "$REPO_DIR"

if [ "${1:-}" = "--status" ]; then
  git status && git log --oneline -3 && exit 0
fi

git config user.name  "${GITHUB_USER}"
git config user.email "${GITHUB_USER}@users.noreply.github.com"

# ─── 2. PAT (once) ──────────────────────────────────────────────────────────
CRED_FILE="${HOME}/.git-credentials"
if [ ! -s "$CRED_FILE" ] || ! grep -q "github.com" "$CRED_FILE" 2>/dev/null; then
  step "GitHub Personal Access Token (stored once via credential store)"
  printf "Open this URL in a browser and create a token with 'repo' scope:\n"
  printf "  https://github.com/settings/tokens/new?scopes=repo&description=Termux%%20push\n"
  printf "Paste the token (input hidden): "
  read -rs PAT
  printf "\n"
  [ -z "$PAT" ] && { err "empty token"; exit 1; }
  git config --global credential.helper store
  printf "https://%s:%s@github.com\n" "$GITHUB_USER" "$PAT" > "$CRED_FILE"
  chmod 600 "$CRED_FILE"
  ok "token stored in $CRED_FILE"
fi

# ─── 3. sync module ─────────────────────────────────────────────────────────
step "Syncing einstein_direct/ into the repository"
mkdir -p "$REPO_DIR/einstein_direct"
cp -r "$SRC_ED"/. "$REPO_DIR/einstein_direct"/
# also refresh the termux helpers inside the repo
mkdir -p "$REPO_DIR/termux"
cp -f "$HERE"/0*.sh "$REPO_DIR/termux"/ 2>/dev/null || true
git add einstein_direct termux 2>/dev/null || git add einstein_direct

# ─── 4. commit + push ───────────────────────────────────────────────────────
MSG="${1:-einstein_direct v3: zoom machine v2 (z~5.2), r_floor fix, honest campaign JSON, EN README}"
if git diff --cached --quiet; then
  ok "nothing to commit"
else
  git commit -m "$MSG" || { err "commit failed"; exit 1; }
fi
step "Pushing to origin/$BRANCH"
git push origin "$BRANCH" \
  && ok "pushed: https://github.com/${GITHUB_USER}/${REPO_NAME}" \
  || { warn "push rejected — remote has new commits"; warn "run: git pull --rebase origin $BRANCH && bash $0"; exit 1; }
