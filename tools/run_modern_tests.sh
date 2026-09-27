#!/usr/bin/env bash
# tools/run_modern_tests.sh
# --------------------------
# Run the characterization tests against the MODERNIZED source inside a
# Python 3.12 Docker container with current numpy and pytest.
#
# Prerequisites: Docker must be installed and running.
# Usage (from repo root):
#   bash tools/run_modern_tests.sh
#
# Expected result (modernised code on Python 3.12):
#   29 passed, 2 xfailed
#   exit 0
#
# The two xfailed tests are the integer-division tests:
#   test_update_mini_batch_int_eta in TestNetwork and TestNetwork2
# These are EXPECTED to fail on Python 3 (golden captured Py2 floor-division).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Running characterization tests against modernized source (Python 3.12, Docker)..."
echo "    Repo: ${REPO_ROOT}"
echo ""

docker run --rm \
  -v "${REPO_ROOT}":/app \
  -w /app/modernized/src \
  -e LEGACYLIFT_SRC=/app/modernized/src \
  python:3.12 \
  sh -c "
    pip install --quiet 'numpy' 'pytest' && \
    python -m pytest /app/tests/test_characterization.py -v \
      --tb=short \
      2>&1
  "

echo ""
echo "==> Modern test run complete."
