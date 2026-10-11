# Collapse-Hawking Bridge — v2.2.0
# Makefile: every scientific operation of the repository as a target.

PYTHON ?= python3

.PHONY: help install test validate data figures c1 c2 c3 c3b c6 all clean

help:
        @echo "Collapse-Hawking Bridge v2.2.0"
        @echo "  make install   - install the chbridge package (editable)"
        @echo "  make test      - run the pytest suite (tests/)"
        @echo "  make validate  - 50-digit mpmath re-verification of all constants"
        @echo "  make data      - rebuild data/bridge tables from committed verdicts"
        @echo "  make figures   - regenerate all figures (RU/EN x light/dark)"
        @echo "  make c1        - run campaign C1 (threshold + born spectrum, ~1 min)"
        @echo "  make c2        - run campaign C2 (two branches, ~30 s; needs c1)"
        @echo "  make c3        - run campaign C3 (Delta*gamma check, ~15 s; needs c1)"
        @echo "  make c3b       - run campaign C3b (concentrated resolution, ~2 min; needs c1)"
        @echo "  make c6        - run campaign C6 (resolution-drift law, ~2 s; needs committed ladder)"
        @echo "  make all       - test + validate + data"
        @echo "  make clean     - remove caches and scratch files"

install:
        $(PYTHON) -m pip install -e .

test:
        $(PYTHON) -m pytest tests/ -q

validate:
        $(PYTHON) -m chbridge.validate

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

c3b:
        $(PYTHON) campaigns/run_c3b.py

c6:
        $(PYTHON) campaigns/run_c6_drift.py

all: test validate data

clean:
        rm -rf .pytest_cache **/__pycache__ scratch *.log
