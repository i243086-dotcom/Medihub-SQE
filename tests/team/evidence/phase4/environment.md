# Phase 4 execution environment

The Windows assessment ran against the actual Flask/Vue application from the integrated Phase 3 merge `436c9ff1b6d9fd29c717be719ec187ce0b93f37d`, using branch `phase4-security-assessment`.

| Component | Configuration |
|---|---|
| Application | Flask loopback `http://127.0.0.1:5001`. Existing Playwright fixture serves the live browser application and actual APIs. |
| Data | Fresh in-memory SQLite per test, frozen booking date with availability on 2030-01-16, synthetic patients Arjun and Vikram and doctors Ajay and Rajesh. Test JWT secret generated per case. SMTP suppressed and blocked. |
| Development DB | Digest recorded in `integrity.json` and pytest logs. |
| Browser | Python 3.11.9, Playwright 1.65.2, Chromium 159.0.8154.6, 1440×1000. Browser requests to external origins are fulfilled only from the pinned local Vue/Bootstrap cache or aborted. |
| Passive proxy | Portable ZAP 2.17.0 and Temurin Java 21.0.13.1. Proxy and daemon bind to `127.0.0.1:8093`. Disposable ZAP home and session, silent mode, scoped to the actual test app. |
| Dependency audit | pip-audit 2.10.1 from an isolated tool venv. PyPI vulnerability service for the actual app/test environment's installed packages. |

## Reproduction

Install the project's normal test dependencies and Chromium. Cache the pinned Vue and Bootstrap files described in the existing [Phase 3 setup](../phase3/environment.md#run-the-chromium-cases). Download the official portable ZAP release and a patched Java 17+ runtime. Run the following from the repository root with ports 5001 and 8093 available.

```powershell
$env:MEDIHUB_BROWSER_ASSETS = Join-Path $env:TEMP 'medihub-phase1-browser-assets'
.venv/Scripts/python.exe tests/team/tools/phase4_passive.py '<java.exe>' '<zap-2.17.0.jar>' tests/team/evidence/phase4
python -m pip_audit --path .venv/Lib/site-packages --format json --desc off --progress-spinner off --vulnerability-service pypi --output tests/team/evidence/phase4/pip-audit.json
.venv/Scripts/python.exe tests/team/tools/phase4_reports.py
```

Use an independent venv for the pip-audit command, and record its actual exit code and version as in `pip-audit-run.json`. The Python audit inventory includes test tools because they are installed in the inspected environment. Production relevance is assessed against `backend/requirements.txt` and actual imports. The Vue application references pinned frontend CDN scripts and styles directly in `frontend/index.html`. The Git tree contains no frontend package manifest or lockfile for a frontend dependency resolver to audit. Third-party origins were outside the ZAP target.

The browser tests exercise ordinary authenticated actions and role/ownership rejection. The ZAP driver uses only context setup, passive status, reports, and shutdown. Captured URLs, alert metadata and whitelisted header names/values omit tokens and response/request bodies. The ZAP session is temporary.
