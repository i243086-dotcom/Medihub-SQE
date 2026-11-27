"""Attach original AxeBuilder results to the corresponding pytest HTML case."""

import json
import os
from pathlib import Path

import pytest


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    audit_dir = os.environ.get("MEDIHUB_PHASE3_ATTACHMENTS")
    if not audit_dir or call.when != "call":
        return
    from pytest_html import extras

    screen = "booking" if "booking" in item.name else "cancellation"
    path = Path(audit_dir) / f"axe-{screen}.json"
    report.extras = [*getattr(report, "extras", []),
                     extras.json(json.loads(path.read_text(encoding="utf8")),
                                 name=f"Original AxeBuilder results ({screen} audit)")]
