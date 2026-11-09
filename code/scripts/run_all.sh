#!/usr/bin/env bash
# Run all implementations and compare results
# Usage: ./scripts/run_all.sh [output_dir]

set -e
OUTPUT_DIR="${1:-output_full}"
echo "=== Running All Implementations ==="

# Python
echo ""
echo "--- Python Verification ---"
cd python
pip install -q -r requirements.txt 2>/dev/null || true
python run.py --mode verify --non-interactive --output-dir "../$OUTPUT_DIR/python"
cd ..

# Julia (if available)
if command -v julia &>/dev/null; then
    echo ""
    echo "--- Julia Verification ---"
    cd julia
    julia --project=. -e 'using Pkg; Pkg.instantiate()' 2>/dev/null || true
    julia --project=. run.jl --non-interactive --output "../$OUTPUT_DIR/julia"
    cd ..
else
    echo "Julia not found, skipping."
fi

echo ""
echo "=== All implementations complete ==="
echo "Results in $OUTPUT_DIR/"
