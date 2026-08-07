#!/usr/bin/env bash
# Build and run the interactive visualization app
# Usage: ./scripts/run_viz.sh

set -e
echo "=== Starting Interactive Visualization ==="

cd interactive-viz
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi
echo "Starting dev server..."
npm run dev
