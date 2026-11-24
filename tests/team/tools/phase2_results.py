"""Link final pytest cases, generated variations and actual mutation evidence."""

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET

from phase2_metrics import SCOPE, case_results, selected_lines


TEAM = Path("tests/team")
EVIDENCE = TEAM / "evidence/phase2/verification"
REGISTRY = TEAM / "test_registry.csv"
REFS = {
    "login": ("FR-09", "BR-04", "R03"),
    "departments": ("FR-01", "BR-04", "R05"),
    "doctors": ("FR-01", "BR-04", "R05"),
    "slots": ("FR-02;FR-04", "BR-01", "R04;R05"),
    "doctorAvailability": ("FR-01;FR-02", "BR-01", "R05"),
    "book": ("FR-03;FR-04", "BR-01;BR-02", "R01;R04;R08"),
    "cancel": ("FR-06;FR-07", "BR-03;BR-04", "R03;R06"),
    "patientList": ("FR-08", "BR-04", "R03;R06"),
    "doctorList": ("FR-08", "BR-04", "R03;R06"),
    "doctorStatus": ("Proposed FR-11", "BR-04", "R06"),
    "adminList": ("FR-08", "BR-04", "R06"),
    "adminStatus": ("Proposed FR-12", "BR-04", "R06;R08"),
}
USE_CASE = {
    "UC01": ("FR-01", "BR-04", "R05"),
    "UC02": ("FR-02;FR-04", "BR-01", "R04;R05"),
    "UC03": ("FR-03;FR-05", "BR-01;BR-02", "R02"),
    "UC04": ("FR-07;FR-08", "BR-04", "R03"),
    "UC05": ("FR-06;FR-07", "BR-03;BR-04", "R06"),
    "UC06": ("FR-08;FR-09", "BR-04", "R03;R06"),
}


def reference(name, parameter):
    if parameter.startswith("WBU-GEN-"):
        return REFS[parameter.split("-")[2]]
    if parameter.startswith("GEN-"):
        return REFS[parameter.split("-")[1]]
    if parameter.startswith("UC"):
        return USE_CASE[parameter.split("-")[0]]
    if parameter.startswith("MCC-"):
        return "FR-03;FR-04;FR-05;FR-10", "BR-02", "R02;R04;R05;R07"
    if any(term in name for term in ("concurrent", "uniqueness", "migration", "late_booking_conflict")):
        return "FR-05", "BR-02", "R01;R02"
    if "reopen" in name or "staff_transition" in name:
        return "Proposed FR-11;Proposed FR-12", "BR-03;BR-04", "R06"
    if "doctor_date_and_filter" in name:
        return "FR-08", "BR-04", "R03;R04"
    if "br01" in name or "slot" in name or "availability" in name:
        return "FR-02;FR-04", "BR-01", "R04;R05"
    if "br03" in name or "cancel" in name:
        return "FR-06;FR-07", "BR-03", "R06"
    if "blacklist" in name:
        return "FR-10", "BR-02", "R07"
    if "book" in name:
        return "FR-03;FR-04", "BR-02", "R08"
    if "status" in name or "reschedule" in name:
        return "Proposed FR-11;Proposed FR-12", "BR-04", "R06"
    if "history" in name or "serialization" in name:
        return "FR-08", "BR-04", "R06"
    if "inactive_doctor" in name or "doctor_edits" in name:
        return "FR-01", "BR-04", "R05"
    return "FR-09", "BR-04", "R03"


def passed(test):
    return not any(test.find(tag) is not None for tag in ("failure", "error", "skipped"))


def update_registry(suite):
    with REGISTRY.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames)
        historical = [row for row in reader if not (row["latest_evidence"] if "latest_evidence" in fields else "")
                      or row["test_id"].startswith(("SETUP-", "API-", "P1-"))]
    for key in ("latest_status", "latest_evidence"):
        if key not in fields:
            fields.append(key)
    old_nodes = {row["pytest_node"]: row for row in historical if row["pytest_node"]}
    for node, row in old_nodes.items():
        if node.endswith("::test_d4a_doctor_reopens_cancelled_appointment"):
            row.update(latest_status="superseded-proposed-oracle",
                       latest_evidence=suite.as_posix())
    rows = []
    by_level = defaultdict(Counter)
    for test in ET.parse(suite).getroot().iter("testcase"):
        classname, name = test.get("classname"), test.get("name")
        module = classname.replace(".", "/") + ".py"
        level = "Browser" if "/e2e/" in module else ("Unit" if "/unit/" in module else "API")
        outcome = "executed-pass" if passed(test) else ("not-executed" if test.find("skipped") is not None
                                                        else "executed-fail")
        by_level[level][outcome] += 1
        historical_node = Path(module).name + f"::{name}"
        if historical_node in old_nodes:
            old_nodes[historical_node].update(latest_status=outcome, latest_evidence=suite.as_posix())
            continue
        parameter = name.rsplit("[", 1)[1].rstrip("]").removeprefix("chromium-") if "[" in name else ""
        requirement, rule, risk = reference(name, parameter)
        case = parameter if parameter.startswith(("GEN-", "WBU-GEN-", "UC", "MCC-")) else "P2-" + re.sub(
            r"[^a-zA-Z0-9_-]+", "-", name.removeprefix("test_")
        ).strip("-")
        rows.append(dict(test_id=case, level=level, technique="generated EP/BVA" if parameter.startswith("GEN-")
                         else "use case" if level == "Browser" else "white-box" if level == "Unit"
                         else "integration", requirement=requirement, rule=rule, risk=risk, status=outcome,
                         pytest_node=module+"::"+name, evidence=suite.as_posix(),
                         issue="#12" if "concurrent" in name else ("#6" if "reopen" in name else ""),
                         latest_status=outcome, latest_evidence=suite.as_posix()))
    combined = historical + rows
    if len({row["test_id"] for row in combined}) != len(combined):
        raise RuntimeError("Duplicate registry case ID")
    if any(not row.get("latest_status") for row in old_nodes.values()):
        raise RuntimeError("A historical pytest node was not reconciled with the current suite")
    temp = REGISTRY.with_suffix(".tmp")
    with temp.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(combined)
    temp.replace(REGISTRY)
    return by_level


def generated(evidence, suite):
    def data(path):
        return {c["id"]: c for c in json.loads((TEAM / "data" / path).read_text())["cases"]}
    old = data("appointment_cases.json")
    changed = data("appointment_cases_proposed.json")
    current_results = case_results(suite)
    proposed_results = case_results(evidence / "generated-proposed.xml")
    with (evidence / "generated-constraint-diff.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["generated_id", "base_expected", "proposed_expected", "base_run", "proposed_run"])
        for identifier in sorted(old.keys() | changed.keys()):
            a = old.get(identifier, {}).get("expected_status")
            b = changed.get(identifier, {}).get("expected_status")
            if a != b:
                writer.writerow([identifier, a, b, current_results.get(identifier), proposed_results.get(identifier)])
    properties = {}
    for case in ET.parse(suite).getroot().iter("testcase"):
        match = re.search(r"\[(GEN-.*)\]$", case.get("name"))
        if match:
            properties[match[1]] = {p.get("name"): p.get("value") for p in case.iter("property")}
    with (evidence / "api-coverage-matrix.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["operation", "cases", "pass", "http_codes_observed", "roles_attempted",
                         "ep_partitions", "bva_points", "fields_varied", "response_schemas_checked"])
        for op in sorted(REFS):
            cases = [x for x in old.values() if x["operation"] == op]
            count = sum(current_results.get(x["id"]) == "PASS" for x in cases)
            statuses = {properties[x["id"]]["actual_status"] for x in cases}
            roles = {properties[x["id"]]["role"] for x in cases}
            writer.writerow([op, len(cases), count, ";".join(sorted(statuses)), ";".join(sorted(roles)),
                             sum(c["probe"] == "partition" for c in cases),
                             sum(c["probe"] == "boundary" for c in cases),
                             ";".join(sorted({c["field"] for c in cases if c["field"]})),
                             sum(bool(c["response_schema"]) and current_results.get(c["id"]) == "PASS" for c in cases)])


def mutation_key(result):
    return tuple(line.strip() for line in result.get("diff", "").splitlines()
                 if line.startswith(("+", "-")) and not line.startswith(("+++", "---")))


def mutation(evidence, final_label):
    def records(label, root):
        dump = root / label / "cosmic-dump.jsonl"
        return [json.loads(line) for line in dump.read_text(encoding="utf-8").splitlines()]
    first = records("mutation-before", EVIDENCE)
    after = records("mutation-after", EVIDENCE)
    final = records(final_label, evidence)
    latest = {mutation_key(result): result["test_outcome"] for _, result in final if result["diff"]}
    with (evidence / "mutation-survivor-review.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["mutant", "source_line_at_baseline", "operator", "change", "analysis",
                         "strengthened_test", "rerun"])
        for work, result in first:
            if result["test_outcome"] != "survived":
                continue
            mutation_spec = work["mutations"][0]
            change = mutation_key(result)
            text = " | ".join(change)
            if "apt_date <= today:" in text and "apt_date == today:" in text:
                analysis = "Equivalent under the preceding strict-past rejection."
                test = "MCC-110111 and today/future cutoff cases"
            elif "success" in text:
                analysis = "Weak response-envelope assertion or unreached rejection path in the subset."
                test = "Assert success flag independently of HTTP outcome; include past and missing-profile cases."
            elif "@patient_required" in text:
                analysis = "Authorization wrapper was bypassed by the focused handler tests."
                test = "Include authenticated and unauthorized role cases through real routing."
            elif "appointment for past dates" in text or "past dates" in text:
                analysis = "The selected mutation suite did not drive the strict-past rejection."
                test = "MCC-110111."
            elif "Profile not found" in text:
                analysis = "The selected suite always had a patient profile."
                test = "test_br03_profile_absent."
            else:
                analysis = "Missing distinguishing clock/date boundary or wrong HTTP-code assertion for a skipped decision."
                test = "Test today before/at/after and a later-hour future booking."
            writer.writerow([work["job_id"], mutation_spec["start_pos"][0], mutation_spec["operator_name"],
                             text, analysis, test, latest.get(change, "not-matched-on-updated-source")])
    totals = {}
    for label, rows in (("before", first), ("after", after), ("final", final)):
        tests = Counter(result["test_outcome"] for _, result in rows)
        workers = Counter(result["worker_outcome"] for _, result in rows)
        totals[label] = {"created": len(rows), "test_outcomes": {str(k): v for k, v in tests.items()},
                         "worker_outcomes": dict(workers),
                         "score_excluding_skipped": tests["killed"] / (tests["killed"] + tests["survived"])}
    totals["final"]["evidence_directory"] = final_label
    with (evidence / "mutation-final-survivors.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["mutant", "operator", "changed_lines", "assessment"])
        for job, result in final:
            if result["test_outcome"] != "survived":
                continue
            change = " | ".join(mutation_key(result))
            if "apt_date <= today:" in change and "apt_date == today:" in change:
                assessment = "Equivalent within the earlier past-date guard."
            elif "split('-', 2)[0]" in change:
                assessment = "Equivalent: both split limits leave the first segment unchanged."
            else:
                assessment = "Survived and needs individual review."
            writer.writerow([job["job_id"], job["mutations"][0]["operator_name"], change, assessment])
    return totals


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=EVIDENCE)
    parser.add_argument("--run-directory", default="release")
    parser.add_argument("--mutation-run", default="mutation-final")
    args = parser.parse_args()
    evidence = args.evidence
    suite = evidence / args.run_directory / "suite/junit.xml"
    levels = update_registry(suite)
    generated(evidence, suite)
    mutation_totals = mutation(evidence, args.mutation_run)
    code_lines = 0
    for filename, functions in SCOPE.items():
        lines, _ = selected_lines(filename, functions)
        source = Path(filename).read_text(encoding="utf-8").splitlines()
        code_lines += sum(bool(source[i - 1].strip()) and not source[i - 1].lstrip().startswith("#") for i in lines)
    summary = {"levels": levels, "mutation": mutation_totals, "scoped_nonblank_noncomment_lines": code_lines}
    (evidence / "phase2-result-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
