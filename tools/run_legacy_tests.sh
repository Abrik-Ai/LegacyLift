#!/usr/bin/env bash
# tools/run_legacy_tests.sh
# --------------------------
# Run the characterization tests against the ORIGINAL legacy source inside
# a Python 2.7 Docker container.  All tests must pass (or be expected-fail)
# on the legacy code — characterization tests describe CURRENT behavior.
#
# Prerequisites: Docker must be installed and running.
# Usage (from repo root):
#   bash tools/run_legacy_tests.sh
#
# Expected result:
#   29 passed  (all network + network2 tests, and vectorized_result tests)
#    2 xfailed (int-eta tests — golden reflects Py2 floor-division, so they PASS
#               on Python 2.7 and are correctly NOT xfailed here; pytest reports
#               them as XPASS which is treated as a pass)
#
# Concretely on Python 2.7 ALL 31 tests should PASS (the xfail decorator is
# satisfied because the test body passes on Py2.7 — pytest records XPASS which
# is a success when strict=True on the decorator is not set in legacy mode).
#
# Note: xfail(strict=True) tests that PASS are reported as XPASS and treated as
# failures on Python 3, but on Python 2.7 those same tests pass, satisfying the
# intent of the mark.  pytest 4.6 on Python 2.7 reports XPASS as a warning, not
# a failure, so the suite exits 0.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Running characterization tests against legacy source (Python 2.7, Docker)..."
echo "    Repo: ${REPO_ROOT}"
echo ""

# Run pytest from legacy-target/src/ so that mnist_loader.load_data() can
# resolve its hardcoded relative path '../data/mnist.pkl.gz'.
# LEGACYLIFT_SRC points to the legacy source directory (already the CWD).
docker run --rm \
  -v "${REPO_ROOT}":/app \
  -w /app/legacy-target/src \
  -e LEGACYLIFT_SRC=/app/legacy-target/src \
  python:2.7 \
  sh -c "
    pip install --quiet 'pytest==4.6.11' 'numpy==1.16.6' && \
    python -m pytest /app/tests/test_characterization.py -v \
      --tb=short \
      --override-ini='asyncio_mode=auto' \
      2>&1
  "

echo ""
echo "==> Legacy baseline test run complete."
