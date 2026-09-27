You are the Report stage of LegacyLift.
Using reports/analysis.json, reports/protect.md, reports/verify.md, reports/modernize.json
and reports/modernize.md, create docs/index.html: a single self-contained, polished,
responsive HTML page (inline CSS, no external requests) that works on GitHub Pages.

It must show:
1. Title "LegacyLift" and one-line tagline: safe, verified legacy code modernization with IBM Bob 2.0.
2. The 5-stage pipeline (Analyze, Protect, Modernize, Verify, Report) as a visual flow.
3. The target project: Michael Nielsen's Neural Networks and Deep Learning code (Python 2.7, MIT).
4. A before/after table: deprecated usages 23 -> 0 (per file), characterization tests 0 -> 31,
   Python 2.7 legacy baseline 31/31 passed, legacy code on Python 3.12: 0 passed / 29 failed,
   modernized code on Python 3.12: 29 passed / 0 failed / 2 documented intentional changes.
5. A "Silent bugs caught" section: zip() iterator, bare print, integer division (3/2),
   explaining why a simple find-and-replace would miss them.
6. The integer-division decision: detected, documented, intentionally fixed.
7. network3.py marked out of scope (Theano) with the reason.
8. Links to the reports and test files in the repository.
Use only numbers that appear in the report files. Also update README.md with a short
project overview, how to run each stage's scripts, and a link to the report page.

