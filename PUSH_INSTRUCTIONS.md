# 📤 Публикация обновления «Аудит и перенос» v2.0 в ваш GitHub

Репозиторий: **https://github.com/wild8highlander/choptuik_ac_bc**
Ваш логин уже вписан во все скрипты: **wild8highlander**. От вас — только PAT.

---

## Состав обновления (что попадёт в репозиторий)

| Файл/папка | Что это |
|---|---|
| `audit_transfer/` | Папка-приложение: README (RU), Python-ядро, Julia-порт, фигуры, JSON-результаты, PDF «Аудит и перенос» (11 стр., v2.0) + LaTeX-исходники |
| `audit_transfer/lemma_article/` | **НОВОЕ v2.0:** отдельная статья по лемме Ш.3 — `Lemma_SH3_Ustojchivost.pdf` (10 стр.) + LaTeX-исходники |
| `docs/monograph/Choptyuk_Monograph_RU_Final.docx` | Исправленная исходная монография: ошибки E2–E7 (числа), фикс кода E1 (знак A), приложение «ПРИЛОЖЕНИЕ D. ERRATA» |
| `docs/monograph/Choptyuk_Monograph_RU_Final.pdf` | **НОВОЕ v2.0:** монография пересобрана в PDF из исправленного docx (60 стр., ERRATA внутри) |
| `docs/monograph/Choptyuk_Monograph_EN_Final.docx` | Фикс кода E1 + «APPENDIX D. ERRATA» (числа в этом издании уже были верны) |
| `docs/monograph/Choptyuk_Monograph_EN_Final.pdf` | **НОВОЕ v2.0:** EN-монография пересобрана в PDF из исправленного docx (59 стр.; старый PDF в репо был битым) |
| `docs/qcd_bridge/choptyuk_qcd_bridge.tex` | Обновлён кавеат о статусе c_K3 (получен статус «derived (leading order)») |
| `.github/workflows/verify-audit-transfer.yml` | **НОВОЕ v2.0:** CI-автозапуск верификации (Python + Julia, артефакты, кросс-проверка) |
| `README.md` | Косметика: раздел «Audit & Transfer Appendix» + строка в структуре проекта |
| `CHANGELOG.md` | Записи `[2.2.0]` и `[2.2.1] - 2026-09-11` |
| `worklog.md` | Записи редакторской верификации |
| `.gitignore` | + строка `_originals_backup/` |
| `push_to_github.sh` / `push_to_github.bat` | Скрипты публикации (этот файл описывает их) |

**Что изменилось в v2.0 по сути:** часть (i) леммы Ш.3 усилена до острой
теоремы следа `F ≥ 5n/7` при всех n (в v1.0 цепочка «≥ n/2» содержала
ошибку — минимум трёхчлена равен n/3; острая теорема исправляет и
усиливает, закрывая открытый в v1.0 вопрос о глобальном минимуме);
наблюдение DSI-4: `c_K3 = 27/672 = 3³/(4·|PSL(2,7)|)` — совпадение с
измеренным +0.0025%. Подробности — в `CHANGELOG.md`.

> Примечание о пересобранных PDF монографий: растровые иллюстрации в
> PDF-рендере прорежены до 2600 px по длинной стороне (≈350–400 dpi при
> ширине рисунка 15–17 см — визуально неотличимо при печати); docx-
> источники остались полноразмерными. Текст и вёрстка — из исправленных
> docx. Старый EN-PDF в репозитории был битым (обрезан) — замена исправляет
> и это.

**Лицензия не изменялась.** Оригиналы docx до правок лежат в
`docs/monograph/_originals_backup/` и в git-истории — этот каталог исключён
из публикации через `.gitignore`.

---

## Способ 1 — автоматом (рекомендуется)

### Шаг 0. Распакуйте архив поверх клона

```bash
# у вас уже есть клон; если нет — склонируйте:
git clone https://github.com/wild8highlander/choptuik_ac_bc.git
cd choptuik_ac_bc

# распакуйте ZIP-архив обновления В КОРЕНЬ клона (с заменой файлов):
unzip -o choptuik_ac_bc_update_audit_transfer.zip -d .
```

> Windows: откройте ZIP, выделите всё и перетащите в папку клона с заменой.

### Шаг 1. Создайте PAT (если ещё нет)

1. Откройте https://github.com/settings/tokens
2. **Classic токен (проще всего):** `Generate new token (classic)` →
   отметьте скоуп **`repo`** → `Generate token` → скопируйте
   (начинается с `ghp_`).
   *Fine-grained тоже подходит:* Repository access → Only `choptuik_ac_bc` →
   Permissions → Contents → **Read and write**.
3. Срок действия — на ваш выбор (30/60/90 дней, или no expiration).

### Шаг 2. Запустите скрипт

```bash
bash push_to_github.sh
```

Windows: двойной клик по `push_to_github.bat` (или в cmd: `push_to_github.bat`).

Скрипт сам:
- проверит, что вы в корне клона `choptuik_ac_bc`;
- попросит вставить PAT (ввод скрыт; можно заранее `export GH_PAT=ghp_...`);
- проиндексирует **только** файлы из таблицы выше (ничего лишнего);
- сделает коммит с подробным сообщением и запушит в `origin/main`;
- **сразу после пуша удалит токен из `.git/config`** — токен не остаётся на диске.

### Шаг 3. Проверьте результат

Скрипт напечатает ссылку вида
`https://github.com/wild8highlander/choptuik_ac_bc/commit/<hash>` — откройте и
убедитесь. На главной репозитория появится раздел «Audit & Transfer Appendix»,
а папка `audit_transfer/` откроется с рендерящимся README и фигурами.

---

## Способ 2 — вручную (если хочется полной прозрачности)

```bash
cd choptuik_ac_bc
# распакуйте архив поверх (см. Шаг 0)

git config core.fileMode false          # убрать шум прав доступа
git add audit_transfer \
        docs/monograph/Choptyuk_Monograph_RU_Final.docx \
        docs/monograph/Choptyuk_Monograph_EN_Final.docx \
        docs/qcd_bridge/choptyuk_qcd_bridge.tex \
        README.md CHANGELOG.md worklog.md .gitignore \
        push_to_github.sh push_to_github.bat PUSH_INSTRUCTIONS.md

git commit -m "feat(audit_transfer): editorial verification appendix v1.0"
git push origin main
# при запросе логина: имя — wild8highlander, пароль — ВАШ PAT (не пароль GitHub!)
```

## Способ 3 — GitHub Desktop / любая GUI

1. Распакуйте архив поверх клона.
2. GUI покажет изменённые файлы — убедитесь, что в списке только файлы из
   таблицы выше, нажмите «Commit to main».
3. `Fetch origin` → `Push origin`. Логин: `wild8highlander`, пароль — PAT
   (GitHub Desktop обычно уже авторизован вашим аккаунтом — тогда ничего
   вводить не нужно).

---

## Если пуш не проходит (частые случаи)

| Симптом | Причина и что делать |
|---|---|
| `Authentication failed` / 401 | PAT неверный или истёк → создайте новый на https://github.com/settings/tokens и вставьте заново |
| `403` / `permission denied` | У classic-токена нет скоупа `repo`; у fine-grained нет Contents: Read and write → поправьте права токена |
| `repository not found` | Опечатка в имени репо/аккаунте (проверьте: `git remote -v` — должно быть `.../wild8highlander/choptuik_ac_bc.git`) |
| SSO-заглушка (корп. аккаунт) | Settings → SSO у токена → «Authorize» для вашей организации |
| `protected branch` / `rejected` | Ветка `main` защищена → пушьте в ветку `audit-transfer-v1` (`git push origin main:audit-transfer-v1`) и откройте PR |
| `remote: invalid username or password` | Вы вставили пароль GitHub вместо PAT — нужен именно токен (ghp_/github_pat_) |

**Безопасность:** скрипты не сохраняют токен: после пуша remote сбрасывается на
`https://github.com/wild8highlander/choptuik_ac_bc.git`. Если всё же вставили
токен куда-то ещё — отзовите его на https://github.com/settings/tokens.

---

## Что сделать после пуша (опционально, 5 минут)

1. **CI-верификация**: после пуша автоматически запустится новый воркфлоу
   `Verify Audit & Transfer` (`.github/workflows/verify-audit-transfer.yml`) —
   Python + Julia проверки, JSON-артефакты и кросс-проверка Python↔Julia;
   запустить вручную можно с вкладки Actions → «Run workflow». Существующие
   workflow репозитория не изменялись.
2. **Topics/описание репо**: добавьте топики `sofic-groups`, `DSI`,
   `verification` — по желанию.
3. **Release**: если пользуетесь релизами, создайте `v2.2.0` с заметками из
   `CHANGELOG.md` (строка `[2.2.0] - 2026-09-11` уже готова).
4. **Zenodo**: новый коммит можно запросить в качестве новой версии DOI
   (обычно автоматически, если включён Zenodo-интеграция).

---

## Как проверить содержимое до пуша (перед просмотром diff)

```bash
git diff --stat HEAD                                   # что изменится
python3 audit_transfer/python/run_all.py               # полная проверка (~3–5 мин)
cd audit_transfer/julia && julia audit_transfer.jl     # Julia-порт (~2–3 мин)
```

Оба прогона детерминированы: повторный запуск даёт побитово те же JSON.
