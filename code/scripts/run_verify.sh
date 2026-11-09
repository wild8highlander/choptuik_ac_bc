#!/usr/bin/env bash
# Run full verification with Python (non-interactive)
# Usage: ./scripts/run_verify.sh [output_dir]

set -e
OUTPUT_DIR="${1:-output}"

echo "=== Choptyuk Spinor Corrections - Verification Script ==="
echo "Output directory: $OUTPUT_DIR"

cd python
pip install -q -r requirements.txt 2>/dev/null || true
python run.py --mode verify --non-interactive --output-dir "../$OUTPUT_DIR"

echo "Verification complete. Results in $OUTPUT_DIR/"
