#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R5 — внешнее сравнение: границы поисков наггетов/стрэйнджлетов (веб-верифицировано)
сливается в roadmap_results.json. Каждая строка таблицы снабжена источником
поискового сниппета (ws_*.json), значения берутся только из подтверждённых цитат."""
import json

WORK = "/home/z/my-project/qhb_work"

rows = [
    {"id": "X1", "who": "de Rujula, Glashow (1984)",
     "what": "ядериты: гипотеза и космологический эталон потока (тёмная материя)",
     "bound": "эталон F ≈ 7.8·(1 г / m) см⁻²·с⁻¹·ср⁻¹ (изотропный, для массы m)",
     "ref": "Nature 312 (1984) 734",
     "src": "ws_derujula/ws_macro: 'De Rujula and Glashow estimated an upper bound ... F = 7.8(1 g/m)'"},
    {"id": "X2", "who": "MACRO, Gran Sasso (1997–2001)",
     "what": "поиск ядеритов подземным детектором",
     "bound": "< 2.7×10⁻¹⁶ см⁻²·с⁻¹·ср⁻¹ (изотропный поток)",
     "ref": "MACRO Collab. (V. Popa et al.), Proc. 25th ICRC (1997)",
     "src": "ws_macro: 'flux limit is 2.7 x 10^-16 cm^-2 s^-1 sr^-1 for an isotropic flux'"},
    {"id": "X3", "who": "SLIM, Gran Sasso",
     "what": "ядериты (ядерные треки)",
     "bound": "~10⁻¹⁵ см⁻²·с⁻¹·ср⁻¹",
     "ref": "SLIM Collab. (S. Cecchini et al.); значение по обзору Piotrowski et al. 2020",
     "src": "ws_slim: 'SLIM has given a limit of ~10^-15'"},
    {"id": "X4", "who": "ANTARES (2023)",
     "what": "ядериты до m ~ 10¹⁷ ГэВ/c² (9 лет данных, 2009–2017)",
     "bound": "~5×10⁻¹⁷ см⁻²·с⁻¹·ср⁻¹",
     "ref": "A. Albert et al. (ANTARES Collab.), 2023 (arXiv 2022)",
     "src": "ws_macro/ws_ant2: 'Upper limits ... at the level of ~5 x 10-17 cm-2 s-1 sr-1'"},
    {"id": "X5", "who": "Pi-of-the-Sky (2020)",
     "what": "тяжёлые компактные объекты, массы 100 г – 100 кг",
     "bound": "самые строгие пределы в классе масс (фотовспышки в атмосфере)",
     "ref": "L. W. Piotrowski et al., Phys. Rev. D (2020)",
     "src": "ws_piotr: 'the most stringent limits on the flux ... masses spanning between 100 g and 100 kg'"},
    {"id": "X6", "who": "BNL E864, AGS",
     "what": "стрэйнджлеты в Au+Pt (|Z|≥1)",
     "bound": "≲10⁻⁶–10⁻⁷ на центральное столкновение (финальная чувствительность); ранние поиски 10⁻⁴–5×10⁻⁵",
     "ref": "T. A. Armstrong et al. (E864 Collab.), Phys. Rev. Lett. 79 (1997)",
     "src": "ws_e864: 'Upper limits of a few 10-6 to 10-7 per central ... (E864)'; 'initial searches ... 10-4 to 5x10-5 per interaction'"},
    {"id": "X7", "who": "STAR, RHIC (2007)",
     "what": "стрэйнджлеты в Au+Au при √s_NN = 200 ГэВ (61 млн центральных столкновений)",
     "bound": "≲ несколько·10⁻⁶–10⁻⁷ на центральное столкновение",
     "ref": "B. I. Abelev et al. (STAR Collab.), Phys. Rev. C (2007)",
     "src": "ws_e864/ws_star: 'Strangelet search in Au+Au collisions at sNN=200 GeV ... 61 million central'"},
    {"id": "X8", "who": "AMS-01 (2000)",
     "what": "стрэйндж-кварковая материя в космических лучах",
     "bound": "кандидатов нет; предел на поток SMN",
     "ref": "J. Alcaraz et al. (AMS Collab.), Phys. Lett. B 490 (2000) 27",
     "src": "ws_ams: AMS-02 статусные материалы; AMS-01 strangelet search PLB 490 (2000)"},
]

record = {
    "table": rows,
    "scope_note": ("Пакет QHB НЕ предсказывает физических потоков: T(0) = 9.21×10⁻¹³ — "
                   "безразмерная модельная вероятность туннелирования, а комбинаторная граница "
                   "наггетов P < 10^(−1.2×10³¹) относится к модельным единицам. Таблица X1–X8 "
                   "фиксирует эмпирическую арену (проверенные границы реальных поисков), в которой "
                   "должно жить любое физическое предсказание о наггетах; сопоставление модельных "
                   "и физических величин без калибровки запрещено дисциплиной честности."),
    "falsifier": "подтверждённый кандидат в наггеты/стрэйнджлеты выше приведённых границ X1–X8",
    "verdict": ("Сравнение выполнено как «контекстная граница», не как сопоставление подобных "
                "величин: модельный пакет поставляет вероятность, эксперименты — пределы потоков. "
                "Канонический статус: comparison (внешнее сравнение с корректными ссылками)."),
}

with open(f"{WORK}/roadmap_results.json") as f:
    data = json.load(f)
data["r5_external"] = record
with open(f"{WORK}/roadmap_results.json", "w") as f:
    json.dump(data, f, ensure_ascii=False, indent=1, default=float)
print("R5 merged into roadmap_results.json; rows:", len(rows))
