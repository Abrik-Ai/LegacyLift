You are the Protect stage of LegacyLift. Your job is to capture the CURRENT behavior of the
legacy code in legacy-target/ as characterization tests, BEFORE any modernization.
Use reports/analysis.md for context. Do not modify anything in legacy-target/.

Approach (golden-master testing):
1. Create tools/capture_golden.py that runs under Python 2.7. It imports the legacy modules
   (src/network.py, src/network2.py, src/mnist_loader.py), feeds them fixed, deterministic
   inputs, and saves the outputs to tests/golden/*.json. Use np.random.seed(42) and build
   small networks with explicit sizes like [4, 3, 2].
   Capture deterministic behavior only:
   - sigmoid and sigmoid_prime on fixed arrays
   - Network.feedforward with fixed weights/biases
   - Network.backprop gradients for a fixed input/label
   - Network.evaluate on a small fixed dataset
   - network2 cost functions (QuadraticCost, CrossEntropyCost) fn and delta
   - network2 save/load round trip
   - mnist_loader.vectorized_result for each digit 0-9
   - shapes and first values returned by mnist_loader.load_data_wrapper
   Do NOT capture full SGD training runs (random.shuffle differs between Python 2 and 3).
2. Create a script tools/run_capture.sh that runs capture_golden.py inside Docker:
   docker run --rm -v "$PWD":/app -w /app python:2.7 sh -c "pip install numpy==1.16.6 && python tools/capture_golden.py"
3. Create pytest tests in tests/test_characterization.py, organized by module, that load the
   golden JSON and compare against the code under test using np.allclose (rtol=1e-7).
   The code under test path must be configurable (default: modernized/src), so the same
   tests can later check the modernized code.
4. Use a separate subagent per module (network, network2, mnist_loader) and generate the
   tests in parallel.
5. Write a short summary to reports/protect.md: number of tests per module and what each covers.

Also make sure the tests cover the risky behaviors found in reports/analysis.md:
- Network.update_mini_batch with a fixed mini-batch and fixed weights, run twice:
  once with a float eta (3.0) and once with an integer eta (3), to capture the
  Python 2 integer-division behavior.
- mnist_loader.load_data_wrapper: capture that the returned data supports len()
  and can be iterated more than once.
