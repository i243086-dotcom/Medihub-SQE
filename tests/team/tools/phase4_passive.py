"""Run Chromium through a disposable ZAP daemon and retain passive evidence."""

import argparse
from collections import Counter
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import monotonic, sleep
from urllib.parse import urlsplit

import requests


PROXY = "http://127.0.0.1:8093"
SITE = "http://127.0.0.1:5001"
SECURITY_HEADERS = ("content-security-policy", "x-frame-options", "x-content-type-options",
                    "strict-transport-security", "referrer-policy", "cache-control",
                    "access-control-allow-origin", "access-control-allow-credentials")


def headers(raw):
    return {k.lower(): v.strip() for name in raw.splitlines()[1:] if ":" in name
            for k, v in [name.split(":", 1)]}


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("java", type=Path)
    parser.add_argument("zap", type=Path)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--tested-commit", required=True)
    parser.add_argument("--protected-db", type=Path, default=Path("backend/instance/medihub-database.db"))
    args = parser.parse_args()
    if not re.fullmatch(r"[a-f0-9]{40}", args.tested_commit):
        parser.error("--tested-commit must be a full Git SHA")
    root = args.evidence.resolve()
    (root / "screenshots").mkdir(parents=True, exist_ok=True)
    protected = args.protected_db.resolve(strict=True)
    digest = sha256(protected.read_bytes()).hexdigest()
    write_json(root / "integrity.json", {"development_db_before": digest})
    key = secrets.token_hex(24)
    settings = ["api.addrs.addr.name=127.0.0.1", "api.addrs.addr.regex=false",
                "autoupdate.checkOnStart=false", "autoupdate.downloadNewRelease=false",
                "autoupdate.installAddonUpdates=false", "autoupdate.installScannerRules=false"]
    config = {"proxy": PROXY, "site": SITE, "mode": "protect", "silent": True, "passive_in_scope_only": True,
              "settings": settings, "api_key": "random per run", "active_tools_invoked": []}
    with TemporaryDirectory(prefix="medihub-phase4-zap-") as temp, requests.Session() as api:
        api.trust_env = False
        api.headers.update({"X-ZAP-API-Key": key})
        log = Path(temp) / "daemon.txt"

        def query(path, **params):
            response = api.get(f"{PROXY}/JSON/{path}/", params=params, timeout=12, allow_redirects=False)
            response.raise_for_status()
            return response.json()

        with log.open("wb") as output:
            process = subprocess.Popen([str(args.java.resolve()), "-XX:ActiveProcessorCount=4", "-Xmx768m",
                                        "-jar", str(args.zap.resolve()), "-daemon", "-silent",
                                        "-host", "127.0.0.1", "-port", "8093", "-dir", temp,
                                        "-config", f"api.key={key}", *[item for s in settings for item in ("-config", s)]],
                                       stdout=output, stderr=subprocess.STDOUT)
            try:
                stop = monotonic() + 180
                while True:
                    try:
                        config.update(query("core/view/version"))
                        break
                    except requests.ConnectionError:
                        if process.poll() is not None or monotonic() >= stop:
                            raise RuntimeError("ZAP daemon failed to start")
                        sleep(1)
                query("context/action/newContext", contextName="MediHub loopback")
                query("context/action/includeInContext", contextName="MediHub loopback",
                      regex=r"http://127\.0\.0\.1:5001/.*")
                query("context/action/setContextInScope", contextName="MediHub loopback", booleanInScope="true")
                query("core/action/setMode", mode="protect")
                query("pscan/action/setScanOnlyInScope", onlyInScope="true")
                config["scanners"] = query("pscan/view/scanners")["scanners"]
                write_json(root / "zap-config.json", config)
                env = {**os.environ, "MEDIHUB_PHASE4_PROXY": PROXY, "MEDIHUB_PHASE4_EVIDENCE": str(root)}
                with (root / "playwright.log.txt").open("wb") as execution:
                    result = subprocess.run([sys.executable, "-B", "-X", "utf8", "-m", "pytest", "tests/team/phase4",
                                             "--browser", "chromium", "-q", "-s", "--tb=short",
                                             f"--junitxml={root / 'playwright.xml'}",
                                             f"--html={root / 'playwright.html'}", "--self-contained-html"],
                                            env=env, stdout=execution, stderr=subprocess.STDOUT, check=False)
                # The browser is closed before waiting for the passive queue.
                queue = []
                finish = monotonic() + 120
                while True:
                    queue.append(int(query("pscan/view/recordsToScan")["recordsToScan"]))
                    if queue[-1] == 0:
                        break
                    if monotonic() >= finish:
                        raise RuntimeError("ZAP passive scan did not drain")
                    sleep(1)
                sites = query("core/view/sites")["sites"]
                assert sites == [SITE], sites
                observed = []
                for entry in query("core/view/messages", baseurl=SITE, start=0, count=500)["messages"]:
                    request = entry["requestHeader"]
                    response = entry["responseHeader"]
                    method, path, _ = request.splitlines()[0].split(" ", 2)
                    target = urlsplit(path)
                    assert not target.netloc or target.netloc == "127.0.0.1:5001"
                    path = target.path + (f"?{target.query}" if target.query else "")
                    status = int(response.splitlines()[0].split()[1]) if response else None
                    rq, rs = headers(request), headers(response)
                    observed.append({"id": entry["id"], "method": method, "path": path, "status": status,
                                     "bearer_present": rq.get("authorization", "").startswith("Bearer "),
                                     "cookie_present": "cookie" in rq, "set_cookie": "set-cookie" in rs,
                                     "security_headers": {k: rs[k] for k in SECURITY_HEADERS if k in rs}})
                write_json(root / "zap-observed-requests.json", observed)
                allowed = {(row["method"], row["path"], row["status"]) for row in observed}
                if result.returncode == 0:
                    assert ("POST", "/api/patient/appointments", 200) in allowed
                    assert ("DELETE", "/api/patient/appointments/1", 200) in allowed
                findings = query("alert/view/alerts", baseurl=SITE, start=0, count=500)["alerts"]
                total = int(query("alert/view/numberOfAlerts", baseurl=SITE)["numberOfAlerts"])
                assert len(findings) == total
                # Persist alert metadata, not request bodies or credential/header values.
                fields = ("id", "pluginId", "alertRef", "name", "risk", "confidence", "url", "method",
                          "param", "description", "solution", "reference", "cweid", "wascid", "messageId", "sourceid")
                safe_alerts = [{k: alert[k] for k in fields if k in alert} for alert in findings]
                write_json(root / "zap-alerts.json", {"version": config["version"], "site": SITE,
                           "passive_remaining": queue[-1], "alerts": safe_alerts})
                export_dir = root / "zap-official"
                export_dir.mkdir(exist_ok=True)
                templates = query("reports/view/templates")
                exports = []
                for template, filename in (("risk-confidence-html", "zap-report.html"),
                                           ("traditional-json", "zap-report.json")):
                    params = {"title": "MediHub Phase 4 Passive Assessment", "template": template,
                              "sites": SITE, "contexts": "MediHub loopback", "reportFileName": filename,
                              "reportDir": str(export_dir), "display": "false"}
                    if template == "risk-confidence-html":
                        params["sections"] = ("contents|aboutThisReport|reportDescription|reportParameters|"
                                              "summaries|riskConfidenceCounts|siteRiskCounts|alertTypeCounts|"
                                              "alerts|appendix|alertTypes")
                    generated = query("reports/action/generate", **params)
                    path = export_dir / filename
                    assert path.is_file(), (template, generated)
                    exports.append({"template": template, "filename": filename, "api": "reports/action/generate",
                                    "sections": params.get("sections"), "sha256": sha256(path.read_bytes()).hexdigest()})
                write_json(root / "zap-report-export.json", {"tested_commit": args.tested_commit,
                           "templates": templates, "exports": exports})
                write_json(root / "zap-run.json", {"sites": sites, "messages": len(observed),
                           "queue_observations": queue, "pytest_exit": result.returncode,
                           "alert_count": total, "alerts_by_risk": Counter(a["risk"] for a in safe_alerts)})
            finally:
                if process.poll() is None:
                    try:
                        query("core/action/shutdown")
                    except requests.RequestException:
                        pass
                    try:
                        process.wait(timeout=20)
                    except subprocess.TimeoutExpired:
                        process.terminate()
                        process.wait(timeout=20)
                output.flush()
                daemon = log.read_text(encoding="utf8", errors="replace").replace(key, "[redacted]")
                daemon = re.sub(r"(?:Bearer )[^\s]+", "Bearer [redacted]", daemon)
                (root / "zap-daemon.log.txt").write_text(daemon, encoding="utf8")
                after = sha256(protected.read_bytes()).hexdigest()
                write_json(root / "integrity.json", {"development_db_before": digest, "development_db_after": after})
                assert after == digest
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
