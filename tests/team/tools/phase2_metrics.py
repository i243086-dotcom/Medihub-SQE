"""Derive executed MCC/MC-DC and scoped white-box coverage from tool reports."""

import argparse
import ast
import csv
import json
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mcc import PREDICATES, ROWS, case_id, oracle


SCOPE = {
    "backend/routes/patient.py": (
        "get_dashboard", "get_departments", "get_available_slots", "get_doctors",
        "get_appointments", "book_appointment", "cancel_appointment", "get_history",
        "get_doctor_availability",
    ),
    "backend/routes/doctor.py": (
        "get_dashboard", "get_patient_history_details", "get_appointments", "get_patients",
        "update_appointment_status", "add_patient_history", "get_availability",
        "set_availability_slots", "get_available_slots",
    ),
    "backend/routes/admin.py": (
        "get_appointments", "update_appointment", "toggle_patient_blacklist",
        "update_doctor", "delete_doctor",
    ),
    "backend/routes/auth.py": ("login", "get_current_user", "logout"),
    "backend/decorators.py": None,
    "backend/models/appointment.py": None,
    "backend/models/doctor.py": None,
    "backend/models/patient.py": None,
    "backend/celery_tasks/email_template.py": None,
}


def case_results(path):
    records = {}
    for test in ET.parse(path).getroot().iter("testcase"):
        name = test.get("name")
        if "[" in name:
            name = name.rsplit("[", 1)[1].rstrip("]")
        if test.find("failure") is not None:
            status = "FAIL"
        elif test.find("error") is not None:
            status = "ERROR"
        elif test.find("skipped") is not None:
            status = "SKIPPED"
        else:
            status = "PASS"
        records[name] = status
    return records


def mcc(junit, out):
    results = case_results(junit)
    with (out / "br02-mcc.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["case", *PREDICATES, "decision", "expected_http", "first_reason",
                         "feasibility", "execution"])
        for bits in ROWS:
            status, reason = oracle(bits)
            status_text = results.get(case_id(bits), "NOT RUN")
            writer.writerow([case_id(bits), *map(int, bits), "accept" if all(bits) else "reject",
                             status, reason,
                             "Feasible: profile/doctor/date/availability set independently; conflicts use distinct doctor and patient rows.",
                             status_text])
    with (out / "br02-mcdc.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["predicate", "all_true", "one_false", "expected_http_pair", "executed_pair"])
        for i, predicate in enumerate(PREDICATES):
            bits = tuple(j != i for j in range(len(PREDICATES)))
            first, second = "MCC-111111", case_id(bits)
            writer.writerow([predicate, first, second, f"200 / {oracle(bits)[0]}",
                             f"{results.get(first, 'NOT RUN')} / {results.get(second, 'NOT RUN')}"])
    print(f"MCC executions: {sum(results.get(case_id(bits)) == 'PASS' for bits in ROWS)}/64 passed")


def selected_lines(path, functions):
    text = Path(path).read_text(encoding="utf-8")
    if functions is None:
        return set(range(1, len(text.splitlines()) + 1)), None
    nodes = {node.name: node for node in ast.parse(text).body if isinstance(node, ast.FunctionDef)}
    lines, ranges = set(), {}
    for name in functions:
        n = nodes[name]
        start = min((d.lineno for d in n.decorator_list), default=n.lineno)
        ranges[name] = [start, n.end_lineno]
        lines.update(range(start, n.end_lineno + 1))
    return lines, ranges


def coverage_report(path, out, enforce):
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not raw["meta"]["branch_coverage"]:
        raise ValueError("Branch measurement was not enabled")
    all_files = {name.replace("\\", "/"): data for name, data in raw["files"].items()}
    counts = {"statements": [0, 0], "branches": [0, 0]}
    files = {}
    for filename, names in SCOPE.items():
        data = all_files[filename]
        scope, ranges = selected_lines(filename, names)
        missed_lines = [line for line in data["missing_lines"] if line in scope]
        missed_branches = [arc for arc in data["missing_branches"] if arc[0] in scope]
        executed = sum(line in scope for line in data["executed_lines"])
        branches = sum(arc[0] in scope for arc in data["executed_branches"])
        files[filename] = {"function_ranges": ranges, "statements": [executed, executed + len(missed_lines)],
                           "branches": [branches, branches + len(missed_branches)],
                           "missing_lines": missed_lines, "missing_branches": missed_branches}
        for category in counts:
            for i, count in enumerate(files[filename][category]):
                counts[category][i] += count
    out.write_text(json.dumps({"scope_totals": counts, "repository_totals": raw["totals"],
                               "files": files}, indent=2) + "\n", encoding="utf-8")
    print(counts)
    return int(enforce and any(hit != total for hit, total in counts.values()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    mcc_parser = sub.add_parser("mcc")
    mcc_parser.add_argument("junit", type=Path)
    mcc_parser.add_argument("output", type=Path)
    cov_parser = sub.add_parser("coverage")
    cov_parser.add_argument("json", type=Path)
    cov_parser.add_argument("output", type=Path)
    cov_parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()
    if args.command == "mcc":
        mcc(args.junit, args.output)
        return 0
    return coverage_report(args.json, args.output, args.enforce)


if __name__ == "__main__":
    sys.exit(main())
