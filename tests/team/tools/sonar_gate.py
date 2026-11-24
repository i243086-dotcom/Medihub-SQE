"""Record and enforce overall Sonar measures in addition to its native gate."""

import argparse
import json
import os
import sys
from pathlib import Path

import requests


LIMITS = {"security_rating": 1.0, "reliability_rating": 2.0, "duplicated_lines_density": 3.0}
SCOPE_FILES = {"backend/app.py", "backend/routes/patient.py", "frontend/index.html", "frontend/js/app.js"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    metrics = [*LIMITS, "complexity", "cognitive_complexity", "code_smells", "bugs",
               "vulnerabilities", "coverage", "line_coverage", "branch_coverage",
               "sqale_index", "sqale_rating", "ncloc"]
    host = os.environ["SONAR_HOST_URL"]
    token = os.environ["SONAR_TOKEN"]
    with requests.Session() as client:
        client.trust_env = False
        client.headers["Authorization"] = "Bearer " + token
        result = client.get(host + "/api/measures/component",
                            params={"component": args.project, "metricKeys": ",".join(metrics)}, timeout=25)
        if result.status_code != 200:
            raise RuntimeError(f"Sonar measures returned HTTP {result.status_code}")
        report = result.json()
        tree = client.get(host + "/api/components/tree",
                          params={"component": args.project, "strategy": "leaves", "qualifiers": "FIL", "ps": 500},
                          timeout=25)
        tree.raise_for_status()
        source_paths = {item["path"] for item in tree.json()["components"]}
    measured = {item["metric"]: item.get("value") for item in report["component"]["measures"]}
    assertions = {key: key in measured and float(measured[key]) <= limit for key, limit in LIMITS.items()}
    checks = {
        "production_files_present": SCOPE_FILES <= source_paths,
        "test_files_absent_from_production": not any(path.startswith("tests/") for path in source_paths),
        "coverage_imported": float(measured.get("coverage", 0)) > 0 and "branch_coverage" in measured,
    }
    args.output.write_text(json.dumps({"raw": report, "limits": LIMITS, "passed": assertions,
                                      "scope_checks": checks, "source_paths": sorted(source_paths)},
                                      indent=2) + "\n", encoding="utf-8")
    print("Overall Sonar gate:", assertions)
    print("Sonar source and coverage checks:", checks)
    return int(not (all(assertions.values()) and all(checks.values())))


if __name__ == "__main__":
    sys.exit(main())
