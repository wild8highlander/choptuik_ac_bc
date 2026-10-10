# Quark-Hawking Bridge — v1.2.0
PYTHON ?= python3

.PHONY: help install test validate data figures claims c1 c2 c3 c4 c5 c6 c7 c8 c9 c10 c11 all clean

help:
	@echo "Quark-Hawking Bridge v1.2.0"
	@echo "  make install   - install the qhb package (editable)"
	@echo "  make test      - run the pytest suite (94 pins)"
	@echo "  make validate  - 50-digit mpmath re-verification (9/9)"
	@echo "  make data      - rebuild data/qhb from committed verdicts"
	@echo "  make figures   - regenerate 40 figures (RU/EN x light/dark)"
	@echo "  make c1        - campaign C1 (the gap law, ~1 s)"
	@echo "  make c2        - campaign C2 (the trap, ~3.5 min)"
	@echo "  make c3        - campaign C3 (the Wu door, ~1 s)"
	@echo "  make c4        - campaign C4 (the floor law, ~1 s)"
	@echo "  make c5        - campaign C5 (the drift law, ~1 s)"
	@echo "  make c6        - campaign C6 (the physical mapping, ~1 s)"
	@echo "  make c7        - campaign C7 (the anharmonic trio, ~5 min)"
	@echo "  make c8        - campaign C8 (the pairwise door, ~10 s)"
	@echo "  make c9        - campaign C9 (the phase map, ~11 s)"
	@echo "  make c10       - campaign C10 (the competing models, ~4 s)"
	@echo "  make c11       - campaign C11 (the vortex anchor, ~35 s)"
	@echo "  make claims    - validate the claims registry (27 claims)"
	@echo "  make all       - test + validate + data"

install:
	$(PYTHON) -m pip install -e .

test:
	$(PYTHON) -m pytest tests/ -q

validate:
	$(PYTHON) -m qhb.validate

data:
	$(PYTHON) scripts/rebuild_data.py

figures:
	$(PYTHON) scripts/make_figures.py --all

c1:
	$(PYTHON) campaigns/run_c1.py
c2:
	$(PYTHON) campaigns/run_c2.py
c3:
	$(PYTHON) campaigns/run_c3.py
c4:
	$(PYTHON) campaigns/run_c4.py
c5:
	$(PYTHON) campaigns/run_c5.py
c6:
	$(PYTHON) campaigns/run_c6.py
c7:
	$(PYTHON) campaigns/run_c7.py
c8:
	$(PYTHON) campaigns/run_c8.py
c9:
	$(PYTHON) campaigns/run_c9.py
c10:
	$(PYTHON) campaigns/run_c10.py
c11:
	$(PYTHON) campaigns/run_c11.py

claims:
	$(PYTHON) -m qhb.claims

all: test validate data

clean:
	rm -rf .pytest_cache **/__pycache__ scratch *.log
