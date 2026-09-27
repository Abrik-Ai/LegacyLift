# LegacyLift

**Safe, verified legacy code modernization with IBM Bob 2.0.**

LegacyLift is a 5-stage pipeline that upgrades legacy Python 2.7 code to
Python 3.12 without guessing. Every behavioral change is either proven safe by
characterization tests or documented as an intentional decision.

**Target project:** Michael Nielsen's *Neural Networks and Deep Learning*
(Python 2.7, MIT) — `mnist_loader.py`, `network.py`, `network2.py`.

📄 **[View the full report →](docs/index.html)**

---

## The 5 Stages

| # | Stage | What it does |
|---|-------|-------------|
| 1 | **Analyze** | Catalog all deprecated constructs per file and assign risk levels. |
| 2 | **Protect** | Write characterization (golden-master) tests against the live Python 2.7 source. Lock the baseline. |
| 3 | **Modernize** | Apply the fixes identified in the analysis. Document intentional semantic changes. |
| 4 | **Verify** | Run the full test suite against the modernized code on Python 3.12. All tests must pass. |
| 5 | **Report** | Generate a consolidated HTML summary page (`docs/index.html`). |

---

## Results at a Glance

| Metric | Before | After |
|--------|-------:|------:|
| Deprecated usages (in-scope files) | 23 | 0 |
| Characterization tests | 0 | 31 |
| Tests passing on Python 2.7 | 31 / 31 | — |
| Tests on Python 3.12 (legacy source) | 0 passed / 29 failed | — |
| Tests on Python 3.12 (modernized) | — | 29 passed / 0 failed |
| Documented intentional changes (XFAIL) | — | 2 |

---

## Running Each Stage

### Prerequisites

- Docker (for Python 2.7 and Python 3.12 isolated environments)
- Python 3 + pytest (for local modernized-code runs)

### Stage 1 — Analyze

The analysis output is already committed at `reports/analysis.json`.
To re-run the analysis prompt, open `prompts/01-analyze.md` with IBM Bob.

### Stage 2 — Protect

**Capture golden files** (requires Python 2.7 Docker image):

```bash
bash tools/run_capture.sh
```

**Verify the Python 2.7 baseline** (31 tests must pass):

```bash
bash tools/run_legacy_tests.sh
# Expected: 29 passed, 2 xpassed -- exit 0
```

### Stage 3 — Modernize

The modernized source is in `modernized/src/`. To re-run the modernization
prompt, open `prompts/02-modernize.md` with IBM Bob.

### Stage 4 — Verify

**Run the characterization tests against the modernized source on Python 3.12**
(Docker):

```bash
bash tools/run_modern_tests.sh
# Expected: 29 passed, 2 xfailed -- exit 0
```

Or locally (requires Python 3 + current numpy + pytest):

```bash
LEGACYLIFT_SRC=modernized/src pytest tests/test_characterization.py -v
```

### Stage 5 — Report

The report page is at [`docs/index.html`](docs/index.html) — viewable locally
or via GitHub Pages.

---

## Repository Layout

```
legacy-target/src/      Original Python 2.7 source (never modified)
modernized/src/         Modernized Python 3.12 source
tests/
  test_characterization.py   31 characterization tests
  golden/                    15 golden JSON files (captured on Python 2.7)
tools/
  capture_golden.py          Golden-file capture script (Python 2.7)
  run_capture.sh             Docker wrapper: capture golden files
  run_legacy_tests.sh        Docker wrapper: test legacy source on Python 2.7
  run_modern_tests.sh        Docker wrapper: test modernized source on Python 3.12
reports/
  analysis.json              Stage 1 — deprecated-usage catalog
  protect.md                 Stage 2 — characterization test report
  modernize.json             Stage 3 — machine-readable change log
  modernize.md               Stage 3 — narrative change log
  verify.md                  Stage 4 — test results before & after
docs/
  index.html                 Stage 5 — consolidated HTML report page
prompts/                    IBM Bob prompt files for each stage
```

---

## License

MIT — same as the target project.
