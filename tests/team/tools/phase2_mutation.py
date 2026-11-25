"""Run Cosmic Ray and two domain-specific mutants in temporary copies."""

import argparse
import ast
import difflib
import json
import os
import shutil
import subprocess
import sys
from collections import Counter
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[3]
ROUTE = Path("backend/routes/patient.py")
UNIT = ("tests/team/unit/test_appointment_rules.py",
        "tests/team/unit/test_appointment_slot_transactions.py")
FAST_SELECTION = (
    "MCC-111111 or MCC-110111 or MCC-111011 or MCC-111101 or MCC-111110 or "
    "test_br01 or test_br03 or test_br04_patient_writes or "
    "(test_late_booking_conflict_rolls_back and arjun)"
)


def command(program, *args):
    tool = shutil.which(program, path=str(Path(sys.executable).parent))
    if tool is None:
        raise RuntimeError(f"{program} is missing from the active Python environment")
    return [tool, *map(str, args)]


def run(args, sandbox, *, timeout=None, log=None):
    env = dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")
    if log is None:
        return subprocess.run(args, cwd=sandbox, env=env, timeout=timeout, capture_output=True)
    with log.open("xb") as f:
        return subprocess.run(args, cwd=sandbox, env=env, timeout=timeout, stdout=f, stderr=subprocess.STDOUT)


def copy_sandbox(dest):
    for path in ROOT.joinpath("backend").rglob("*.py"):
        relative = path.relative_to(ROOT)
        if any(part.startswith(".") or part in {"instance", "venv"} for part in relative.parts):
            continue
        target = dest / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    for relative in ("tests/team/conftest.py", "tests/team/phase2_support.py", "tests/team/mcc.py", *UNIT):
        target = dest / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    assert not (dest / "backend/instance").exists()


def source_guards(text):
    tree = ast.parse(text)
    functions = {item.name: item for item in tree.body if isinstance(item, ast.FunctionDef)}
    guards = {}
    for name, expression in (("book_appointment", "existing_booking"),
                             ("cancel_appointment", "appointment.status != 'booked'")):
        function = functions[name]
        matches = [node for node in ast.walk(function) if isinstance(node, ast.If) and
                   ast.unparse(node.test) == expression]
        if len(matches) != 1 or matches[0].test.lineno != matches[0].test.end_lineno:
            raise RuntimeError(f"Expected a single source guard for {name}")
        guards[name] = matches[0].test
    return functions, guards


def two_custom(sandbox, evidence, text, base_command):
    _, guards = source_guards(text)
    results = []
    for identifier, function, selection in (
        ("CM-01", "book_appointment", "MCC-111101"),
        ("CM-02", "cancel_appointment", "test_br03_cancel_transition"),
    ):
        test = guards[function]
        lines = text.splitlines(keepends=True)
        original = lines[test.lineno - 1]
        lines[test.lineno - 1] = original[:test.col_offset] + "False" + original[test.end_col_offset:]
        mutant = "".join(lines)
        compile(mutant, str(ROUTE), "exec")
        (evidence / f"{identifier}.diff").write_text("".join(difflib.unified_diff(
            text.splitlines(keepends=True), mutant.splitlines(keepends=True),
            fromfile=ROUTE.as_posix(), tofile=ROUTE.as_posix(),
        )), encoding="utf-8")
        (sandbox / ROUTE).write_text(mutant, encoding="utf-8")
        try:
            exit_code = run([*base_command, "-k", selection], sandbox, timeout=60,
                            log=evidence / f"{identifier}.txt").returncode
        finally:
            (sandbox / ROUTE).write_text(text, encoding="utf-8")
        status = {0: "survived", 1: "killed"}.get(exit_code, "incompetent")
        results.append({"id": identifier, "target": function, "line": test.lineno,
                        "assertions": selection, "exit": exit_code, "status": status})
    return results


def cosmic_ray(sandbox, evidence, source, base_command):
    functions, guards = source_guards(source)
    booking, cancellation = functions["book_appointment"], functions["cancel_appointment"]
    cutoff = next(n for n in booking.body if isinstance(n, ast.If) and ast.unparse(n.test) == "apt_date < today")
    availability = next(n for n in booking.body if isinstance(n, ast.Assign) and
                        ast.unparse(n.targets[0]) == "availability")
    end = next(n for n in cancellation.body if isinstance(n, ast.Try))
    ranges = [f"{cutoff.lineno}-{availability.lineno - 1}",
              f"{guards['book_appointment'].lineno - 7}-{booking.end_lineno}",
              f"{cancellation.lineno}-{end.lineno - 1}"]
    command_string = subprocess.list2cmdline([*base_command, "-k", FAST_SELECTION])
    config = sandbox / "cosmic.toml"
    config.write_text(
        "[cosmic-ray]\n"
        f'module-path = "{ROUTE.as_posix()}"\n'
        f"test-command = {json.dumps(command_string)}\n"
        "timeout = 45\n"
        "[cosmic-ray.distributor]\nname = 'local'\n"
        "[cosmic-ray.filters.line-filter.lines]\n"
        f'"{ROUTE.as_posix()}" = {json.dumps(ranges)}\n', encoding="utf-8"
    )
    shutil.copyfile(config, evidence / "effective-cosmic.toml")
    session = sandbox / "cosmic.sqlite"
    for name, args in (
        ("init", command("cosmic-ray", "init", config, session)),
        ("filter", command("cr-filter-lines", "--config", config, session)),
        ("baseline", command("cosmic-ray", "baseline", config)),
        ("exec", command("cosmic-ray", "exec", config, session)),
        ("report", command("cr-report", session)),
        ("dump", command("cosmic-ray", "dump", session)),
    ):
        print(f"Cosmic Ray {name}", flush=True)
        log = evidence / ("cosmic-dump.jsonl" if name == "dump" else f"cosmic-{name}.txt")
        if run(args, sandbox, log=log).returncode:
            raise RuntimeError(f"Cosmic Ray {name} failed, see {log}")
    records = [json.loads(line)[1] for line in
               (evidence / "cosmic-dump.jsonl").read_text(encoding="utf-8").splitlines()]
    outcomes = Counter(item.get("test_outcome") for item in records)
    workers = Counter(item.get("worker_outcome") for item in records)
    killed, survived = outcomes["killed"], outcomes["survived"]
    if not killed + survived:
        raise RuntimeError("Cosmic Ray produced no killed/survived results")
    return {"selected_ranges": ranges, "outcomes": dict(outcomes), "workers": dict(workers),
            "score": killed / (killed + survived), "killed": killed, "survived": survived}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--custom-only", action="store_true")
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()
    evidence = args.output.resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    with TemporaryDirectory(prefix="medihub-mutation-") as folder:
        sandbox = Path(folder)
        copy_sandbox(sandbox)
        original = (sandbox / ROUTE).read_text(encoding="utf-8")
        base = [Path(sys.executable).as_posix(), "-B", "-X", "utf8", "-m", "pytest",
                "-p", "no:cacheprovider", "-q", "--tb=short", *UNIT]
        if run(base, sandbox, timeout=90, log=evidence / "original-unit.txt").returncode:
            raise RuntimeError("Unmodified sandbox must pass before applying mutants")
        results = {"production_sha256": sha256((ROOT / ROUTE).read_bytes()).hexdigest(),
                   "custom": two_custom(sandbox, evidence, original, base)}
        if not args.custom_only:
            results["cosmic"] = cosmic_ray(sandbox, evidence, original, base)
        assert (sandbox / ROUTE).read_text(encoding="utf-8") == original
    (evidence / "summary.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))
    return int(args.enforce and (any(x["status"] != "killed" for x in results["custom"])
                                 or results.get("cosmic", {}).get("score", 0) < 0.75))


if __name__ == "__main__":
    sys.exit(main())
