"""Reconcile native k6 summaries and tagged points without changing original output."""

from collections import Counter, defaultdict
from pathlib import Path
import argparse
import json


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def summarize(directory):
    run = read(directory / "run.json")
    native = read(directory / "summary.redacted.json")["metrics"]
    timings = native["http_req_duration{phase:steady}"]
    failure = native["phase5_unexpected{phase:steady}"]
    statuses, markers, totals = Counter(), defaultdict(dict), Counter()
    for line in (directory / "metrics.jsonl").open(encoding="utf-8"):
        entry = json.loads(line)
        if entry["type"] != "Point":
            continue
        metric, point = entry["metric"], entry["data"]
        tags, value = point["tags"], point["value"]
        if metric == "phase5_boundary_ms":
            markers[tags["event"]][tags["vu"]] = value
        if tags.get("phase") != "steady":
            continue
        if metric == "http_reqs":
            statuses[tags["status"]] += int(value)
        elif metric == "http_req_failed":
            totals["http_errors"] += int(value)
        elif metric == "phase5_unexpected":
            totals["operation_samples"] += 1
            totals["unexpected"] += int(value)
        elif metric == "checks":
            totals["checks"] += 1
            totals["failed_checks"] += int(value == 0)

    count = sum(statuses.values())
    assert count and count == totals["operation_samples"]
    durations = {key: value for key, value in timings.items() if key != "thresholds"}
    assert count == durations["count"]
    vus = run["profile"]["vus"]
    assert markers["entered"].keys() == markers["left"].keys() and len(markers["entered"]) == vus
    overlap = (min(markers["left"].values()) - max(markers["entered"].values())) / 1000
    assert overlap >= 60
    assert totals["checks"] == 2 * count
    period = run["targets"]["steady_seconds"]
    return {
        "id": directory.name,
        "vus": vus,
        "configured_seconds": period,
        "observed_common_vu_seconds": overlap,
        "start_utc": run["k6_started_utc"],
        "end_utc": run["k6_ended_utc"],
        "first_steady_marker_unix_ms": min(markers["entered"].values()),
        "last_steady_marker_unix_ms": max(markers["left"].values()),
        "completed": count,
        "requests_per_second": count / period,
        "duration_ms": durations,
        "status_counts": dict(statuses),
        **totals,
        "unexpected_pct": 100 * totals["unexpected"] / count,
        # The legacy --summary-export format encodes a failed threshold as true.
        "latency_thresholds": {rule: not failed for rule, failed in timings["thresholds"].items()},
        "failure_thresholds": {rule: not failed for rule, failed in failure["thresholds"].items()},
        "exit_code": run["exit_code"],
        "dashboard_http": run["dashboard_http"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", type=Path)
    args = parser.parse_args()
    results = [summarize(args.runs / f"P5-L{i:02}") for i in range(1, 5)]
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
