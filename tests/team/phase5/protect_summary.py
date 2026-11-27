"""Make a shareable copy of k6's legacy summary while keeping its original private."""

import argparse
import json
from pathlib import Path
import re
import shutil


JWT = re.compile(r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")


def publish_summary(source, destination):
    original = json.loads(source.read_text(encoding="utf-8"))
    # k6's --summary-export retains the setup() return value, which includes
    # short-lived synthetic bearer tokens and is unrelated to the metrics.
    if "setup_data" in original:
        original["setup_data"] = "[REDACTED: disposable session credentials]"
    content = json.dumps(original, indent=2) + "\n"
    if JWT.search(content):
        raise ValueError("Potential bearer token in the shareable summary")
    destination.write_text(content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("private", type=Path)
    args = parser.parse_args()
    args.private.mkdir(parents=True, exist_ok=True)
    private_original = args.private / (args.run.name + "-summary.json")
    if private_original.exists():
        raise FileExistsError(private_original)
    shutil.move(args.run / "summary.json", private_original)
    publish_summary(private_original, args.run / "summary.redacted.json")


if __name__ == "__main__":
    main()
