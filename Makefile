# Choptuik AC/BC Makefile

PYTHON_DIR  := python
DOCS_DIR    := docs-site
BUILD_DIR   := build
DIST_DIR    := dist

.PHONY: all install test lint clean docs-install docs-build docs-serve docs-deploy docs coverage sign-release release

all: install test lint

install:
	pip install -e $(PYTHON_DIR)/[dev]

test:
	pytest $(PYTHON_DIR)/tests/ -v --cov=choptuik_ac_bc

lint:
	ruff check $(PYTHON_DIR)/
	mypy $(PYTHON_DIR)/src/

docs-install:
	pip install -r $(DOCS_DIR)/requirements.txt

docs-build:
	cd $(DOCS_DIR) && mkdocs build --strict

docs-serve:
	cd $(DOCS_DIR) && mkdocs serve

docs-deploy:
	cd $(DOCS_DIR) && mike deploy --push --update-aliases $$(python -c "import choptuik_ac_bc; print(choptuik_ac_bc.__version__)") latest

docs: docs-install docs-build

coverage:
	pytest $(PYTHON_DIR)/tests/ --cov=choptuik_ac_bc --cov-report=html --cov-report=term
	@echo "Open htmlcov/index.html for detailed coverage report"

sign-release:
	@read -p "Enter version to sign: " VERSION; \
	pip install sigstore; \
	for f in $(DIST_DIR)/*; do sigstore sign --bundle "$$f.sigstore" "$$f"; done

release:
	@read -p "Enter release version (e.g., 2.1.0): " VERSION; \
	git tag -a v$$VERSION -m "Release v$$VERSION"; \
	git push origin v$$VERSION; \
	echo "Release pipeline triggered for v$$VERSION"

clean:
	rm -rf $(BUILD_DIR) $(DIST_DIR) htmlcov .coverage .mypy_cache .ruff_cache
	rm -rf $(DOCS_DIR)/site
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
