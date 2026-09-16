# DSI-лаборатория: быстрые команды.
# На Android/Termux: pkg install make, затем те же команды.

PY := python3

.PHONY: help test run quick fig clean verify

help:
	@echo "make test   - быстрые pytest-проверки (~1-2 мин)"
	@echo "make run    - все 7 экспериментов + сводная фигура (5-15 мин)"
	@echo "make quick  - только эксперименты 2, 6, 7 (самые быстрые)"
	@echo "make fig    - только сводная фигура Чоптюка"
	@echo "make verify - test + run (полная верификация)"
	@echo "make clean  - удалить __pycache__ и .pytest_cache"

test:
	$(PY) -m pytest tests/ -q

run:
	$(PY) run_all.py

quick:
	$(PY) run_all.py 2 6 7

fig:
	$(PY) fig_choptuik.py

verify: test run

clean:
	rm -rf __pycache__ .pytest_cache tests/__pycache__
