# Booking function complexity comparison

The numbered graph counts 91 edges, 69 nodes and one connected component. Its cyclomatic complexity is 91 − 69 + 2 = 24. Expanding short-circuit conditions adds five independent decisions. The expanded graph has 101 edges and 74 nodes, giving 29. That graph treats the assignment at patient.py line 269 as one statement. Expanding its inline conditional adds one decision, giving 30 under the analyzer's convention.

Radon 6.0.1 measured 30 for the same function body at lines 213–339. The source hash, five short-circuit decisions and inline conditional line are recorded in the JSON comparison. The result is Radon's measurement. SonarQube's patient-route complexity is a file aggregate, listed separately in the Sonar export.

Reproduction uses `python -m pip install radon==6.0.1`, followed by `python -m radon cc -j backend/routes/patient.py` from the repository root.

[Numbered CFG](booking-cfg.md) · [Radon raw output](radon-patient.json) · [Same-function reconciliation](cfg-comparison.json) · [Radon complexity rules](https://radon.readthedocs.io/en/latest/intro.html#cyclomatic-complexity)
