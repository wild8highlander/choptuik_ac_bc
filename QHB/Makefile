PYTHON ?= python3

.PHONY: all data audit twins tests figures workbook deep clean

all: data audit twins figures tests deep

data:
	$(PYTHON) tools/run_all.py

audit:
	$(PYTHON) audit/audit_ivp.py

twins:
	$(PYTHON) tools/twin_check.py

tests:
	$(PYTHON) -m pytest -q

figures:
	$(PYTHON) tools/make_figures.py

workbook:
	$(PYTHON) workbook/build_workbook.py

deep:
	$(PYTHON) tools/rebuild_data.py
	$(PYTHON) audit/deep_checks_extra.py

clean:
	rm -rf docs/figures/*.png data/*.json
