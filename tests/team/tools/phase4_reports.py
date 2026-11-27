"""Render readable evidence from recorded Phase 4 tool results."""

from collections import Counter
from html import escape
import json
from pathlib import Path
from packaging.version import Version
from playwright.sync_api import sync_playwright


ROOT = Path("tests/team/evidence/phase4").resolve()


def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8-sig"))


def table(headers, rows):
    return ("<table><thead><tr>" + "".join(f"<th>{escape(str(h))}</th>" for h in headers)
            + "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{escape(str(v))}</td>" for v in row)
                                              + "</tr>" for row in rows) + "</tbody></table>")


def report(name, title, sections):
    page = """<!doctype html><meta charset="utf-8"><style>
    body{font:17px system-ui;background:#fff;color:#111;max-width:1320px;margin:44px auto;padding:0 24px}
    table{border-collapse:collapse;width:100%;margin:10px 0 28px}
    th,td{text-align:left;border:1px solid #777;padding:10px;vertical-align:top;overflow-wrap:anywhere}
    </style>"""
    (ROOT / name).write_text(page + f"<title>{escape(title)}</title><h1>{escape(title)}</h1>" + sections,
                             encoding="utf8")


def package_groups(dependency):
    groups = []
    for entry in dependency["vulns"]:
        ids = {entry["id"], *entry["aliases"]}
        joining = [group for group in groups if ids & group["ids"]]
        fixes = set(entry["fix_versions"])
        for group in joining:
            ids.update(group["ids"])
            fixes.update(group["fixes"])
            groups.remove(group)
        groups.append({"ids": ids, "fixes": fixes})
    return groups


def dependency_report():
    data = read("pip-audit.json")["dependencies"]
    audit = read("pip-audit-run.json")
    overview, details = [], []
    for d in data:
        if not d.get("vulns"):
            continue
        groups = package_groups(d)
        fixes = {v for g in groups for v in g["fixes"]}
        overview.append((d["name"], d["version"], len(d["vulns"]), len(groups),
                         max(fixes, key=Version) if fixes else "None listed"))
        details.extend((d["name"], d["version"], ", ".join(sorted(g["ids"])),
                        ", ".join(sorted(g["fixes"], key=Version)) or "None listed") for g in groups)
    summary = dict(packages=len(data), affected=len(overview), records=sum(row[2] for row in overview),
                   alias_groups=len(details), skipped=sum("skip_reason" in d for d in data), exit=audit["exit"])
    (ROOT / "dependency-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf8")
    info = f"<p>{escape(audit['tool'])} via PyPI. {summary['packages']} packages, {summary['records']} returned records, {summary['alias_groups']} advisory groups and exit {audit['exit']}.</p>"
    report("dependency-summary.html", "MediHub Phase 4 | Python dependency audit", info +
           table(("Package", "Installed", "Raw records", "Advisory groups", "Highest listed fix"), overview)
           + "<p>Confirm compatible upgrades and audit the resolved environment again.</p>")
    report("dependency-advisories.html", "MediHub Phase 4 | Advisory IDs and versions", info
           + table(("Package", "Installed", "Advisory IDs including aliases", "Fixed versions in advisory"), details)
           + "<h2>Full audited package list</h2>" + table(("Package", "Version", "Audit skip"),
               ((d["name"], d.get("version", ""), d.get("skip_reason", "")) for d in data)))


def zap_report():
    data = read("zap-alerts.json")
    run = read("zap-run.json")
    alerts = data["alerts"]
    count = Counter((a["pluginId"], a["name"], a["risk"], a["confidence"]) for a in alerts)
    info = (f"<p>OWASP ZAP {escape(data['version'])} passive scan over {escape(data['site'])}. "
            f"{run['messages']} HTTP messages and {data['passive_remaining']} pending records.</p>")
    report("zap-summary.html", "MediHub Phase 4 | ZAP passive scan", info
           + table(("Rule", "Alert", "Risk", "Confidence", "Instances"), ((*k, v) for k, v in count.items())))
    report("zap-alerts.html", "MediHub Phase 4 | ZAP passive alert details", info
           + table(("Rule", "Alert", "Risk", "Confidence", "Route", "Parameter", "Observation", "Correction"),
                   ((a["pluginId"], a["name"], a["risk"], a["confidence"], f"{a['method']} {a['url']}",
                     a.get("param", ""), a.get("description", ""), a.get("solution", "")) for a in alerts)))


def screenshots():
    decisions = [read(f"P4-{n:02}.json") for n in (2, 4)]
    for d in decisions:
        report(f"{d['test']}-response.html", f"MediHub Phase 4 | {d['test']} server decision",
               table(("Account", "Action", "HTTP result", "Server message", "SQLite unchanged"),
                     [(d["account"], f"{d['method']} {d['url']}", d["http_status"],
                       d["response_message"], d["before"] == d["after"])]))
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        for name in ("zap-summary", "zap-alerts", "dependency-summary", "P4-02-response", "P4-04-response"):
            page.goto((ROOT / f"{name}.html").as_uri())
            assert page.locator("table").first.is_visible()
            page.screenshot(path=ROOT / "screenshots" / f"{name}.png", animations="disabled")
        browser.close()


if __name__ == "__main__":
    dependency_report()
    zap_report()
    screenshots()
