/**
 * i18n.ts — English / Russian translations and useTranslation hook.
 *
 * All UI text lives here so the language toggle can swap it instantly without
 * a round-trip. Default language is English.
 */

import { useSyncExternalStore } from "react";
import type { Language } from "./types";

type Dict = Record<string, string>;

const en: Dict = {
  "app.title": "Choptuik-QCD Bridge",
  "app.subtitle": "Interactive visualization of the 9-section monograph",
  "app.author": "Ishak Khamzatovich Isaev",
  "app.orcid": "ORCID 0009-0003-7299-0701",

  "nav.home": "Home",
  "nav.dashboard": "Dashboard",
  "nav.about": "About",
  "nav.section": "Section",
  "nav.sections": "Sections",
  "nav.run": "Run",
  "nav.reports": "Reports",
  "nav.parameters": "Parameters",

  "home.heading": "Choptuik–QCD Bridge — 9-Section Dashboard",
  "home.intro":
    "This dashboard mirrors the Python engine `qcd_bridge_engine.py`. Every section can be re-computed live in the browser via JavaScript ports of the same formulas; full-precision runs are dispatched to the Python backend via `/api/run`.",
  "home.quickStats": "Quick stats",
  "home.openSection": "Open section",

  "s1.title": "O_chi operator (28×28)",
  "s1.short": "K3 ⊕ M_F ⊕ κ_T·V_T",
  "s1.desc": "Construction of the structural operator O_chi = Q_K3 ⊕ M_F + κ_T·V_T at N=28.",
  "s1.stat": "22 K3 + 6 N_f",

  "s2.title": "RMT universality sweep",
  "s2.short": "BF(GUE/Poisson)",
  "s2.desc": "Bayes factor BF(GUE/Poisson) across κ_T to classify the universality class.",
  "s2.stat": "κ_T → BF",

  "s3.title": "Spectral staircase",
  "s3.short": "Wigner vs data",
  "s3.desc": "Cumulative spectral staircase vs Wigner semicircle for the unfolded O_chi spectrum.",
  "s3.stat": "N(λ) curve",

  "s4.title": "N-scaling of ⟨λ⟩ → 0",
  "s4.short": "1/√N artifact",
  "s4.desc": "Verifies that the finite-N offset of ⟨λ⟩ scales as 1/√N and vanishes in the continuum.",
  "s4.stat": "1/√N",

  "s5.title": "τ_relax dynamics",
  "s5.short": "~5e-41 s",
  "s5.desc": "Dynamic relaxation of θ → 0 with τ_relax ≈ ℏ/Λ_QCD ≈ 5×10⁻⁴¹ s.",
  "s5.stat": "~5e-41 s",

  "s6.title": "κ_T physical estimate",
  "s6.short": "95% CL > 2.62",
  "s6.desc": "Lattice Dirac data constrains κ_T > 2.62 (95% CL); best-fit κ_T = 8.45.",
  "s6.stat": "BF ≥ 99",

  "s7.title": "Cabibbo angle coincidence",
  "s7.short": "θ_C from b_Ch",
  "s7.desc": "Framework prediction θ_C = ½·arcsin(2√(b_Ch/4)) vs measured θ_C.",
  "s7.stat": "δ < 15%",

  "s8.title": "CP 8-step solution chain",
  "s8.short": "θ̄ = 0",
  "s8.desc": "The 8 logical steps deriving θ̄ = 0 exactly (no new fields, scales or symmetries).",
  "s8.stat": "0 new fields",

  "s9.title": "Jet wake bridge (NR ↔ QCD)",
  "s9.short": "χ_eff = δ_C·Λ⁴",
  "s9.desc": "Bridge between numerical relativity jet wakes and QCD topological sectors via χ_eff.",
  "s9.stat": "χ_eff[GeV⁴]",

  "params.title": "Custom parameters",
  "params.kappaT": "κ_T (T-breaking coupling)",
  "params.N": "N (Hilbert space dim.)",
  "params.nFlavors": "n_flavors (quark flavors)",
  "params.seed": "Random seed",
  "params.sections": "Sections to compute",
  "params.language": "Language",
  "params.reset": "Reset to defaults",
  "params.runPython": "Run via Python (full precision)",
  "params.runLocal": "Live preview (JS)",
  "params.running": "Running…",
  "params.mode": "Run mode",

  "mode.verify_all": "Verify all sections",
  "mode.verify_section": "Verify single section",
  "mode.custom": "Custom",

  "report.title": "Download reports",
  "report.intro":
    "Each button triggers a Python-backed generation in the requested format and downloads the file. Reports are saved to /choptuik_ac_bc/code/web/output/.",
  "report.generate": "Generate",
  "report.generating": "Generating…",
  "report.download": "Download",
  "report.fmt.txt": "TXT",
  "report.fmt.csv": "CSV",
  "report.fmt.md": "Markdown",
  "report.fmt.pdf": "PDF",
  "report.fmt.html": "HTML",
  "report.fmt.docx": "DOCX",
  "report.fmt.json": "JSON",
  "report.lastRun": "Last run",
  "report.noRun": "No run yet — click “Run via Python” first.",
  "report.copyPath": "Copy path",
  "report.copied": "Copied",

  "about.title": "About",
  "about.author": "Author",
  "about.orcid": "ORCID",
  "about.repo": "Repository",
  "about.monograph": "Monograph",
  "about.license": "License",
  "about.bio":
    "Ishak Khamzatovich Isaev is the author of the Choptuik–QCD bridge monograph, a framework that connects the Choptuik critical exponent δ_C = π/7 with the QCD strong-CP problem through a 28×28 operator O_chi = Q_K3 ⊕ M_F + κ_T·V_T built on the K3 intersection form. The framework predicts θ̄ = 0 exactly, with no new fields, scales or symmetries, and exposes falsification tests via the Giusti–Rossi–Testa lattice method and PSL(2,7) algebraic geometry.",
  "about.stack": "Tech stack",
  "about.stackText":
    "Next.js 16 (App Router) · TypeScript · Tailwind CSS 4 · shadcn/ui · Plotly.js · Python 3 (NumPy) backend via subprocess.",
  "about.references": "References",

  "footer.author": "Author",
  "footer.orcid": "ORCID",
  "footer.repo": "GitHub",
  "footer.license": "License",
  "footer.poweredBy": "Built with Next.js 16 · Tailwind 4 · Plotly.js",

  "plot.loading": "Rendering 3D plot…",
  "plot.empty": "No data — adjust parameters or click “Run via Python”.",
  "plot.matrix": "Matrix heatmap",
  "plot.eigvals": "Eigenvalue spectrum",
  "plot.sweep3d": "κ_T sweep: 3D scatter (κ_T, BF, ⟨λ⟩)",
  "plot.staircase": "Spectral staircase vs Wigner semicircle",
  "plot.scaling": "1/√N scaling test",
  "plot.tau": "τ_relax decay (log time)",
  "plot.kappaT": "Lattice κ_T confidence region",
  "plot.cabibbo": "Cabibbo: predicted vs measured",
  "plot.cpchain": "CP 8-step chain (3D bars)",
  "plot.jetwake": "Jet wake bridge: χ_eff surface",

  "stats.bf": "Bayes factor",
  "stats.class": "Class",
  "stats.lambdaMin": "λ_min",
  "stats.lambdaMax": "λ_max",
  "stats.lambdaMean": "⟨λ⟩",
  "stats.lambdaStd": "σ_λ",
  "stats.elapsed": "Elapsed (s)",
  "stats.shape": "Operator shape",
  "stats.trace": "Trace",
  "stats.N": "N",
  "stats.absMean": "|⟨λ⟩|",
  "stats.theory": "1/√N (theory)",
  "stats.ratio": "ratio",
  "stats.tauRelax": "τ_relax (s)",
  "stats.tauTheory": "τ_relax theory (s)",
  "stats.theta0": "θ_0",
  "stats.thetaAt1Tau": "θ(τ)",
  "stats.thetaAt5Tau": "θ(5τ)",
  "stats.kappaLower": "κ_T lower (95% CL)",
  "stats.kappaBest": "κ_T best-fit",
  "stats.bfAtLower": "BF @ lower",
  "stats.bfAtBest": "BF @ best-fit",
  "stats.thetaCpred": "θ_C predicted (rad)",
  "stats.thetaCmeas": "θ_C measured (rad)",
  "stats.deviationPct": "Deviation %",
  "stats.coincidence": "Coincidence",
  "stats.finalResult": "Final result",
  "stats.totalSteps": "Total steps",
  "stats.chiEff": "χ_eff (GeV⁴)",
  "stats.chiEffEv": "χ_eff (eV⁴)",
  "stats.bridge": "Bridge formula",
  "stats.deltaC": "δ_C",
  "stats.kappaCoupling": "κ_T coupling",

  "class.negative": "negative",
  "class.weak": "weak",
  "class.positive": "positive",
  "class.strong": "strong",
  "class.decisive": "decisive",

  "table.step": "Step",
  "table.statement": "Statement",
  "table.evidence": "Evidence",
  "table.section": "§",
  "table.kappa": "κ_T",
  "table.bf": "BF(GUE/Poisson)",
  "table.N": "N",
  "table.lambdaMean": "⟨λ⟩",
  "table.absMean": "|⟨λ⟩|",
  "table.theory": "1/√N",

  "toast.runStart": "Dispatching run to Python backend…",
  "toast.runOk": "Run complete in {elapsed}s",
  "toast.runErr": "Run failed: {msg}",
  "toast.reportOk": "{fmt} report ready — downloading…",
  "toast.reportErr": "{fmt} report failed: {msg}",
  "toast.copied": "Path copied to clipboard",
  "toast.preview": "Live preview updated",

  "common.refresh": "Refresh preview",
  "common.openExternal": "Open externally",
  "common.viewFigure": "View static figure",
  "common.collapse": "Collapse",
  "common.expand": "Expand",

  "dashboard.title": "Interactive Dashboard — 9 Sections",
  "dashboard.subtitle": "Section-specific sliders drive live JavaScript previews. Use “Run via Python” for canonical full-precision results.",
  "dashboard.tab": "Section",
  "dashboard.runPython": "Run all (Python)",
  "dashboard.runLocal": "Live preview",
  "dashboard.reset": "Reset section",
  "dashboard.elapsed": "Elapsed",
  "dashboard.noData": "Adjust sliders and click “Live preview”.",
  "dashboard.slider.kappaT": "κ_T (T-breaking)",
  "dashboard.slider.kappaTmin": "κ_T min",
  "dashboard.slider.kappaTmax": "κ_T max",
  "dashboard.slider.nKappas": "# κ_T points",
  "dashboard.slider.nFlavors": "n_flavors",
  "dashboard.slider.seed": "Random seed",
  "dashboard.slider.nBins": "BF bins",
  "dashboard.slider.Nmin": "N min",
  "dashboard.slider.Nmax": "N max",
  "dashboard.slider.nPoints": "# N points",
  "dashboard.slider.theta0": "θ_0 (initial)",
  "dashboard.slider.tMinLog": "log10(t_min)",
  "dashboard.slider.tMaxLog": "log10(t_max)",
  "dashboard.slider.deltaC": "δ_C (Choptuik exponent)",
  "dashboard.slider.lambdaQCD": "Λ_QCD (GeV)",
  "dashboard.slider.tMax": "Wake crossing t_max",
  "dashboard.slider.sin2Theta": "sin²(θ_C) measured",
  "dashboard.slider.Nstair": "K3 N revealed",
};

const ru: Dict = {
  "app.title": "Мост Чоптуика–КХД",
  "app.subtitle": "Интерактивная визуализация 9 разделов монографии",
  "app.author": "Ишак Хамзатович Исаев",
  "app.orcid": "ORCID 0009-0003-7299-0701",

  "nav.home": "Главная",
  "nav.dashboard": "Панель",
  "nav.about": "О проекте",
  "nav.section": "Раздел",
  "nav.sections": "Разделы",
  "nav.run": "Запуск",
  "nav.reports": "Отчёты",
  "nav.parameters": "Параметры",

  "home.heading": "Мост Чоптуика–КХД — панель 9 разделов",
  "home.intro":
    "Панель повторяет Python-движок `qcd_bridge_engine.py`. Каждый раздел можно пересчитать в браузере через JS-порты тех же формул; прогоны с полной точностью выполняются Python-бэкендом через `/api/run`.",
  "home.quickStats": "Ключевые показатели",
  "home.openSection": "Открыть раздел",

  "s1.title": "Оператор O_chi (28×28)",
  "s1.short": "K3 ⊕ M_F ⊕ κ_T·V_T",
  "s1.desc": "Построение структурного оператора O_chi = Q_K3 ⊕ M_F + κ_T·V_T при N=28.",
  "s1.stat": "22 K3 + 6 N_f",

  "s2.title": "Развертка универсальности RMT",
  "s2.short": "BF(GUE/Poisson)",
  "s2.desc": "Фактор Байеса BF(GUE/Poisson) по κ_T для определения класса универсальности.",
  "s2.stat": "κ_T → BF",

  "s3.title": "Спектральная лестница",
  "s3.short": "Вигнер vs данные",
  "s3.desc": "Кумулятивная спектральная лестница vs полукруг Вигнера для развёрнутого спектра O_chi.",
  "s3.stat": "N(λ) кривая",

  "s4.title": "N-скейлинг ⟨λ⟩ → 0",
  "s4.short": "1/√N артефакт",
  "s4.desc": "Проверка, что конечномерный сдвиг ⟨λ⟩ убывает как 1/√N и исчезает в континууме.",
  "s4.stat": "1/√N",

  "s5.title": "Динамика τ_relax",
  "s5.short": "~5e-41 с",
  "s5.desc": "Динамическая релаксация θ → 0 с τ_relax ≈ ℏ/Λ_QCD ≈ 5×10⁻⁴¹ с.",
  "s5.stat": "~5e-41 с",

  "s6.title": "Физическая оценка κ_T",
  "s6.short": "95% CL > 2.62",
  "s6.desc": "Данные решёточного Дирака ограничивают κ_T > 2.62 (95% CL); best-fit κ_T = 8.45.",
  "s6.stat": "BF ≥ 99",

  "s7.title": "Совпадение угла Кабиббо",
  "s7.short": "θ_C из b_Ch",
  "s7.desc": "Предсказание рамки θ_C = ½·arcsin(2√(b_Ch/4)) vs измеренный θ_C.",
  "s7.stat": "δ < 15%",

  "s8.title": "CP 8-шаговая цепочка решения",
  "s8.short": "θ̄ = 0",
  "s8.desc": "8 логических шагов, выводящих θ̄ = 0 точно (без новых полей, масштабов и симметрий).",
  "s8.stat": "0 новых полей",

  "s9.title": "Мост струйного следа (NR ↔ КХД)",
  "s9.short": "χ_eff = δ_C·Λ⁴",
  "s9.desc": "Связь струйных следов численной относительности с топологическими секторами КХД через χ_eff.",
  "s9.stat": "χ_eff[ГэВ⁴]",

  "params.title": "Пользовательские параметры",
  "params.kappaT": "κ_T (T-нарушающая связь)",
  "params.N": "N (размерность пространства Гильберта)",
  "params.nFlavors": "n_flavors (ароматы кварков)",
  "params.seed": "Случайное зерно",
  "params.sections": "Разделы для расчёта",
  "params.language": "Язык",
  "params.reset": "Сбросить по умолчанию",
  "params.runPython": "Запустить через Python (полная точность)",
  "params.runLocal": "Живой просмотр (JS)",
  "params.running": "Выполняется…",
  "params.mode": "Режим прогона",

  "mode.verify_all": "Проверить все разделы",
  "mode.verify_section": "Проверить один раздел",
  "mode.custom": "Пользовательский",

  "report.title": "Скачать отчёты",
  "report.intro":
    "Каждая кнопка запускает Python-генерацию отчёта в нужном формате и скачивает файл. Отчёты сохраняются в /choptuik_ac_bc/code/web/output/.",
  "report.generate": "Сгенерировать",
  "report.generating": "Генерация…",
  "report.download": "Скачать",
  "report.fmt.txt": "TXT",
  "report.fmt.csv": "CSV",
  "report.fmt.md": "Markdown",
  "report.fmt.pdf": "PDF",
  "report.fmt.html": "HTML",
  "report.fmt.docx": "DOCX",
  "report.fmt.json": "JSON",
  "report.lastRun": "Последний прогон",
  "report.noRun": "Прогонов ещё нет — сначала нажмите «Запустить через Python».",
  "report.copyPath": "Копировать путь",
  "report.copied": "Скопировано",

  "about.title": "О проекте",
  "about.author": "Автор",
  "about.orcid": "ORCID",
  "about.repo": "Репозиторий",
  "about.monograph": "Монография",
  "about.license": "Лицензия",
  "about.bio":
    "Ишак Хамзатович Исаев — автор монографии «Мост Чоптуика–КХД», объединяющей критический показатель Чоптуика δ_C = π/7 с проблемой сильного CP в КХД через оператор O_chi = Q_K3 ⊕ M_F + κ_T·V_T размерности 28×28, построенный на форме пересечений K3. Рамка предсказывает θ̄ = 0 точно, без новых полей, масштабов и симметрий, и предлагает тесты фальсификации через метод Джусти–Росси–Теста на решётке и алгебраическую геометрию PSL(2,7).",
  "about.stack": "Технологии",
  "about.stackText":
    "Next.js 16 (App Router) · TypeScript · Tailwind CSS 4 · shadcn/ui · Plotly.js · Python 3 (NumPy) бэкенд через subprocess.",
  "about.references": "Ссылки",

  "footer.author": "Автор",
  "footer.orcid": "ORCID",
  "footer.repo": "GitHub",
  "footer.license": "Лицензия",
  "footer.poweredBy": "Сделано на Next.js 16 · Tailwind 4 · Plotly.js",

  "plot.loading": "Рендеринг 3D-графика…",
  "plot.empty": "Нет данных — измените параметры или нажмите «Запустить через Python».",
  "plot.matrix": "Тепловая карта матрицы",
  "plot.eigvals": "Спектр собственных значений",
  "plot.sweep3d": "Развертка κ_T: 3D-диаграмма (κ_T, BF, ⟨λ⟩)",
  "plot.staircase": "Спектральная лестница vs полукруг Вигнера",
  "plot.scaling": "Тест 1/√N скейлинга",
  "plot.tau": "Затухание τ_relax (лог. время)",
  "plot.kappaT": "Доверительная область решёточного κ_T",
  "plot.cabibbo": "Кабиббо: предсказание vs измерение",
  "plot.cpchain": "CP 8-шаговая цепочка (3D-бары)",
  "plot.jetwake": "Мост струйного следа: поверхность χ_eff",

  "stats.bf": "Фактор Байеса",
  "stats.class": "Класс",
  "stats.lambdaMin": "λ_min",
  "stats.lambdaMax": "λ_max",
  "stats.lambdaMean": "⟨λ⟩",
  "stats.lambdaStd": "σ_λ",
  "stats.elapsed": "Время (с)",
  "stats.shape": "Размер оператора",
  "stats.trace": "След",
  "stats.N": "N",
  "stats.absMean": "|⟨λ⟩|",
  "stats.theory": "1/√N (теория)",
  "stats.ratio": "отношение",
  "stats.tauRelax": "τ_relax (с)",
  "stats.tauTheory": "τ_relax теория (с)",
  "stats.theta0": "θ_0",
  "stats.thetaAt1Tau": "θ(τ)",
  "stats.thetaAt5Tau": "θ(5τ)",
  "stats.kappaLower": "κ_T нижняя (95% CL)",
  "stats.kappaBest": "κ_T best-fit",
  "stats.bfAtLower": "BF @ нижняя",
  "stats.bfAtBest": "BF @ best-fit",
  "stats.thetaCpred": "θ_C предсказанный (рад)",
  "stats.thetaCmeas": "θ_C измеренный (рад)",
  "stats.deviationPct": "Отклонение %",
  "stats.coincidence": "Совпадение",
  "stats.finalResult": "Итог",
  "stats.totalSteps": "Всего шагов",
  "stats.chiEff": "χ_eff (ГэВ⁴)",
  "stats.chiEffEv": "χ_eff (эВ⁴)",
  "stats.bridge": "Формула моста",
  "stats.deltaC": "δ_C",
  "stats.kappaCoupling": "κ_T связь",

  "class.negative": "отрицательный",
  "class.weak": "слабый",
  "class.positive": "положительный",
  "class.strong": "сильный",
  "class.decisive": "решающий",

  "table.step": "Шаг",
  "table.statement": "Утверждение",
  "table.evidence": "Доказательство",
  "table.section": "§",
  "table.kappa": "κ_T",
  "table.bf": "BF(GUE/Poisson)",
  "table.N": "N",
  "table.lambdaMean": "⟨λ⟩",
  "table.absMean": "|⟨λ⟩|",
  "table.theory": "1/√N",

  "toast.runStart": "Прогон отправлен на Python-бэкенд…",
  "toast.runOk": "Прогон завершён за {elapsed} с",
  "toast.runErr": "Прогон не удался: {msg}",
  "toast.reportOk": "Отчёт {fmt} готов — скачивание…",
  "toast.reportErr": "Отчёт {fmt} не построен: {msg}",
  "toast.copied": "Путь скопирован в буфер обмена",
  "toast.preview": "Живой просмотр обновлён",

  "common.refresh": "Обновить просмотр",
  "common.openExternal": "Открыть внешнюю ссылку",
  "common.viewFigure": "Открыть статичную фигуру",
  "common.collapse": "Свернуть",
  "common.expand": "Развернуть",

  "dashboard.title": "Интерактивная панель — 9 разделов",
  "dashboard.subtitle": "Слайдеры для каждого раздела управляют живыми JS-превью. Для канонических результатов с полной точностью используйте «Run via Python».",
  "dashboard.tab": "Раздел",
  "dashboard.runPython": "Запустить все (Python)",
  "dashboard.runLocal": "Живое превью",
  "dashboard.reset": "Сброс раздела",
  "dashboard.elapsed": "Время",
  "dashboard.noData": "Настройте слайдеры и нажмите «Живое превью».",
  "dashboard.slider.kappaT": "κ_T (T-нарушение)",
  "dashboard.slider.kappaTmin": "κ_T мин",
  "dashboard.slider.kappaTmax": "κ_T макс",
  "dashboard.slider.nKappas": "# точек κ_T",
  "dashboard.slider.nFlavors": "n_flavors",
  "dashboard.slider.seed": "Случайное зерно",
  "dashboard.slider.nBins": "бин BF",
  "dashboard.slider.Nmin": "N мин",
  "dashboard.slider.Nmax": "N макс",
  "dashboard.slider.nPoints": "# точек N",
  "dashboard.slider.theta0": "θ_0 (начальное)",
  "dashboard.slider.tMinLog": "log10(t_мин)",
  "dashboard.slider.tMaxLog": "log10(t_макс)",
  "dashboard.slider.deltaC": "δ_C (показатель Чоптуика)",
  "dashboard.slider.lambdaQCD": "Λ_QCD (ГэВ)",
  "dashboard.slider.tMax": "t_макс пробуждения струи",
  "dashboard.slider.sin2Theta": "sin²(θ_C) измеренное",
  "dashboard.slider.Nstair": "K3 N раскрыто",
};

const DICTS: Record<Language, Dict> = { en, ru };

// ─── Lightweight external store (no extra deps) ──────────────────────────────
let currentLang: Language = "en";
const listeners = new Set<() => void>();

if (typeof window !== "undefined") {
  const saved = window.localStorage.getItem("qcd-bridge-lang");
  if (saved === "en" || saved === "ru") currentLang = saved;
}

function emit() {
  for (const l of listeners) l();
}

export function setLanguage(lang: Language) {
  if (lang === currentLang) return;
  currentLang = lang;
  if (typeof window !== "undefined") {
    window.localStorage.setItem("qcd-bridge-lang", lang);
  }
  emit();
}

export function getLanguage(): Language {
  return currentLang;
}

function subscribe(cb: () => void) {
  listeners.add(cb);
  return () => listeners.delete(cb);
}

/** React hook returning the current language + a `t(key)` translator. */
export function useTranslation(): {
  lang: Language;
  t: (key: string, vars?: Record<string, string | number>) => string;
  setLang: (l: Language) => void;
} {
  const lang = useSyncExternalStore(subscribe, getLanguage, getLanguage);
  const t = (key: string, vars?: Record<string, string | number>) => {
    let s = DICTS[lang][key] ?? DICTS.en[key] ?? key;
    if (vars) {
      for (const [k, v] of Object.entries(vars)) {
        s = s.replace(`{${k}}`, String(v));
      }
    }
    return s;
  };
  return { lang, t, setLang: setLanguage };
}
