#!/usr/bin/env bash
# ============================================================================
#  install_shortcut.sh — ставит choptuik-push в «доверенную папку» Termux
#
#  «Доверенная папка» — это ~/.shortcuts. Скрипты из неё запускаются
#  приложением Termux:Widget ОДНИМ тапом с рабочего стола, без вопросов
#  и без открытия терминала вручную.
#
#  Что делает установщик:
#    1. Создаёт ~/.shortcuts, если её нет
#    2. Копирует choptuik_push.sh туда с ЗАПИСАННЫМ путём к репозиторию
#    3. Делает файлы исполняемыми
#    4. Подсказывает, как добавить кнопку на рабочий стол
# ============================================================================
set -u

SHORTCUTS_DIR="${HOME}/.shortcuts"
SCRIPT_NAME="choptuik-push.sh"

# Ищем исходный choptuik_push.sh рядом с этим установщиком
HERE="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd)"
SRC="${HERE}/choptuik_push.sh"

# Где реально лежит репозиторий (чтобы прописать в ярлык)
REPO_DIR=""
while IFS= read -r cand; do
    [ -n "$cand" ] || continue
    if [ -d "${cand}/.git" ]; then REPO_DIR="$(cd "$cand" && pwd)"; break; fi
done <<EOF
${CHOPTUIK_REPO:-}
${HERE}
${HOME}/choptuik_ac_bc
$(pwd)
EOF

if [ ! -f "$SRC" ]; then
    # Случай «установщик уже скопирован в ~/.shortcuts» — берём скрипт оттуда же
    if [ -f "${SHORTCUTS_DIR}/${SCRIPT_NAME}" ]; then
        SRC="${SHORTCUTS_DIR}/${SCRIPT_NAME}"
    else
        echo "[ОШИБКА] Рядом с установщиком нет choptuik_push.sh"
        echo "  Распакуйте ZIP целиком в корень репозитория и запустите:"
        echo "    bash termux/install_shortcut.sh"
        exit 1
    fi
fi

[ -n "$REPO_DIR" ] || REPO_DIR="${HOME}/choptuik_ac_bc"

echo ""
echo "=============================================================="
echo "  УСТАНОВКА КНОПКИ ПУША В ДОВЕРЕННУЮ ПАПКУ TERMUX"
echo "=============================================================="
echo "  Источник скрипта : ${SRC}"
echo "  Путь репозитория : ${REPO_DIR}"
echo "  Папка ярлыков    : ${SHORTCUTS_DIR}"
echo ""

# 1. Создаём доверенную папку
if [ ! -d "$SHORTCUTS_DIR" ]; then
    mkdir -p "$SHORTCUTS_DIR" || { echo "[ОШИБКА] не удалось создать ${SHORTCUTS_DIR}"; exit 1; }
    echo "[OK] Создана папка ~/.shortcuts (доверенная папка Termux:Widget)"
else
    echo "[OK] ~/.shortcuts уже существует"
fi

# 2. Копируем push-скрипт и вшиваем в него путь к репозиторию.
#    Скрипт ищет репозиторий в переменной INSTALL_REPO_DIR — добавляем её
#    сразу после строки BRANCH="main".
if grep -q "^INSTALL_REPO_DIR=" "$SRC"; then
    # Переустановка: путь уже вшит — просто обновляем его
    sed "s|^INSTALL_REPO_DIR=.*|INSTALL_REPO_DIR=\"${REPO_DIR}\"   # <- вшито установщиком|" \
        "$SRC" > "${SHORTCUTS_DIR}/${SCRIPT_NAME}.tmp"
else
    sed "s|^BRANCH=\"main\"|BRANCH=\"main\"\nINSTALL_REPO_DIR=\"${REPO_DIR}\"   # <- вшито установщиком|" \
        "$SRC" > "${SHORTCUTS_DIR}/${SCRIPT_NAME}.tmp"
fi
mv "${SHORTCUTS_DIR}/${SCRIPT_NAME}.tmp" "${SHORTCUTS_DIR}/${SCRIPT_NAME}"
chmod +x "${SHORTCUTS_DIR}/${SCRIPT_NAME}"
echo "[OK] Ярлык установлен: ~/.shortcuts/${SCRIPT_NAME}"

# 3. Копия установщика рядом — чтобы можно было переустановить в один тап
cp -f "$0" "${SHORTCUTS_DIR}/install-choptuik-shortcut.sh" 2>/dev/null && \
    chmod +x "${SHORTCUTS_DIR}/install-choptuik-shortcut.sh"

# 4. Проверка bash в Termux
command -v git >/dev/null 2>&1 || {
    echo ""
    echo "[ВНИМАНИЕ] git ещё не установлен. Перед первым пушем выполните:"
    echo "    pkg update -y && pkg install git -y"
}

echo ""
echo "=============================================================="
echo "  ГОТОВО! Как теперь пушить одним тапом:"
echo "=============================================================="
echo "  1. Установите из F-Droid приложение «Termux:Widget»"
echo "     (тот же источник, откуда ставили Termux!)."
echo "  2. На рабочем столе Android: долгий тап → Виджеты →"
echo "     «Termux:Widget» → выберите «choptuik-push.sh»."
echo "  3. Тап по кнопке = скрипт сам сделает коммит и push."
echo "     Первый раз спросит PAT-токен, дальше — молча и сам."
echo ""
echo "  Без виджета тоже можно, прямо в Termux:"
echo "    bash ~/.shortcuts/${SCRIPT_NAME}"
echo "    bash ~/.shortcuts/${SCRIPT_NAME} --force   # только если нужен форс"
echo "    bash ~/.shortcuts/${SCRIPT_NAME} --status  # просто статус"
echo ""
