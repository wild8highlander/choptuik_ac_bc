# DSI-лаборатория: быстрые команды.
# На Android/Termux: pkg install make, затем те же команды.

PY := python3

.PHONY: help test validate run quick fig verify figures logo animations \
        monograph multilang lint lint-mypy clean

help:
	@echo "make test        - быстрые pytest-проверки теорем (~1-2 мин)"
	@echo "make validate    - аудит закоммиченных вердиктов (dsilab.validate)"
	@echo "make run         - все 7 экспериментов + сводная фигура (5-15 мин)"
	@echo "make quick       - только эксперименты 2, 6, 7 (самые быстрые)"
	@echo "make fig         - только сводная фигура Чоптюка"
	@echo "make verify      - test + validate + run (полная верификация)"
	@echo "make figures     - регенерация сводной фигуры"
	@echo "make logo        - логотип (светл/тёмн.) + аватары из scripts/"
	@echo "make animations  - 8 анимаций (en/ru, gif+mp4) из results/"
	@echo "make monograph   - пересборка PDF-монографий EN/RU (tectonic)"
	@echo "make multilang   - сборка и прогон C/C++/JS-двойников + diff"
	@echo "make lint        - ruff + black --check по dsi_lab"
	@echo "make lint-mypy   - mypy по dsilab/ и тестам"
	@echo "make clean       - удалить __pycache__ и .pytest_cache"

test:
	$(PY) -m pytest tests/ -q

validate:
	$(PY) -m dsilab.validate

run:
	$(PY) run_all.py

quick:
	$(PY) run_all.py 2 6 7

fig:
	$(PY) fig_choptuik.py

verify: test validate run

figures:
	$(PY) fig_choptuik.py

logo:
	$(PY) scripts/make_logo.py

animations:
	$(PY) scripts/make_animations.py --all

monograph:
	cd monograph/tex && tectonic dsilab_monograph_en.tex && \
		tectonic dsilab_monograph_ru.tex && \
		mv dsilab_monograph_en.pdf dsilab_monograph_ru.pdf ..

multilang:
	mkdir -p multilang/c/build
	cd multilang/c && $(CC) -O2 -ffp-contract=off -o build/dsi_core \
		dsi_core.c -lm && ./build/dsi_core > build/c_out.txt && \
		diff build/c_out.txt reference_output.txt
	cd multilang/cpp && $(CXX) -O2 -ffp-contract=off -o /tmp/dsi_core_cpp \
		dsi_core.cpp && /tmp/dsi_core_cpp > /tmp/cpp_out.txt && \
		diff /tmp/cpp_out.txt ../c/reference_output.txt
	node multilang/javascript/dsi_core.mjs > /tmp/js_out.txt && \
		diff /tmp/js_out.txt multilang/c/reference_output.txt
	@echo "multilang: C/C++/JS output byte-identical to reference"

lint:
	ruff check . && black --check dsilab/ scripts/ tests/test_dsilab_package.py

lint-mypy:
	mypy --ignore-missing-imports dsilab/ tests/test_dsilab_package.py

clean:
	rm -rf __pycache__ .pytest_cache tests/__pycache__ dsilab/__pycache__ \
		scripts/__pycache__ multilang/c/build
