#!/usr/bin/env bash
# ============================================================================
#  choptuik_push.sh — автоматическая публикация исправлений в GitHub
#  Репозиторий: https://github.com/wild8highlander/choptuik_ac_bc (main)
#  Пользователь: wild8highlander
#
#  ЧТО ДЕЛАЕТ:
#    1. Находит локальный клон репозитория
#    2. Проверяет/настраивает PAT-токен GitHub (один раз, потом помнит)
#    3. Добавляет все изменения, делает коммит
#    4. Пушит в origin main
#
#  ИСПОЛЬЗОВАНИЕ:
#    bash choptuik_push.sh                     # обычный коммит + push
#    bash choptuik_push.sh "моё сообщение"     # своё сообщение коммита
#    bash choptuik_push.sh --force             # ЖЁСТКИЙ push (перезапишет
#                                              # удалённую main вашей версией)
#    bash choptuik_push.sh --status            # только показать статус
#
#  ФОРС (--force) применяется ТОЛЬКО по явному флагу — без вопросов и не
#  автоматически. Если обычный push отклонён, скрипт подскажет, что делать.
# ============================================================================
set -u

GITHUB_USER="wild8highlander"
REPO_NAME="choptuik_ac_bc"
REPO_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}.git"
BRANCH="main"
CRED_FILE="${HOME}/.git-credentials"
PAT_HINT="https://github.com/settings/tokens/new?scopes=repo&description=Termux%20choptuik%20push"

# ─── Оформление вывода ──────────────────────────────────────────────────────
if [ -t 1 ]; then
    C_G="\033[1;32m"; C_R="\033[1;31m"; C_Y="\033[1;33m"; C_B="\033[1;36m"; C_0="\033[0m"
else
    C_G=""; C_R=""; C_Y=""; C_B=""; C_0=""
fi
step()  { printf "${C_B}==>${C_0} %s\n" "$*"; }
ok()    { printf "${C_G}  [OK] %s${C_0}\n" "$*"; }
warn()  { printf "${C_Y}  [ВНИМАНИЕ] %s${C_0}\n" "$*"; }
err()   { printf "${C_R}  [ОШИБКА] %s${C_0}\n" "$*"; }
die()   { err "$*"; exit 1; }

FORCE=0
DO_STATUS=0
COMMIT_MSG=""
for arg in "$@"; do
    case "$arg" in
        --force)    FORCE=1 ;;
        --status)   DO_STATUS=1 ;;
        --help|-h)  sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *)          COMMIT_MSG="$arg" ;;
    esac
done

[ -z "${COMMIT_MSG}" ] && COMMIT_MSG="fix: termux pack — CLI EOF/mode fixes, audit_transfer graceful playwright, CI/Lint badge repairs ($(date +%Y-%m-%d))"

# ─── Шаг 1. Проверка окружения ──────────────────────────────────────────────
echo ""
echo "=============================================================="
echo "  ПУШ ИСПРАВЛЕНИЙ: ${GITHUB_USER}/${REPO_NAME} -> ${BRANCH}"
echo "=============================================================="

step "1/6 Проверяю окружение (git, сеть, путь репозитория)"
command -v git >/dev/null 2>&1 || die "git не установлен. Выполните: pkg install git  — и запустите скрипт снова."

# Где лежит репозиторий? Порядок поиска:
#   a) переменная окружения CHOPTUIK_REPO
#   b) папка, из которой запущен скрипт (если там .git)
#   c) папка, в которую скрипт был установлен установщиком
#   d) ~/choptuik_ac_bc  (папка по умолчанию из инструкции)
#   e) текущая директория
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd)"
CANDIDATES="${CHOPTUIK_REPO:-}
${SCRIPT_DIR}
${INSTALL_REPO_DIR:-}
${HOME}/${REPO_NAME}
$(pwd)"

REPO_DIR=""
while IFS= read -r cand; do
    [ -n "$cand" ] || continue
    if [ -d "${cand}/.git" ]; then REPO_DIR="$(cd "$cand" && pwd)"; break; fi
done <<EOF
$CANDIDATES
EOF

[ -n "$REPO_DIR" ] || die "Клон ${REPO_NAME} не найден.
  Скопируйте этот скрипт в папку репозитория ЛИБО выполните:
    git clone ${REPO_URL} ~/${REPO_NAME}
  и запустите: bash ~/${REPO_NAME}/termux/choptuik_push.sh"
cd "$REPO_DIR" || die "Не удалось войти в папку $REPO_DIR"
ok "Репозиторий: ${REPO_DIR}"

# Защита от «dubious ownership» (бывает, если папка создана другим приложением)
if ! git rev-parse --git-dir >/dev/null 2>&1; then
    warn "Git жалуется на владение папкой (dubious ownership) — исправляю…"
    git config --global --add safe.directory "$REPO_DIR" 2>/dev/null \
        || die "Не удалось добавить safe.directory. Выполните вручную:
  git config --global --add safe.directory ${REPO_DIR}"
    git rev-parse --git-dir >/dev/null 2>&1 || die "git по-прежнему не работает в этой папке."
fi

# Проверяем remote origin — если кривой, чиним
CUR_URL="$(git remote get-url origin 2>/dev/null || echo "")"
case "$CUR_URL" in
    *"${REPO_NAME}"*) ok "origin: ${CUR_URL}" ;;
    *) git remote remove origin 2>/dev/null; git remote add origin "$REPO_URL"
       ok "Настроил origin -> ${REPO_URL}" ;;
esac

# ─── Шаг 2. Ветка ───────────────────────────────────────────────────────────
step "2/6 Проверяю ветку ${BRANCH}"
CUR_BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")"
[ "$CUR_BRANCH" = "$BRANCH" ] || {
    warn "Сейчас вы в ветке «${CUR_BRANCH}», переключаюсь на «${BRANCH}»…"
    git checkout -B "$BRANCH" || die "Не удалось переключиться на ветку ${BRANCH}."
}
ok "Ветка: ${BRANCH}"

# ─── Шаг 3. PAT-токен ───────────────────────────────────────────────────────
step "3/6 Проверяю вход в GitHub (PAT-токен)"
git config --global credential.helper store

have_cred() {
    [ -f "$CRED_FILE" ] && grep -q "https://${GITHUB_USER}:[^@]*@github.com" "$CRED_FILE" 2>/dev/null
}

if ! have_cred; then
    echo ""
    echo "  ┌──────────────────────────────────────────────────────────────┐"
    echo "  │ Нужен Personal Access Token (PAT) — это пароль для программ. │"
    echo "  │ 1. Откройте в браузере ссылку (scope repo уже выбран):       │"
    echo "  │    ${PAT_HINT}"
    echo "  │ 2. Нажмите зелёную кнопку Generate token.                    │"
    echo "  │ 3. Скопируйте токен (ghp_...) и вставьте ниже.               │"
    echo "  └──────────────────────────────────────────────────────────────┘"
    printf "  Вставьте токен и нажмите Enter > "
    read -r PAT
    PAT="$(printf '%s' "$PAT" | tr -d '[:space:]')"
    [ -n "$PAT" ] || die "Пустой токен. Запустите скрипт ещё раз."
    case "$PAT" in
        ghp_*|github_pat_*|gho_*|ghu_*|ghs_*) : ;;
        *) warn "Токен не начинается с ghp_/github_pat_ — проверьте, что скопировали его целиком." ;;
    esac
    [ "${#PAT}" -ge 20 ] || die "Токен слишком короткий — скопирован не полностью. Запустите снова."
    # Проверяем токен ДО записи (ls-remote — быстрая сетевая проверка прав)
    step "    Проверяю токен на сервере GitHub…"
    if GIT_TERMINAL_PROMPT=0 git ls-remote "https://${GITHUB_USER}:${PAT}@github.com/${GITHUB_USER}/${REPO_NAME}.git" HEAD >/dev/null 2>&1; then
        ok "Токен принят GitHub."
    else
        err "GitHub отклонил токен (неверный, просрочен или нет галочки repo)."
        echo "     Создайте новый: ${PAT_HINT}"
        exit 1
    fi
    mkdir -p "$(dirname "$CRED_FILE")"
    grep -v "https://${GITHUB_USER}:[^@]*@github.com" "$CRED_FILE" 2>/dev/null > "${CRED_FILE}.tmp" || true
    mv "${CRED_FILE}.tmp" "$CRED_FILE"
    printf 'https://%s:%s@github.com\n' "$GITHUB_USER" "$PAT" >> "$CRED_FILE"
    chmod 600 "$CRED_FILE"
    unset PAT
    ok "Токен сохранён в ${CRED_FILE} (права 600, доступен только вам)."
else
    ok "PAT уже сохранён — используем его."
fi

# ─── Шаг 4. git identity + изменения ────────────────────────────────────────
step "4/6 Готовлю коммит"
GIT_NAME="$(git config user.name  || true)"
GIT_MAIL="$(git config user.email || true)"
[ -n "$GIT_NAME" ] || { git config user.name  "$GITHUB_USER";                    warn "user.name был пуст — поставил ${GITHUB_USER}"; }
[ -n "$GIT_MAIL" ] || { git config user.email "${GITHUB_USER}@users.noreply.github.com"; warn "user.email был пуст — поставил noreply-адрес"; }

if [ "$DO_STATUS" = "1" ]; then
    git status
    exit 0
fi

git add -A
if [ -z "$(git status --porcelain 2>/dev/null)" ]; then
    AHEAD="$(git rev-list --count "origin/${BRANCH}..${BRANCH}" 2>/dev/null || echo "?")"
    if [ "$AHEAD" = "0" ]; then
        ok "Изменений нет и всё уже отправлено — пушить нечего. Готово."
        exit 0
    fi
    warn "Новых изменений нет, но есть непушенные коммиты ($AHEAD) — отправляю их."
else
    git commit -m "$COMMIT_MSG" || die "Коммит не создан (см. сообщение выше)."
    ok "Коммит создан: $(git log -1 --oneline)"
fi

# ─── Шаг 5. Push ────────────────────────────────────────────────────────────
step "5/6 Отправляю в GitHub (push origin ${BRANCH})"
PUSH_OUT="$(git push origin "$BRANCH" 2>&1)"
PUSH_RC=$?
echo "$PUSH_OUT" | sed 's/^/    /'

if [ $PUSH_RC -eq 0 ]; then
    ok "Push успешный!"
else
    case "$PUSH_OUT" in
        *"non-fast-forward"*|*"rejected"*|*"fetch first"*|*"behind"*|*"contains work"*)
            echo ""
            err "GitHub отклонил push: на сервере есть коммиты, которых нет у вас."
            if [ $FORCE -eq 1 ]; then
                step "    Флаг --force активен — перезаписываю удалённую ветку…"
                if git push --force origin "$BRANCH" 2>&1 | sed 's/^/    /'; then
                    ok "Force push выполнен!"
                else
                    die "Force push не прошёл — проверьте сообщение выше."
                fi
            else
                echo "  ВАРИАНТЫ (выберите один):"
                echo "   1) Забрать изменения сервера и наложить свои сверху:"
                echo "        git pull --rebase origin ${BRANCH} && bash $0"
                echo "   2) ЖЁСТКО перезаписать сервер вашей версией (чужие правки"
                echo "      на GitHub будут потеряны!) — вы выбрали делать это"
                echo "      только по флагу, поэтому запустите:"
                echo "        bash $0 --force"
            fi
            exit 1 ;;
        *"Authentication"*|*"403"*|*"could not read Username"*|*"terminal prompts disabled"*)
            err "GitHub не принял токен (403/аутентификация)."
            echo "   Чинится так:"
            echo "     rm ${CRED_FILE}   # стереть старый токен"
            echo "     bash $0           # скрипт спросит новый PAT"
            exit 1 ;;
        *"Could not resolve host"*|*"network"*|*"Failed to connect"*)
            err "Нет доступа к интернету. Проверьте сеть и запустите скрипт ещё раз."
            exit 1 ;;
        *)
            err "Push не прошёл (код $PUSH_RC). Сообщение выше — скопируйте его, если попросите помощи."
            exit 1 ;;
    esac
fi

# ─── Шаг 6. Итог ────────────────────────────────────────────────────────────
step "6/6 Готово"
echo "  Что дальше:"
echo "   • Бейджи CI/Lint на GitHub обновятся через 1–5 минут после пуша:"
echo "     https://github.com/${GITHUB_USER}/${REPO_NAME}/actions"
echo "   • Если бейдж «завис» серым — откройте Actions → выберите workflow"
echo "     → Enable/Re-run (в новых workflows включён ручной запуск)."
echo ""
