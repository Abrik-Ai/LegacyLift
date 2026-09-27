#!/usr/bin/env bash
# tools/run_capture.sh
# ---------------------
# Run capture_golden.py inside a Python 2.7 Docker container.
# Produces golden JSON files in tests/golden/.
#
# Prerequisites: Docker must be installed and running.
# Usage (from repo root):
#   bash tools/run_capture.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Running golden-master capture under Python 2.7 (Docker)..."
# Run from legacy-target/src so that the legacy load_data() can resolve
# the hardcoded relative path '../data/mnist.pkl.gz'.
docker run --rm \
  -v "${REPO_ROOT}":/app \
  -w /app/legacy-target/src \
  python:2.7 \
  sh -c "pip install --quiet numpy==1.16.6 && python /app/tools/capture_golden.py"

echo ""
echo "==> Capture complete. Golden files written to tests/golden/:"
ls -1 "${REPO_ROOT}/tests/golden/"
