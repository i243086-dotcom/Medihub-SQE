"""Record and enforce overall Sonar measures in addition to its native gate."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import requests


LIMITS = {"security_rating": 1.0, "reliability_rating": 2.0, "duplicated_lines_density": 3.0}
SOURCE_EXTENSIONS = {".py", ".html", ".css", ".js"}
GENERATED_OR_LOCAL = {".venv", "instance", "__pycache__", "node_modules"}


def expected_sources():
    tracked = subprocess.check_output(["git", "ls-files", "-z", "--", "backend", "frontend"])
    return {name for name in tracked.decode("utf-8").split("\0")
            if Path(name).suffix in SOURCE_EXTENSIONS
            and not GENERATED_OR_LOCAL.intersection(Path(name).parts)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project")
    parser.add_argument("output", type=Path)
    parser.add_argument("--baseline")
    parser.add_argument("--revision")
    args = parser.parse_args()
    metrics = [*LIMITS, "complexity", "cognitive_complexity", "code_smells", "bugs",
               "vulnerabilities", "coverage", "line_coverage", "branch_coverage",
               "sqale_index", "sqale_rating", "ncloc", "ncloc_language_distribution",
               "security_hotspots", "new_coverage", "new_lines_to_cover"]
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
        tree_data = tree.json()
        source_paths = {item["path"] for item in tree_data["components"]}
        native = client.get(host + "/api/qualitygates/project_status",
                            params={"projectKey": args.project}, timeout=25)
        native.raise_for_status()
        native_gate = native.json()["projectStatus"]
        history = client.get(host + "/api/project_analyses/search",
                             params={"project": args.project, "ps": 2}, timeout=25)
        history.raise_for_status()
        analyses = history.json()
        issues = client.get(host + "/api/issues/search",
                            params={"componentKeys": args.project, "rules": "python:S4502"}, timeout=25)
        issues.raise_for_status()
        s4502 = [{key: item.get(key) for key in ("key", "rule", "status", "issueStatus", "component", "line", "hash")}
                 for item in issues.json()["issues"]]
        new_issues = client.get(host + "/api/issues/search", params={
            "componentKeys": args.project, "inNewCodePeriod": "true", "resolved": "false",
        }, timeout=25)
        new_issues.raise_for_status()
        new_findings = [{key: item.get(key) for key in ("rule", "component", "line", "message")}
                        for item in new_issues.json()["issues"]]
        route = client.get(host + "/api/measures/component", params={
            "component": f"{args.project}:backend/routes/patient.py",
            "metricKeys": "complexity,cognitive_complexity,ncloc",
        }, timeout=25)
        route.raise_for_status()
        patient_route = route.json()["component"]
    measured = {item["metric"]: item.get("value") for item in report["component"]["measures"]}
    assertions = {key: key in measured and float(measured[key]) <= limit for key, limit in LIMITS.items()}
    required = expected_sources()
    checks = {
        "production_files_present": bool(required) and required <= source_paths,
        "source_inventory_complete": len(source_paths) == tree_data["paging"]["total"],
        "test_files_absent_from_production": not any(path.startswith("tests/") for path in source_paths),
        "coverage_imported": float(measured.get("coverage", 0)) > 0 and "branch_coverage" in measured,
    }
    if args.baseline:
        revisions = [item.get("revision") for item in analyses["analyses"]]
        checks["candidate_and_baseline_revisions"] = revisions == [args.revision, args.baseline]
        coverage_gate = next((item for item in native_gate["conditions"]
                              if item["metricKey"] == "new_coverage"), None)
        coverable = next((int(item["period"]["value"]) for item in report["component"]["measures"]
                          if item["metric"] == "new_lines_to_cover" and "period" in item), 0)
        checks["native_new_coverage_evaluated"] = bool(coverage_gate) or (
            bool(native_gate.get("period")) and coverable < 20 and native_gate["ignoredConditions"]
        )
    args.output.write_text(json.dumps({"raw": report, "limits": LIMITS, "passed": assertions,
                                      "scope_checks": checks, "source_paths": sorted(source_paths),
                                      "missing_sources": sorted(required - source_paths), "s4502": s4502,
                                      "open_new_issues": new_findings,
                                      "patient_route": patient_route,
                                      "native_gate": native_gate, "analysis_history": analyses},
                                      indent=2) + "\n", encoding="utf-8")
    print("Overall Sonar gate:", assertions)
    print("Sonar source and coverage checks:", checks)
    print("Native gate and evaluated conditions:", native_gate["status"], native_gate["conditions"])
    print("Open new Sonar issues:", new_findings)
    return int(not (all(assertions.values()) and all(checks.values()) and native_gate["status"] == "OK"))


if __name__ == "__main__":
    sys.exit(main())
