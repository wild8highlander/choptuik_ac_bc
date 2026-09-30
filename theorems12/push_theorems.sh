#!/usr/bin/env bash
# ============================================================================
# push_theorems.sh — автопубликация цикла «Двенадцать теорем» (theorems12/, 
# расширенная редакция: 20 теорем × 2 языка, 80 файлов DOCX+PDF)
# в репозиторий wild8highlander/choptuik_ac_bc через Personal Access Token.
#
# БЕЗОПАСНОСТЬ:
#   • PAT читается из переменной окружения GH_PAT или запрашивается скрыто
#     (read -s) — токен НИКОГДА не записывается в файлы и не попадает в
#     историю команд;
#   • пуш выполняется одноразовым URL — токен не сохраняется в .git/config;
#   • после пуша переменная очищается (trap).
#
# Использование:
#   GH_PAT=ghp_xxx  bash push_theorems.sh           # вариант 1: через env
#   bash push_theorems.sh                            # вариант 2: скрытый запрос
#   bash push_theorems.sh --message "свой текст"     # свой commit message
# ============================================================================
set -u

REPO_SLUG="wild8highlander/choptuik_ac_bc"
REPO_URL="https://github.com/${REPO_SLUG}.git"
GH_USER="wild8highlander"
COMMIT_MSG="theorems12: full bilingual monograph cycle extended to 20 theorems (12 canonical + 8 supplementary; EN 1-20 + RU 1-20, DOCX+PDF, 80 files) + EN README block"

# ── аргументы ───────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --message) COMMIT_MSG="$2"; shift 2 ;;
    -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
    *) echo "Неизвестный аргумент: $1 (см. --help)"; exit 2 ;;
  esac
done

# ── пути: скрипт лежит в theorems12/, корень репо — на уровень выше ────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

if [[ ! -d ".git" ]]; then
  echo "ОШИБКА: $REPO_ROOT не является git-репозиторием."
  echo "Сначала клонируйте: git clone ${REPO_URL}"
  exit 1
fi
if [[ ! -d "theorems12" ]]; then
  echo "ОШИБКА: папка theorems12/ не найдена в $REPO_ROOT"
  exit 1
fi

# ── зависимости ─────────────────────────────────────────────────────────────
for tool in git curl; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "ОШИБКА: не найден '$tool'."
    echo "Termux:  pkg install git curl"
    exit 1
  fi
done

# ── PAT: env или скрытый запрос ─────────────────────────────────────────────
if [[ -z "${GH_PAT:-}" ]]; then
  printf "Введите ваш GitHub PAT (ввод скрыт): "
  read -r -s GH_PAT
  echo ""
fi
if [[ -z "$GH_PAT" ]]; then
  echo "ОШИБКА: PAT пуст. Получите токен: GitHub -> Settings -> Developer settings -> Personal access tokens"
  exit 1
fi
trap 'GH_PAT=""; unset GH_PAT' EXIT

# ── [1/5] preflight токена через GitHub API ────────────────────────────────
echo "[1/5] Preflight токена (GitHub API)..."
API_JSON="$(curl -sS --max-time 20 -H "Authorization: token ${GH_PAT}" \
                  -H "Accept: application/vnd.github+json" \
                  https://api.github.com/user 2>&1)" || {
  echo "ОШИБКА: сеть недоступна или GitHub не отвечает."; exit 1; }
LOGIN="$(printf '%s' "$API_JSON" | sed -n 's/.*"login"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)"
if [[ -z "$LOGIN" ]]; then
  echo "ОШИБКА: токен не принят GitHub (проверьте срок действия и scope 'repo')."
  echo "Ответ API (первые строки):"; printf '%s\n' "$API_JSON" | head -3
  exit 1
fi
if [[ "$LOGIN" != "$GH_USER" ]]; then
  echo "ОШИБКА: токен принадлежит аккаунту '$LOGIN', а пуш идёт в ${GH_USER}/${REPO_SLUG##*/}."
  exit 1
fi
echo "      OK: токен аккаунта '$LOGIN' принят."

# ── [2/5] ветка и remote ────────────────────────────────────────────────────
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)"
[[ "$BRANCH" == "HEAD" ]] && BRANCH="main"
if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$REPO_URL"
else
  git remote add origin "$REPO_URL"
fi
echo "[2/5] Ветка: $BRANCH; origin -> $REPO_URL"

# ── [3/5] индексация theorems12/ и README.md ───────────────────────────────
echo "[3/5] Индексация файлов..."
git add theorems12 README.md
if git diff --cached --quiet; then
  echo "      Нечего коммитить: папка theorems12/ и README уже в актуальном состоянии."
  echo "      Проверяю соответствие с GitHub без пуша..."
else
  git -c user.name="${GH_USER}" -c user.email="${GH_USER}@users.noreply.github.com" \
      commit -m "$COMMIT_MSG" || { echo "ОШИБКА коммита."; exit 1; }
  echo "      Коммит создан: $(git rev-parse --short HEAD)"
fi

# ── [4/5] пуш одноразовым URL (токен не persists в config) ─────────────────
echo "[4/5] Пуш в ${GH_USER}/${REPO_SLUG##*/} (ветка $BRANCH)..."
PUSH_URL="https://${GH_USER}:${GH_PAT}@github.com/${REPO_SLUG}.git"
if git push "$PUSH_URL" "HEAD:${BRANCH}" 2>push_stderr.log; then
  rm -f push_stderr.log
  echo "      Push выполнен."
else
  RC=$?
  ERR="$(cat push_stderr.log 2>/dev/null)"; rm -f push_stderr.log
  echo "Пуш не удался (код $RC). Ответ git:"
  printf '%s\n' "$ERR" | sed "s/${GH_PAT}/***PAT***"'/g'
  if printf '%s' "$ERR" | grep -q "non-fast-forward\|rejected"; then
    echo ""
    echo "ПОДСКАЗКА: на GitHub есть более новые коммиты. Выполните:"
    echo "  git pull --rebase origin $BRANCH && bash push_theorems.sh"
  fi
  exit 1
fi

# ── [5/5] верификация через ls-remote ───────────────────────────────────────
echo "[5/5] Верификация (ls-remote)..."
REMOTE_SHA="$(git ls-remote "$PUSH_URL" "refs/heads/${BRANCH}" | cut -f1)"
LOCAL_SHA="$(git rev-parse HEAD)"
if [[ "$REMOTE_SHA" == "$LOCAL_SHA" ]]; then
  echo ""
  echo "УСПЕХ: $BRANCH = ${LOCAL_SHA:0:7} синхронизирован с GitHub."
  echo "Папка theorems12/ опубликована: ${REPO_URL%/}.git -> tree/$BRANCH"
else
  echo "ВНИМАНИЕ: SHA не совпали (remote: ${REMOTE_SHA:0:7}, local: ${LOCAL_SHA:0:7})."
  exit 1
fi
