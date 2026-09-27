# -*- coding: utf-8 -*-
"""
capture_golden.py
~~~~~~~~~~~~~~~~~
Golden-master capture script.  Run under Python 2.7 to record the baseline
behaviour of the legacy modules BEFORE any modernisation.

Usage (via Docker):
    docker run --rm -v "$PWD":/app -w /app python:2.7 \
        sh -c "pip install numpy==1.16.6 && python tools/capture_golden.py"

Outputs JSON files to tests/golden/.
"""

from __future__ import print_function   # safe on Python 2.7+ and 3.x

import json
import os
import sys
import tempfile

import numpy as np

# ---------------------------------------------------------------------------
# Make legacy-target/src importable
# ---------------------------------------------------------------------------
SRC_DIR = os.path.join(os.path.dirname(__file__), '..', 'legacy-target', 'src')
sys.path.insert(0, os.path.abspath(SRC_DIR))

import network   as network_mod
import network2  as network2_mod
import mnist_loader

GOLDEN_DIR = os.path.join(os.path.dirname(__file__), '..', 'tests', 'golden')
os.makedirs(GOLDEN_DIR) if not os.path.isdir(GOLDEN_DIR) else None


def save(name, obj):
    path = os.path.join(GOLDEN_DIR, name + '.json')
    with open(path, 'w') as f:
        json.dump(obj, f, indent=2)
    print('  wrote', path)


def arr(a):
    """Recursively convert ndarray / nested list to plain Python lists."""
    if isinstance(a, np.ndarray):
        return a.tolist()
    if isinstance(a, (list, tuple)):
        return [arr(x) for x in a]
    # scalars – numpy float -> python float
    try:
        return float(a)
    except (TypeError, ValueError):
        return a


# ===========================================================================
# 1.  network.py — pure-math helpers
# ===========================================================================
print("==> Capturing network.py helpers ...")

np.random.seed(42)
z_1d = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
z_2d = np.array([[-1.0, 0.0], [0.5, 1.5]])

save('network_sigmoid', {
    'z_1d':            arr(z_1d),
    'sigmoid_z_1d':    arr(network_mod.sigmoid(z_1d)),
    'z_2d':            arr(z_2d),
    'sigmoid_z_2d':    arr(network_mod.sigmoid(z_2d)),
})

save('network_sigmoid_prime', {
    'z_1d':                 arr(z_1d),
    'sigmoid_prime_z_1d':   arr(network_mod.sigmoid_prime(z_1d)),
    'z_2d':                 arr(z_2d),
    'sigmoid_prime_z_2d':   arr(network_mod.sigmoid_prime(z_2d)),
})

# ===========================================================================
# 2.  network.py — Network.feedforward
# ===========================================================================
print("==> Capturing network.Network.feedforward ...")

np.random.seed(42)
net = network_mod.Network([4, 3, 2])
x_feed = np.array([[0.1], [0.5], [-0.3], [0.8]])

save('network_feedforward', {
    'sizes':   net.sizes,
    'biases':  arr(net.biases),
    'weights': arr(net.weights),
    'x':       arr(x_feed),
    'output':  arr(net.feedforward(x_feed)),
})

# ===========================================================================
# 3.  network.py — Network.backprop
# ===========================================================================
print("==> Capturing network.Network.backprop ...")

# Re-use same net and input; label is a one-hot column vector
y_bp = np.array([[1.0], [0.0]])
nabla_b, nabla_w = net.backprop(x_feed, y_bp)

save('network_backprop', {
    'sizes':   net.sizes,
    'biases':  arr(net.biases),
    'weights': arr(net.weights),
    'x':       arr(x_feed),
    'y':       arr(y_bp),
    'nabla_b': arr(nabla_b),
    'nabla_w': arr(nabla_w),
})

# ===========================================================================
# 4.  network.py — Network.evaluate
# ===========================================================================
print("==> Capturing network.Network.evaluate ...")

np.random.seed(42)
eval_net = network_mod.Network([4, 3, 2])
# Build a small fixed test dataset (10 samples, correct labels)
test_dataset = [
    (np.array([[0.1 * i], [0.2 * i], [0.3 * i], [0.4 * i]]), i % 2)
    for i in range(1, 11)
]
score = eval_net.evaluate(test_dataset)

save('network_evaluate', {
    'sizes':  eval_net.sizes,
    'biases': arr(eval_net.biases),
    'weights': arr(eval_net.weights),
    'dataset': [{'x': arr(x), 'y': int(y)} for x, y in test_dataset],
    'score':  int(score),
})

# ===========================================================================
# 5.  network.py — update_mini_batch  (float eta  AND  int eta)
# ===========================================================================
print("==> Capturing network.Network.update_mini_batch (float+int eta) ...")

def _make_mini_batch_3():
    """Reproducible 3-sample mini-batch for a [4,3,2] network (float-eta test)."""
    rng = np.random.RandomState(7)
    return [
        (rng.randn(4, 1), np.array([[1.0], [0.0]])),
        (rng.randn(4, 1), np.array([[0.0], [1.0]])),
        (rng.randn(4, 1), np.array([[1.0], [0.0]])),
    ]

def _make_mini_batch_2():
    """Reproducible 2-sample mini-batch for the int-eta test.
    With len=2 and eta=3: Python 2 computes 3/2 = 1 (floor division),
    while Python 3 computes 3/2 = 1.5 (true division).
    This makes the integer-division hazard actually visible in the golden values.
    """
    rng = np.random.RandomState(13)
    return [
        (rng.randn(4, 1), np.array([[1.0], [0.0]])),
        (rng.randn(4, 1), np.array([[0.0], [1.0]])),
    ]

def _net_state(n):
    return {'biases': arr(n.biases), 'weights': arr(n.weights)}

# --- float eta = 3.0, batch size = 3 ---
np.random.seed(42)
net_f = network_mod.Network([4, 3, 2])
mb_f = _make_mini_batch_3()
state_before_f = _net_state(net_f)
net_f.update_mini_batch(mb_f, 3.0)
state_after_f = _net_state(net_f)

save('network_update_mini_batch_float_eta', {
    'eta':          3.0,
    'sizes':        net_f.sizes,
    'mini_batch':   [{'x': arr(x), 'y': arr(y)} for x, y in mb_f],
    'state_before': state_before_f,
    'state_after':  state_after_f,
})

# --- int eta = 3, batch size = 2 ---
# Python 2: 3/2 == 1 (floor division); Python 3: 3/2 == 1.5 (true division).
# The golden values here are produced by Python 2.7 and reflect floor-division.
np.random.seed(42)
net_i = network_mod.Network([4, 3, 2])
mb_i = _make_mini_batch_2()
state_before_i = _net_state(net_i)
net_i.update_mini_batch(mb_i, 3)          # integer eta — Python 2 floor-divides: 3/2 = 1
state_after_i = _net_state(net_i)

save('network_update_mini_batch_int_eta', {
    'eta':          3,
    'batch_size':   2,
    'sizes':        net_i.sizes,
    'mini_batch':   [{'x': arr(x), 'y': arr(y)} for x, y in mb_i],
    'state_before': state_before_i,
    'state_after':  state_after_i,
})

# ===========================================================================
# 6.  network2.py — QuadraticCost and CrossEntropyCost
# ===========================================================================
print("==> Capturing network2 cost functions ...")

np.random.seed(0)
a_cost = np.array([0.9, 0.1, 0.05, 0.8])
y_cost = np.array([1.0, 0.0, 0.0,  1.0])
z_cost = np.array([2.0, -1.0, -3.0, 1.5])

save('network2_quadratic_cost', {
    'a': arr(a_cost), 'y': arr(y_cost), 'z': arr(z_cost),
    'fn':    float(network2_mod.QuadraticCost.fn(a_cost, y_cost)),
    'delta': arr(network2_mod.QuadraticCost.delta(z_cost, a_cost, y_cost)),
})

save('network2_crossentropy_cost', {
    'a': arr(a_cost), 'y': arr(y_cost), 'z': arr(z_cost),
    'fn':    float(network2_mod.CrossEntropyCost.fn(a_cost, y_cost)),
    'delta': arr(network2_mod.CrossEntropyCost.delta(z_cost, a_cost, y_cost)),
})

# ===========================================================================
# 7.  network2.py — Network.feedforward and backprop
# ===========================================================================
print("==> Capturing network2.Network.feedforward + backprop ...")

np.random.seed(42)
net2 = network2_mod.Network([4, 3, 2])
y_bp2 = np.array([[1.0], [0.0]])

ff2 = net2.feedforward(x_feed)
nb2, nw2 = net2.backprop(x_feed, y_bp2)

save('network2_feedforward_backprop', {
    'sizes':   net2.sizes,
    'biases':  arr(net2.biases),
    'weights': arr(net2.weights),
    'x':       arr(x_feed),
    'y':       arr(y_bp2),
    'feedforward_output': arr(ff2),
    'nabla_b': arr(nb2),
    'nabla_w': arr(nw2),
})

# ===========================================================================
# 8.  network2.py — update_mini_batch (float eta + int eta)
# ===========================================================================
print("==> Capturing network2.Network.update_mini_batch (float+int eta) ...")

def _net2_state(n):
    return {'biases': arr(n.biases), 'weights': arr(n.weights)}

# float eta — batch size 3
np.random.seed(42)
net2_f = network2_mod.Network([4, 3, 2])
mb2_f = _make_mini_batch_3()
state2_before_f = _net2_state(net2_f)
net2_f.update_mini_batch(mb2_f, 3.0, lmbda=0.1, n=100)
state2_after_f = _net2_state(net2_f)

save('network2_update_mini_batch_float_eta', {
    'eta': 3.0, 'lmbda': 0.1, 'n': 100,
    'sizes': net2_f.sizes,
    'mini_batch':   [{'x': arr(x), 'y': arr(y)} for x, y in mb2_f],
    'state_before': state2_before_f,
    'state_after':  state2_after_f,
})

# int eta — batch size 2: Python 2 computes 3/2 = 1 (floor), Python 3 gives 1.5
np.random.seed(42)
net2_i = network2_mod.Network([4, 3, 2])
mb2_i = _make_mini_batch_2()
state2_before_i = _net2_state(net2_i)
net2_i.update_mini_batch(mb2_i, 3, lmbda=0.1, n=100)
state2_after_i = _net2_state(net2_i)

save('network2_update_mini_batch_int_eta', {
    'eta': 3, 'batch_size': 2, 'lmbda': 0.1, 'n': 100,
    'sizes': net2_i.sizes,
    'mini_batch':   [{'x': arr(x), 'y': arr(y)} for x, y in mb2_i],
    'state_before': state2_before_i,
    'state_after':  state2_after_i,
})

# ===========================================================================
# 9.  network2.py — save / load round-trip
# ===========================================================================
print("==> Capturing network2.Network save/load round-trip ...")

np.random.seed(42)
net2_save = network2_mod.Network([4, 3, 2])
ff_before_save = net2_save.feedforward(x_feed)

tmp = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
tmp.close()
try:
    net2_save.save(tmp.name)
    net2_loaded = network2_mod.load(tmp.name)
    ff_after_load = net2_loaded.feedforward(x_feed)
finally:
    os.unlink(tmp.name)

save('network2_save_load', {
    'sizes':              net2_save.sizes,
    'biases':             arr(net2_save.biases),
    'weights':            arr(net2_save.weights),
    'x':                  arr(x_feed),
    'feedforward_before': arr(ff_before_save),
    'feedforward_after':  arr(ff_after_load),
    'cost_class':         str(net2_save.cost.__name__),
})

# ===========================================================================
# 10.  mnist_loader — vectorized_result
# ===========================================================================
print("==> Capturing mnist_loader.vectorized_result ...")

vr = {}
for digit in range(10):
    vec = mnist_loader.vectorized_result(digit)
    vr[str(digit)] = arr(vec)

save('mnist_loader_vectorized_result', {'digits': vr})

# ===========================================================================
# 11.  mnist_loader — load_data_wrapper shapes and first values
# ===========================================================================
print("==> Capturing mnist_loader.load_data_wrapper ...")

tr, va, te = mnist_loader.load_data_wrapper()

# Capture len() to document the list-vs-iterator contract
tr_len = len(tr)
va_len = len(va)
te_len = len(te)

# First element from each split
tr_x0, tr_y0 = tr[0]
va_x0, va_y0 = va[0]
te_x0, te_y0 = te[0]

# Verify second iteration works (list semantics)
tr_x0_again, _ = tr[0]
second_iter_matches = bool(np.allclose(tr_x0, tr_x0_again))

save('mnist_loader_load_data_wrapper', {
    'training_len':   tr_len,
    'validation_len': va_len,
    'test_len':       te_len,
    'training_x0_shape':   list(tr_x0.shape),
    'training_y0_shape':   list(tr_y0.shape),
    'validation_x0_shape': list(va_x0.shape),
    'validation_y0_dtype': str(va_y0.__class__.__name__),
    'test_x0_shape':       list(te_x0.shape),
    'test_y0_dtype':       str(te_y0.__class__.__name__),
    'training_x0_first5':  arr(tr_x0[:5].flatten()),
    'training_y0_first5':  arr(tr_y0[:5].flatten()),
    'second_iter_matches': second_iter_matches,
})

print("\nAll golden files captured successfully.")
