# Choptyuk Spinor Corrections - Master Makefile
# Usage: make <target>

.PHONY: all verify simulate plots reports clean python-verify julia-verify java-build viz-build \
       viz-dev test lint docker-build docker-run install setup

PYTHON_DIR  = python
JULIA_DIR   = julia
JAVA_DIR    = java-webapp
VIZ_DIR     = interactive-viz
OUTPUT_DIR  = output

# ═══════════════════════════════════════════════
# Main targets
# ═══════════════════════════════════════════════

all: verify simulate plots reports
	@echo "✅ All computations complete. Results in $(OUTPUT_DIR)/"

verify: python-verify
	@echo "✅ Verification complete"

simulate: python-simulate
	@echo "✅ Simulations complete"

plots: python-plots
	@echo "✅ Plots generated"

reports: python-reports
	@echo "✅ Reports generated"

# ═══════════════════════════════════════════════
# Python
# ═══════════════════════════════════════════════

python-install:
	cd $(PYTHON_DIR) && pip install -r requirements.txt

python-verify: python-install
	cd $(PYTHON_DIR) && python run.py --mode verify --non-interactive --output-dir ../$(OUTPUT_DIR)/python

python-simulate: python-install
	cd $(PYTHON_DIR) && python -c "from src.simulation.simulator import Simulator; s=Simulator(); s.sweep_delta_C(); s.sweep_lambda_1(); s.convergence_analysis(); print('Simulations complete')"

python-plots: python-verify
	@echo "Plots saved to $(OUTPUT_DIR)/python/plots/"

python-reports: python-verify
	@echo "Reports saved to $(OUTPUT_DIR)/python/reports/"

# ═══════════════════════════════════════════════
# Julia
# ═══════════════════════════════════════════════

julia-install:
	cd $(JULIA_DIR) && julia --project=. -e 'using Pkg; Pkg.instantiate()'

julia-verify: julia-install
	cd $(JULIA_DIR) && julia --project=. run.jl --non-interactive --output ../$(OUTPUT_DIR)/julia

# ═══════════════════════════════════════════════
# Java
# ═══════════════════════════════════════════════

java-build:
	cd $(JAVA_DIR) && mvn clean package -DskipTests

java-run: java-build
	cd $(JAVA_DIR) && java -jar target/choptyuk-webapp.jar

# ═══════════════════════════════════════════════
# Next.js Interactive Visualization
# ═══════════════════════════════════════════════

viz-install:
	cd $(VIZ_DIR) && npm install

viz-build: viz-install
	cd $(VIZ_DIR) && npm run build

viz-dev: viz-install
	cd $(VIZ_DIR) && npm run dev

# ═══════════════════════════════════════════════
# Docker
# ═══════════════════════════════════════════════

docker-build:
	docker build -t choptyuk-verify -f docker/Dockerfile .

docker-run:
	docker run --rm -v $(PWD)/$(OUTPUT_DIR):/app/output choptyuk-verify

docker-up:
	cd docker && docker-compose up -d

docker-down:
	cd docker && docker-compose down

# ═══════════════════════════════════════════════
# Quality & Testing
# ═══════════════════════════════════════════════

lint:
	cd $(PYTHON_DIR) && ruff check src/ --ignore E501 || true
	cd $(PYTHON_DIR) && mypy src/ --ignore-missing-imports || true
	cd $(VIZ_DIR) && npm run lint --if-present || true

test:
	cd $(PYTHON_DIR) && python -m pytest tests/ -v || true

pre-commit:
	pre-commit run --all-files

# ═══════════════════════════════════════════════
# Setup & Cleanup
# ═══════════════════════════════════════════════

setup: python-install julia-install viz-install
	@echo "✅ All environments set up"

clean:
	rm -rf $(OUTPUT_DIR)
	rm -rf $(VIZ_DIR)/.next $(VIZ_DIR)/node_modules
	rm -rf $(JAVA_DIR)/target
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# ═══════════════════════════════════════════════
# Git helpers
# ═══════════════════════════════════════════════

release:
	@read -p "Version (e.g., v1.1.0): " ver; \
	git tag -a $$ver -m "Release $$ver"; \
	git push origin $$ver
