You are the Modernize and Verify stages of LegacyLift.
Context: reports/analysis.md (what to fix) and reports/protect.md (the safety net).

MODERNIZE
1. Copy legacy-target/src/mnist_loader.py, network.py and network2.py into modernized/src/.
   Also copy any data files they need so load_data() works from modernized/src.
   Never modify legacy-target/. Do not modernize network3.py (Theano, out of scope).
2. Modernize the copies to Python 3.12 with current NumPy, fixing every item in
   reports/analysis.md. Follow the official Python "Porting Python 2 Code to Python 3" guide
   and NumPy documentation. Do not use or copy existing Python 3 ports of this project.
3. Use one subagent per module, working in parallel.
4. Integer division: use true division (eta/len(mini_batch)). This is an intentional,
   documented behavior change. Keep the float-eta tests matching exactly.

VERIFY
5. Create tools/run_modern_tests.sh that runs the characterization tests against
   modernized/src inside Docker python:3.12 with current numpy and pytest.
6. Run it. If any test fails, fix the modernized code and rerun. Log every failure and its
   fix in reports/verify.md. If a change cannot be made to pass, revert that change.
7. Also show the "before" state: run the same tests against the ORIGINAL legacy code on
   Python 3.12 and record how they fail (e.g. SyntaxError on import).

REPORT
8. Recount deprecated/Python-2-only usages in modernized/src using the same rules as
   reports/analysis.md. Write reports/modernize.md and reports/modernize.json with
   before/after counts per file, the list of changes, and final test results.
