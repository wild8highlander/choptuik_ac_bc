# Запуск dsi_lab на Android через Termux — пошаговая инструкция

Всё считается **на самом телефоне**: тесты (~3 мин) и все 7 экспериментов
(~10-25 мин). Интернет нужен только на шагах 1-2 и 4 (push на GitHub).

## 1. Установка Termux

Устанавливайте Termux **только с F-Droid или GitHub Releases**
(версия из Google Play устарела и сломана):

- F-Droid: https://f-droid.org/packages/com.termux/
- GitHub: https://github.com/termux/termux-app/releases (файл `...arm64.apk`
  для большинства современных телефонов)

## 2. Базовые пакеты

Откройте Termux и выполните (копируйте строку целиком):

```bash
pkg update -y && pkg upgrade -y
pkg install -y python git make clang libjpeg-turbo libpng freetype pkg-config binutils
python3 -m pip install --upgrade pip wheel setuptools
```

`clang/binutils` нужны, если какой-то пакет pip решит собираться из исходников.

## 3. Установка Python-зависимостей

**Вариант А (обычно срабатывает):**

```bash
cd /путь/к/dsi_lab          # или: cd ~/dsi_lab
python3 -m pip install -r requirements.txt
```

`numpy` и `matplotlib` ставятся колесами, `scipy` может собираться 5-20 минут —
это нормально, дождитесь.

**Вариант Б (быстрее — предсобранные пакеты Termux):**

```bash
pkg install -y python-numpy python-scipy
python3 -m pip install matplotlib pytest
```

**Вариант В (если matplotlib из pip уперся):**

```bash
pkg install -y tur-repo
pkg install -y python-matplotlib
python3 -m pip install pytest
```

Проверка:

```bash
python3 -c "import numpy, scipy, matplotlib, pytest; print('OK')"
```

## 4. Перенос папки dsi_lab в репозиторий и push

### 4.1. Получить пакет на телефон

Если у вас есть `dsi_lab_github.zip`:

```bash
termux-setup-storage            # разрешит доступ к /sdcard (спросит разрешение)
cp /sdcard/Download/dsi_lab_github.zip ~/
cd ~ && unzip dsi_lab_github.zip
cd ~/dsi_lab
```

(если `unzip` нет: `pkg install -y unzip`)

### 4.2. Запустить и убедиться, что всё работает

```bash
python3 -m pytest tests/ -q     # должно быть: N passed
python3 run_all.py              # полная верификация (10-25 мин)
```

Чтобы телефон не засыпал во время счёта:

```bash
termux-wake-lock                # включить (отключить: termux-wake-unlock)
```

### 4.3. Запушить в ваш GitHub-репозиторий

**Способ 1 — через GitHub CLI (проще всего с авторизацией):**

```bash
pkg install -y gh
gh auth login                   # выберите: GitHub.com → HTTPS → Login with a web browser
gh repo clone <ваш-логин>/choptuik_ac_bc ~/repo
cp -r ~/dsi_lab ~/repo/
cd ~/repo
git add dsi_lab
git commit -m "Add dsi_lab: 7 DSI experiments + pytest suite + reports (RU/EN)"
git push
```

**Способ 2 — чистый git с Personal Access Token:**

1. На GitHub: Settings → Developer settings → Personal access tokens →
   Tokens (classic) → Generate new token, отметьте `repo`;
2. Скопируйте токен (показывается один раз);

```bash
git config --global user.name  "Ваше Имя"
git config --global user.email "you@example.com"
gh repo clone <ваш-логин>/choptuik_ac_bc ~/repo   # или без gh:
# git clone https://<ваш-логин>:<ТОКЕН>@github.com/<ваш-логин>/choptuik_ac_bc.git ~/repo
cp -r ~/dsi_lab ~/repo/
cd ~/repo
git add dsi_lab && git commit -m "Add dsi_lab" && git push
# логин/пароль при push: логин = ваш логин, пароль = ТОКЕН (не пароль GitHub!)
```

**Способ 3 — без git на телефоне (через браузер):**

1. Откройте https://github.com/<ваш-логин>/choptuik_ac_bc;
2. Add file → Upload files;
3. Перетащите **содержимое** папки `dsi_lab` (в Chrome на Android доступен
   выбор папки; файлы лягут в корень репо или в подпапку через
   web-редактор: создайте файл `dsi_lab/README.md` — GitHub создаст папку);
4. Commit changes.

Этот способ медленнее для ~50 файлов — рекомендуются способы 1-2.

## 5. Частые проблемы

| Симптом | Решение |
|---|---|
| `pip install scipy` висит часами | `pkg install -y python-scipy` (предсобранный) |
| `error: externally-managed-environment` | добавьте `--break-system-packages` к pip или используйте `pkg install python-*` |
| matplotlib: `freetype not found` | `pkg install -y freetype libjpeg-turbo pkg-config clang` и повторить |
| Кириллица в фигурах квадратиками | не должна появиться (DejaVu Sans есть всегда); если да — `pkg install -y font-dejavu` |
| `pytest: command not found` | `python3 -m pytest tests/ -q` (именно так и в Makefile) |
| Телефон греется / батарея | это нормально: 7 экспериментов считают матрицы; wake-lock + зарядка |
| `git push` просит пароль | нужен **токен** (п. 4.3, способ 2), а не пароль GitHub |

## 6. Что должно получиться

- `pytest tests/ -q` → все тесты passed (проверяются теоремы A/B/C,
  перепись {7,3} из GL(3,2), дробь 9/224, делимости Гурвица);
- `run_all.py` → 7 блоков `[OK] exp*.py`, обновлённые `results/*.json`
  (совпадают с закоммиченными до ~1e-13) и 32 PNG в `fig_ru/`/`fig_en/`;
- в репозитории появится папка `dsi_lab` с README, которую можно открыть
  прямо на github.com.
