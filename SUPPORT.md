# Поддержка / Support

Спасибо, что используете **choptuik_ac_bc**. Вот как получить помощь.

## 📚 Самопомощь (начните здесь)

| Вопрос | Где ответ |
|---|---|
| «Как воспроизвести число X?» | [README → Индекс воспроизведения](README.md#индекс-воспроизведения-каждое-число--команда--json) и [`verification/README.md`](verification/README.md) — у каждого числа есть команда и JSON |
| «Как запустить пакет?» | [README → Быстрый старт](README.md#быстрый-старт) и `README.md` в соответствующей папке пакета |
| «Что верифицировано и с каким вердиктом?» | [`verification/README.md`](verification/README.md) (досье) · [`monograph/verification_monograph_bilingual.pdf`](monograph/verification_monograph_bilingual.pdf) (монография) |
| «Что означает константа/термин?» | [`docs/`](docs/) · глоссарий в приложении CHB (`Collapse Hawking Bridge/monograph/`) |
| «Как устроен репозиторий?» | [README → Интеллект-карта](README.md#интеллект-карта-репозитория) · [`docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md) |
| Ошибка сборки/зависимостей | [`.devcontainer/`](.devcontainer/) (всё предустановлено) · [`docker/`](docker/) · таблицы зависимостей в `pyproject.toml` / `requirements.txt` каждого пакета |

## 🐞 Нашли расхождение с машинным вердиктом?

Это самое ценное сообщение для этого репозитория. Откройте issue по шаблону
**Verification Discrepancy** ([`.github/ISSUE_TEMPLATE/verification_discrepancy.md`](.github/ISSUE_TEMPLATE/verification_discrepancy.md))
и укажите: команду, которую вы запускали, ожидаемое число из JSON-вердикта,
полученное число и версию Python/платформу. Содержательные сообщения об ошибках
и несоответствиях воспроизведения приветствуются более всего.

## 💬 Вопросы и обсуждения

- **Математика, методы, интерпретация вердиктов** → Discussions, шаблон *Q&A*
  ([открыть](https://github.com/wild8highlander/choptuik_ac_bc/discussions))
- **Новый результат/расширение поверх программы** → Discussions, шаблон *New Mathematical Result*
- **Общие баги и пожелания** → Issues по шаблонам Bug Report / Feature Request

## ⏱ Время ответа

Репозиторий ведётся в одиночку. Ожидайте ответа в течение **~1–2 недель**;
критические расхождения верификации рассматриваются в первую очередь.

## 🔒 Безопасность

Не публикуйте проблемы безопасности в публичных issues — следуйте
[`SECURITY.md`](SECURITY.md) (email автору).
