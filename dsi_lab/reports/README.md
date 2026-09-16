# reports/ — итоговые документы

Восемь финальных документов по двум циклам работы (RU и EN, PDF и DOCX),
плюс LaTeX-исходники и HTML-обложки.

## Открытые задачи фреймворка (эксперименты 1–5)

| Файл | Язык | Формат |
|------|------|--------|
| `Choptyuk_OpenProblems_Report_RU.pdf` | RU | PDF, 14 стр. (Tectonic) |
| `Choptyuk_OpenProblems_Report_EN.pdf` | EN | PDF, 13 стр. |
| `Choptyuk_OpenProblems_Report_RU.docx` | RU | DOCX |
| `Choptyuk_OpenProblems_Report_EN.docx` | EN | DOCX |

## Аналитическая атака (эксперименты 6–7: 224 = 4·56, порог e ≥ 1, разрешимость задачи Чоптюка)

| Файл | Язык | Формат |
|------|------|--------|
| `Choptyuk_Analytic_Attack_RU.pdf` | RU | PDF, 13 стр. |
| `Choptyuk_Analytic_Attack_EN.pdf` | EN | PDF, 12 стр. |
| `Choptyuk_Analytic_Attack_RU.docx` | RU | DOCX |
| `Choptyuk_Analytic_Attack_EN.docx` | EN | DOCX |

## LaTeX-исходники (`tex/`)

`report_ru.tex`, `report_en.tex`, `attack_ru.tex`, `attack_en.tex` —
компилируются Tectonic'ом:

```bash
cd tex
# фигуры лежат в ../../fig_ru и ../../fig_en; tex ожидает figs_ru/figs_en:
ln -s ../../fig_ru figs_ru && ln -s ../../fig_en figs_en
tectonic report_ru.tex     # и т.д.
```

Обложки: `covers/cover_{ru,en,attack_ru,attack_en}.html` (открываются
в браузере; печатать в PDF из диалога печати).
