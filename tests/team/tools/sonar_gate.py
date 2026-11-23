"""Record and enforce overall Sonar measures in addition to its native gate."""

import argparse
import json
import os
import sys
from pathlib import Path

import requests


LIMITS = {"security_rating": 1.0, "reliability_rating": 2.0, "duplicated_lines_density": 3.0}


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
        result = client.get(host + "/api/measures/component", headers={"Authorization": "Bearer " + token},
                            params={"component": args.project, "metricKeys": ",".join(metrics)}, timeout=25)
        if result.status_code != 200:
            raise RuntimeError(f"Sonar measures returned HTTP {result.status_code}")
        report = result.json()
    measured = {item["metric"]: item.get("value") for item in report["component"]["measures"]}
    assertions = {key: key in measured and float(measured[key]) <= limit for key, limit in LIMITS.items()}
    args.output.write_text(json.dumps({"raw": report, "limits": LIMITS, "passed": assertions},
                                      indent=2) + "\n", encoding="utf-8")
    print("Overall Sonar gate:", assertions)
    return int(not all(assertions.values()))


if __name__ == "__main__":
    sys.exit(main())
