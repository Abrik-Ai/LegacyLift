# LegacyLift — Protect Stage Report

**Stage:** Protect  
**Depends on:** `reports/analysis.md`  
**Golden files:** `tests/golden/*.json` (15 files, captured on Python 2.7.18)  
**Test file:** `tests/test_characterization.py`  
**Capture script:** `tools/capture_golden.py` (Python 2.7) via `tools/run_capture.sh`  
**Legacy baseline runner:** `tools/run_legacy_tests.sh`  

---

## Python 2.7 Baseline Result

Golden files were generated and tests were run against the original legacy
source inside the official `python:2.7` Docker image (Python 2.7.18,
numpy 1.16.6, pytest 4.6.11).

```
platform linux2 -- Python 2.7.18, pytest-4.6.11
collected 31 items

31 passed in 15.30 seconds
```

All 31 tests pass unconditionally on Python 2.7. The two integer-division
tests (`test_update_mini_batch_int_eta` in `TestNetwork` and `TestNetwork2`)
use a **conditional** xfail marker:

```python
@pytest.mark.xfail(sys.version_info >= (3,), strict=True, reason=...)
```

On Python 2.7 the condition evaluates to `False`, the marker is inactive,
and both tests run as plain `PASS`. On Python 3 the condition is `True`,
the test body fails (floor-division vs true-division), and pytest records
the expected `XFAIL`.

---

## Summary

31 characterization (golden-master) tests across three modules lock the
Python 2.7 behavior of the legacy code before any modernisation begins.
All tests **pass or are intentionally xfail** on the legacy Python 2.7 source.

The test suite is designed so that:
- Tests targeting **risky constructs** (`zip()` iterator, integer division)
  pass on Python 2.7 and fail (or are xfail) on Python 3.
- Tests targeting **safe constructs** (math, backprop, cost functions, save/load)
  pass on both Python 2.7 and Python 3 once the code is modernised.

---

## Test Counts by Module

| Module | Class | Tests | Golden files |
|--------|-------|------:|--------------|
| `network.py` | `TestNetwork` | 10 | 7 |
| `network2.py` | `TestNetwork2` | 11 | 6 |
| `mnist_loader.py` | `TestMnistLoader` | 10 | 2 |
| **Total** | | **31** | **15** |

---

## What Each Test Covers

### `TestNetwork` (10 tests)

| Test | What it pins | Py2.7 | Py3 (legacy) |
|------|-------------|-------|--------------|
| `test_sigmoid_1d` | `sigmoid()` on 1-D array | PASS | PASS* |
| `test_sigmoid_2d` | `sigmoid()` on 2-D array | PASS | PASS* |
| `test_sigmoid_prime_1d` | `sigmoid_prime()` on 1-D array | PASS | PASS* |
| `test_sigmoid_prime_2d` | `sigmoid_prime()` on 2-D array | PASS | PASS* |
| `test_feedforward_output` | `Network.feedforward()`, fixed weights | PASS | PASS* |
| `test_backprop_nabla_b` | Per-layer bias gradients from `backprop()` | PASS | PASS* |
| `test_backprop_nabla_w` | Per-layer weight gradients from `backprop()` | PASS | PASS* |
| `test_evaluate_score` | `Network.evaluate()` integer score | PASS | PASS* |
| `test_update_mini_batch_float_eta` ⚠️ | `update_mini_batch(eta=3.0)`, batch_size=3 | PASS | PASS* |
| `test_update_mini_batch_int_eta` ⚠️ `xfail` | `update_mini_batch(eta=3)`, batch_size=2 — Py2 floor-div (3/2=1) | XPASS | XFAIL |

### `TestNetwork2` (11 tests)

| Test | What it pins | Py2.7 | Py3 (legacy) |
|------|-------------|-------|--------------|
| `test_quadratic_cost_fn` | `QuadraticCost.fn(a, y)` | PASS | PASS* |
| `test_quadratic_cost_delta` | `QuadraticCost.delta(z, a, y)` | PASS | PASS* |
| `test_crossentropy_cost_fn` | `CrossEntropyCost.fn(a, y)` | PASS | PASS* |
| `test_crossentropy_cost_delta` | `CrossEntropyCost.delta(z, a, y)` | PASS | PASS* |
| `test_feedforward_output` | `Network.feedforward()`, fixed weights | PASS | PASS* |
| `test_backprop_nabla_b` | Per-layer bias gradients from `backprop()` | PASS | PASS* |
| `test_backprop_nabla_w` | Per-layer weight gradients from `backprop()` | PASS | PASS* |
| `test_update_mini_batch_float_eta` ⚠️ | `update_mini_batch(eta=3.0, lmbda=0.1, n=100)`, batch_size=3 | PASS | PASS* |
| `test_update_mini_batch_int_eta` ⚠️ `xfail` | `update_mini_batch(eta=3)`, batch_size=2 — Py2 floor-div | XPASS | XFAIL |
| `test_save_load_feedforward` | `save()` + `load()` round-trip preserves `feedforward()` | PASS | PASS* |
| `test_save_load_cost_class` | `save()` + `load()` restores cost class name | PASS | PASS* |

### `TestMnistLoader` (10 tests)

| Test | What it pins | Py2.7 | Py3 (legacy) |
|------|-------------|-------|--------------|
| `test_vectorized_result_shape` | Output always `(10, 1)` for all 10 digits | PASS | PASS* |
| `test_vectorized_result_values` | Exact values for all 10 digits | PASS | PASS* |
| `test_vectorized_result_one_hot` | Structural one-hot check | PASS | PASS* |
| `test_load_data_wrapper_lengths` ⚠️ | `len(data)` works; guards `zip()` iterator bug | PASS | FAIL |
| `test_load_data_wrapper_training_shapes` ⚠️ | Training `x` shape `(784,1)`, `y` shape `(10,1)` | PASS | FAIL |
| `test_load_data_wrapper_validation_shapes` ⚠️ | Validation `x` shape `(784,1)` | PASS | FAIL |
| `test_load_data_wrapper_test_shapes` ⚠️ | Test `x` shape `(784,1)` | PASS | FAIL |
| `test_load_data_wrapper_training_x0_first5` ⚠️ | First 5 pixel values of training sample 0 | PASS | FAIL |
| `test_load_data_wrapper_training_y0_first5` ⚠️ | First 5 values of one-hot label 0 | PASS | FAIL |
| `test_load_data_wrapper_second_iteration` ⚠️ | Re-indexing `data[0]` returns same value | PASS | FAIL |

_*Py3 (legacy) means: running the legacy unmodified source under Python 3 without any compat shim.
These tests will only pass on Py3 once the code is modernised._

⚠️ = tests that directly guard a risky behavior identified in `reports/analysis.md`

---

## Risky Behavior Coverage

| Risk (from analysis.md) | Test(s) | Py2.7 result | Py3 after modernisation |
|---|---|---|---|
| `zip()` returns iterator (ML-3,4,5) | 7 `TestMnistLoader` load_data_wrapper tests | PASS | Will PASS once `list(zip())` fix applied |
| `eta/len()` integer division (NW-5,6 / N2-9,10) | `test_update_mini_batch_int_eta` (x2) | XPASS (floor-div golden matches) | XFAIL — will FAIL until `float()` cast added |
| `cPickle` removed (ML-1,2) | All `TestMnistLoader` tests (import guard) | PASS | Will PASS once `cPickle` -> `pickle` applied |

---

## Integer-Division Test Design

Both int-eta tests use a mini-batch of **size 2** with `eta=3`:

```
Python 2.7:  3 / 2  ==  1    (integer floor division)
Python 3:    3 / 2  ==  1.5  (true division)
```

The golden values in `network_update_mini_batch_int_eta.json` and
`network2_update_mini_batch_int_eta.json` were captured on Python 2.7 and
reflect the floor-division result. The tests use a conditional marker:

```python
@pytest.mark.xfail(sys.version_info >= (3,), strict=True, reason=...)
```

| Runtime | xfail condition | Test body | pytest result |
|---------|----------------|-----------|---------------|
| Python 2.7 | `False` (inactive) | passes | `PASS` |
| Python 3 (legacy) | `True` (active) | fails (1.5 vs 1) | `XFAIL` |
| Python 3 (modernised) | `True` (active) | passes | `XPASS` |

`strict=True` on the modernised path turns `XPASS` into a hard failure,
which flags that the test should be updated to a plain assertion once the
integer-division fix is confirmed working.

---

## How to Run

### Regenerate golden files (Python 2.7, Docker)

```bash
bash tools/run_capture.sh
```

### Run characterization tests against the Python 2.7 legacy baseline (Docker)

```bash
bash tools/run_legacy_tests.sh
# Expected: 29 passed, 2 xpassed -- exit 0
```

### Run characterization tests against the modernised code (Python 3, default)

```bash
# Default: tests expect modules in modernized/src/
pytest tests/test_characterization.py -v

# Or explicitly:
LEGACYLIFT_SRC=modernized/src pytest tests/test_characterization.py -v
```

---

*Report generated by LegacyLift -- Protect stage. No files in `legacy-target/` were modified.*
