# LegacyLift — Analysis Report

**Stage:** Analyze  
**Target:** `legacy-target/src/`  
**Files in scope:** `mnist_loader.py`, `network.py`, `network2.py`  
**Files assessed for risk only:** `network3.py`  
**Original runtime:** Python 2.6 / 2.7  

---

## 1. Module Summaries

### `mnist_loader.py`
Loads the MNIST handwritten-digit dataset from a gzip-compressed pickle file
(`mnist.pkl.gz`). Exposes two public functions:

- **`load_data()`** — Deserialises the raw pickle and returns a 3-tuple of
  `(training_data, validation_data, test_data)` NumPy arrays.
- **`load_data_wrapper()`** — Wraps `load_data()` and reshapes images into
  column vectors; converts training labels into one-hot 10-dimensional vectors
  via `vectorized_result()`. Returns lazy `zip` iterables (in Python 2).

### `network.py`
Implements a minimal feedforward neural network trained with mini-batch
stochastic gradient descent (SGD) and backpropagation. Key features:

- Single `Network` class (old-style class inheriting `object`).
- Quadratic (MSE) cost function only.
- Sigmoid activation throughout.
- `SGD()` iterates over epochs, shuffles data, and prints progress.
- `backprop()` computes per-sample gradients; `update_mini_batch()` applies
  them with a fixed learning rate `eta`.
- **No regularisation, no model save/load.**

### `network2.py`
An enhanced version of `network.py` with the same overall architecture but
adding:

- Pluggable cost functions (`QuadraticCost`, `CrossEntropyCost`).
- L2 weight regularisation (λ parameter in `SGD` / `update_mini_batch`).
- Improved weight initialiser (`default_weight_initializer` scales by
  `1/√n_in`; `large_weight_initializer` reproduces the naïve approach from
  `network.py`).
- Training monitoring flags (cost and accuracy on training and evaluation data
  per epoch).
- **Model persistence** via `save()` / `load()` using `json`.
- A bare `print` (no arguments) is used at line 186 to emit a blank line
  between epoch reports.

### `network3.py` *(risk assessment only — out of scope)*
See §4.

---

## 2. Python 2-Only Constructs and Deprecated APIs

### `mnist_loader.py`

| # | Line | Construct | Issue | Modern Replacement |
|---|------|-----------|-------|--------------------|
| 1 | 13 | `import cPickle` | `cPickle` does not exist in Python 3; it was merged into `pickle` (which is C-accelerated by default). | `import pickle` |
| 2 | 43 | `cPickle.load(f)` | Call-site of the removed module. | `pickle.load(f, encoding='latin1')` (the `encoding` argument is required to load pickles created with Python 2 `str`/`bytes` objects) |
| 3 | 71 | `zip(training_inputs, training_results)` | In Python 2, `zip()` returns a **list**. In Python 3 it returns a lazy iterator. Downstream code in `network.py` calls `len(training_data)` and indexes into it; a bare iterator would cause `TypeError`. | Wrap with `list(zip(...))` |
| 4 | 73 | `zip(validation_inputs, va_d[1])` | Same list-vs-iterator issue. | `list(zip(...))` |
| 5 | 75 | `zip(test_inputs, te_d[1])` | Same list-vs-iterator issue. | `list(zip(...))` |

**Total for `mnist_loader.py`: 5**

---

### `network.py`

| # | Line | Construct | Issue | Modern Replacement |
|---|------|-----------|-------|--------------------|
| 1 | 56 | `xrange(epochs)` | `xrange` was removed in Python 3; `range` now returns a lazy sequence natively. | `range(epochs)` |
| 2 | 60 | `xrange(0, n, mini_batch_size)` | Same — `xrange` removed. | `range(0, n, mini_batch_size)` |
| 3 | 64 | `print "Epoch {0}: …"` | Print **statement** syntax; a `SyntaxError` in Python 3. | `print("Epoch {0}: …".format(…))` |
| 4 | 67 | `print "Epoch {0} complete".format(j)` | Print statement. | `print("Epoch {0} complete".format(j))` |
| 5 | 80 | `eta/len(mini_batch)` | In Python 2, `/` between two `int` values performs **floor division** (e.g. `0.5/4 → 0` if `eta` happened to be integral). Here `eta` is typically a `float`, so this is latent rather than always-broken — but it is a semantic hazard that must be audited. Both operands must be confirmed as `float`, or the expression rewritten as `eta / float(len(mini_batch))`. | Ensure `eta` is always `float`; or use `eta / float(len(mini_batch))` |
| 6 | 82 | `eta/len(mini_batch)` (biases update) | Same integer-division hazard as above. | Same fix |
| 7 | 112 | `xrange(2, self.num_layers)` | `xrange` removed. | `range(2, self.num_layers)` |

**Total for `network.py`: 7**

---

### `network2.py`

| # | Line | Construct | Issue | Modern Replacement |
|---|------|-----------|-------|--------------------|
| 1 | 159 | `xrange(epochs)` | `xrange` removed in Python 3. | `range(epochs)` |
| 2 | 163 | `xrange(0, n, mini_batch_size)` | `xrange` removed. | `range(0, n, mini_batch_size)` |
| 3 | 167 | `print "Epoch %s training complete" % j` | Print statement; `SyntaxError` in Python 3. | `print("Epoch %s training complete" % j)` |
| 4 | 171 | `print "Cost on training data: {}".format(cost)` | Print statement. | `print(…)` |
| 5 | 175–176 | `print "Accuracy on training data: {} / {}".format(…)` | Print statement (spans two physical lines via implicit string continuation). | `print(…)` |
| 6 | 180 | `print "Cost on evaluation data: {}".format(cost)` | Print statement. | `print(…)` |
| 7 | 184–185 | `print "Accuracy on evaluation data: {} / {}".format(…)` | Print statement. | `print(…)` |
| 8 | 186 | `print` (bare, no arguments) | Print statement with no arguments (emits a newline). In Python 3 this is a no-op expression that evaluates the `print` built-in object without calling it — **silently drops the blank line**. | `print()` |
| 9 | 204 | `eta/len(mini_batch)` (weights update) | Integer-division hazard (same as `network.py` lines 80/82). | Ensure `eta` is `float`; or `eta / float(len(mini_batch))` |
| 10 | 206 | `eta/len(mini_batch)` (biases update) | Same. | Same fix |
| 11 | 235 | `xrange(2, self.num_layers)` | `xrange` removed. | `range(2, self.num_layers)` |

**Total for `network2.py`: 11**

---

## 3. Outdated Dependencies

### NumPy usage patterns

All three in-scope files use NumPy via `import numpy as np`. The patterns used
(`np.random.randn`, `np.zeros`, `np.dot`, `np.exp`, `np.argmax`,
`np.linalg.norm`, `np.nan_to_num`, `ndarray.tolist`, `np.array`) are **stable
core APIs** that remain unchanged in NumPy 1.x and 2.x. No deprecated NumPy
APIs are used in `mnist_loader.py`, `network.py`, or `network2.py`.

> **Note on `network3.py` (out of scope):** Line 215 of `network3.py` computes
> `filter_shape[0]*np.prod(filter_shape[2:])/np.prod(poolsize)`. In NumPy ≥
> 1.20, `np.prod` on integer arrays returns an `int64`, so the `/` operator
> would perform **true division** in Python 3, yielding a `float`. This is not
> a problem for `network.py` / `network2.py`.

### Theano (`network3.py` — out of scope)

`network3.py` has a hard dependency on **Theano** (lines 40–51:
`import theano`, `import theano.tensor as T`, `theano.tensor.nnet.conv`,
`theano.tensor.signal.downsample`, etc.). Theano was **officially discontinued
and archived in 2017**. Its last PyPI release (1.0.5, 2020) does not support
Python 3.8+ or CUDA 10+. This dependency cannot be modernised in place; a
port would require replacing Theano with a current framework (e.g. PyTorch or
TensorFlow/Keras), which constitutes a full rewrite rather than a migration.

---

## 4. Risk Ratings

### `mnist_loader.py` — **Medium**

**Reason:** The `cPickle` → `pickle` change is mechanical and low-risk.
However, the `zip()` → `list(zip())` change is a **silent semantic break**:
the code produces lazy iterators instead of lists, and any consumer that calls
`len()`, indexes, or iterates more than once over the returned data will
fail at runtime rather than at import time. The bug only surfaces during
execution, making it easy to miss in a casual review.

### `network.py` — **Medium**

**Reason:** Three `xrange` calls and two `print` statements are
straightforward mechanical fixes. The integer-division hazard on `eta/len(…)`
(lines 80, 82) is latent: if a caller ever passes an integer `eta`, the
learning-rate divisor silently becomes 0 in Python 2 (floor division) — in
Python 3 it would be correct, but the Python 2 behaviour means the original
code may have been relying on floats being passed. This needs careful
verification. The file has no I/O beyond what `mnist_loader` provides, so
there are no pickle encoding concerns here.

### `network2.py` — **Medium**

**Reason:** Contains the largest count of deprecated usages (11), though most
are mechanical (`xrange`, `print` statements). The silent bare `print` at line
186 is a correctness issue that won't raise an exception. The same
integer-division hazard as `network.py` exists at lines 204 and 206. The
`save()` / `load()` JSON persistence uses the standard `json` module, which is
unchanged between Python 2 and 3, and is therefore **not** a risk. No issues
with model file compatibility.

### `network3.py` — **Out of Scope**

**Reason:** `network3.py` depends entirely on **Theano**, a discontinued
library (last release 2020, Python 3.8+ unsupported). The file uses Theano
symbolic tensor operations as its computation substrate; every layer class,
every training function, and the data-loading path all depend on Theano APIs.
A Python 3 migration of this file is not feasible without replacing the entire
backend, which is outside the scope of a syntactic/semantic upgrade.
Additionally, the file uses `cPickle` (line 35), `xrange` (lines 99, 161,
162, 169, 178), and print statements (lines 57–58, 63–64) — but these issues
are moot given the Theano blocker.

**This file should be excluded from the migration and flagged for a separate
architectural decision (replace with PyTorch/TensorFlow or remove).**

---

## 5. Deprecated/Python-2-Only Usage Counts Summary

| File | Count |
|------|-------|
| `mnist_loader.py` | 5 |
| `network.py` | 7 |
| `network2.py` | 11 |
| `network3.py` | out of scope (Theano dependency) |
| **Total (in-scope)** | **23** |

---

*Report generated by LegacyLift — Analyze stage. No files in `legacy-target/` were modified.*
