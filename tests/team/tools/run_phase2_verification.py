"""Run the scoped white-box gate and complete Phase 2 suite with reports."""

import argparse
import json
import os
import re
import subprocess
import sys
from hashlib import sha256
from pathlib import Path


def run_suite(out, tests, browser=False):
    out.mkdir()
    cmd = [sys.executable, "-B", "-X", "utf8", "-m", "pytest", "-p", "no:cacheprovider",
           "-q", "-s", "--tb=short", "-o", "junit_family=legacy", tests,
           "--junitxml=" + str(out / "junit.xml"), "--cov=backend", "--cov-branch",
           "--cov-report=json:" + str(out / "coverage.json"),
           "--cov-report=xml:" + str(out / "coverage.xml"),
           "--cov-report=html:" + str(out / "htmlcov")]
    if browser:
        cmd += ["--browser", "chromium", "--html=" + str(out / "pytest.html"),
                "--self-contained-html", "--screenshot", "only-on-failure", "--output", str(out / "screenshots")]
    env = dict(os.environ, COVERAGE_FILE=str(out / ".coverage"))
    with (out / "pytest.txt").open("xb") as stream:
        result = subprocess.run(cmd, stdout=stream, stderr=subprocess.STDOUT, env=env)
    for p in (out / "pytest.txt", out / "junit.xml"):
        if re.search(rb"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", p.read_bytes()):
            raise RuntimeError("An unpublishable bearer-like value appeared in the test output")
    print(out.name, "exit", result.returncode,
          (out / "pytest.txt").read_text(encoding="utf-8").splitlines()[-1], flush=True)
    subprocess.run([sys.executable, "tests/team/tools/phase2_metrics.py", "coverage",
                    str(out / "coverage.json"), str(out / "scoped.json")], check=True)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--unit-only", action="store_true")
    args = parser.parse_args()
    path = args.output.resolve()
    path.mkdir(parents=True, exist_ok=False)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    recorded = {"HEAD": head, "python": sys.version.split()[0],
                "backend_sha256": {p.as_posix(): sha256(p.read_bytes()).hexdigest()
                                   for p in sorted(Path("backend").rglob("*.py"))}}
    (path / "environment.json").write_text(json.dumps(recorded, indent=2) + "\n", encoding="utf-8")
    unit = run_suite(path / "unit", "tests/team/unit")
    subprocess.run([sys.executable, "tests/team/tools/phase2_metrics.py", "mcc",
                    str(path / "unit/junit.xml"), str(path)], check=True)
    suite = 0 if args.unit_only else run_suite(path / "suite", "tests/team", browser=True)
    return unit or suite


if __name__ == "__main__":
    sys.exit(main())
