"""Check the frozen audit output and write a per-case semantic comparison."""

import argparse
import csv
import json
from collections import Counter
from hashlib import sha256
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "tests/team/evidence/phase2/phase1_reaudit"
ARCHIVE = RAW / "run-03"
EXPECTED = Counter({"pass": 67, "fail": 12, "policy pending": 15})


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(value, key=None):
    if isinstance(value, dict):
        return {k: normalize(v, k) for k, v in value.items()
                if k not in {"updated_at", "created_at"}}
    if isinstance(value, list):
        if key in {"db_before", "db_after", "rows"}:
            return [row[:6] for row in value]
        return [normalize(item) for item in value]
    return value


def load_cases(revision):
    raw = read(ARCHIVE / f"{revision}.json")
    server = (ARCHIVE / f"{revision}-server.log").read_text(encoding="utf-8")
    cases = {case["id"]: case for case in raw["cases"]}
    assert len(cases) == len(raw["cases"]) == 94
    assert Counter(case["verdict"] for case in cases.values()) == EXPECTED
    assert raw["summary"] == {**EXPECTED, "untested": 0}
    assert raw["smtp_attempts"] == [] and raw["url"] == "http://127.0.0.1:5001"
    assert "Verified disposable engine:" in server
    assert len([case for case in cases.values() if case["id"] != "P1-UI01"]) == 93
    for case in cases.values():
        assert f"{case['id']} {case['verdict']}" in server
        for step in case["steps"]:
            if step.get("method") in {"POST", "PUT", "DELETE"}:
                assert isinstance(step["db_before"], list) and isinstance(step["db_after"], list)
    steps = cases["P1-UI01"]["steps"]
    assert [row["db_after"][0][5] for row in steps if row.get("db_after")] == ["booked", "cancelled"]
    assert any("doctor" in step.get("ui", "") and "Cancelled" in step["ui"] for step in steps)
    assert '"POST /api/patient/appointments HTTP/1.1" 200' in server
    assert '"DELETE /api/patient/appointments/1 HTTP/1.1" 200' in server
    for name in ("booking", "cancellation", "doctor"):
        assert (ARCHIVE / f"{revision}-{name}.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    return cases


def outcomes(case):
    http = [f"{step['method']} {step['path']}={step['status']}" for step in case["steps"]
            if "status" in step]
    writes = [f"{step['db_before']} -> {step['db_after']}" for step in normalize(case["steps"])
              if step.get("db_before") is not None]
    return " | ".join(http), " | ".join(writes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    environment = read(ARCHIVE / "environment.json")
    development = ROOT / "backend/instance/medihub-database.db"
    assert environment["dev_db_before_sha256"] == environment["dev_db_after_sha256"]
    if development.is_file():
        assert sha256(development.read_bytes()).hexdigest() == environment["dev_db_after_sha256"]
    assert environment["baseline_commit"] == "e58ce855f5fb0c725ece13fa0a44d25486078465"
    assert environment["current_commit"] == "256efcb6e85feb9c16692b490a68fc8979674888"
    for name, expected in (("full", "6 failed, 6 passed"), ("smoke", "6 failed, 3 passed")):
        assert expected in (RAW / f"stage-d-{name}.log").read_text(encoding="utf-8")
    baseline, current = load_cases("baseline"), load_cases("current")
    assert baseline.keys() == current.keys()
    with (ROOT / "tests/team/test_registry.csv").open(encoding="utf-8", newline="") as f:
        registry = {row["test_id"]: row for row in csv.DictReader(f)}
    assert all(case_id in registry for case_id in baseline)
    with args.output.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("id", "scope", "oracle", "baseline_verdict", "current_verdict",
                         "semantic_match", "baseline_http", "baseline_db", "current_http", "current_db"))
        differences = []
        for case_id, left in baseline.items():
            right = current[case_id]
            assert left["verdict"] == right["verdict"]
            comparable = lambda case: normalize({k: v for k, v in case.items() if k != "error"})
            match = comparable(left) == comparable(right)
            if not match:
                differences.append(case_id)
            writer.writerow((case_id, left["scope"], left["expected"], left["verdict"], right["verdict"],
                             match, *outcomes(left), *outcomes(right)))
    print("94 unique IDs per build: 67 passed, 12 failed, 15 policy pending.")
    print("Equal verdicts for every ID; semantic differences:", differences)
    print("Raw snapshots own all timestamps; comparison omits them and free-form failure prose.")


if __name__ == "__main__":
    main()
