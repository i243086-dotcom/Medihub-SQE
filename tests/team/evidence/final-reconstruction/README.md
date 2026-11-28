# Final reconstruction evidence

Production code matches integrated main `50554b9aefbf514bc4998aed1bedd20441f793f3`. The changes concern tests, fixtures, data generation, evidence and documentation. The historical 227 generated cases and 729 combined passes remain in the previous archives. The seven handwritten minute cases were retired from collection after their exact inputs became generated cases.

| Result | Genuine output |
|---|---|
| 430 unit and 372 API/integration, 802 passed, no failures or skips | [Combined pytest JUnit](functional.xml) · [unit JUnit](unit.xml) |
| 30 Chromium flows passed, no failures or skips | [Native browser JUnit](browser.xml). An [initial setup attempt](browser-initial-setup.xml) collected the 30 flows but could not start without the asset environment variable. The successful rerun used the verified pinned cache. |
| 262 generated cases passed, 256 JSON schema and 6 HTML media-type assertions, 49 semantically asserted successful reads | [Derived per-case matrix with native references](ep-bva-matrix.csv) |
| 720/720 selected statements and 234/234 selected arcs; combined 972/1170 statements and 261/372 arcs | [Native unit JSON](unit-coverage.json) · [Scope calculation](scoped.json) · [Native combined JSON](functional-coverage.json) |
| Two proposed spec changes, 254 matched cases and eight expected policy differences | [Native diagnostic JUnit](proposed-diagnostic.xml) · [Exact differing IDs](summary.json) |
| Real isolated Windows frontend, synthetic sign-in and protected read HTTP 200 | [Startup and SQLite hash check](windows-setup-smoke.json) |
| Original CFG source and recount | [Numbered graph and edges](../phase2/closure/booking-cfg.md) · [Recount](cfg-verification.json) |
| Exact FR → rule → risk → executed ID → result | [Requirements trace](requirements-trace.csv) · [Concrete executable registry](current-execution-registry.csv) |
| Cross-phase, deduplicated findings | [Finding-level register](findings-register.csv) · [Full rubric](../../../../docs/team/FINAL_RUBRIC_AUDIT.md) |
| Full Word pagination and media verification | [Word layout record](word-layout.json) |

## Reproduce on Windows

Use a separate output directory for a new run. Keep the committed native archives. The local run used Python 3.11.9, pytest 9.2.0 and coverage.py 7.17.4. Commands from the repository root:

```powershell
$py = (Resolve-Path '.venv\Scripts\python.exe').Path
$fresh = Join-Path $env:TEMP ('medihub-sqe-recheck-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $fresh | Out-Null
& $py tests/team/tools/generate_appointment_cases.py tests/team/data/appointments.openapi.yaml "$fresh/active.json"
& $py tests/team/tools/generate_appointment_cases.py tests/team/data/appointments.openapi.yaml "$fresh/proposed.json" --overlay tests/team/data/appointments.proposed-v2.yaml
& $py -m pytest -p no:cacheprovider tests/team/unit tests/team/api -q --tb=short -o junit_family=legacy "--junitxml=$fresh/functional.xml" --cov=backend --cov-branch "--cov-report=json:$fresh/coverage.json"
```

The active suite defaults to the committed generated file. Compare the fresh and committed SHA-256 values before or after the test. For the optional proposed-policy demonstration set `MEDIHUB_GENERATED_CASES` to `$fresh/proposed.json`, run only `tests/team/api/test_generated_appointments.py` with a separate JUnit path, then remove that environment variable from the PowerShell session. The nonzero diagnostic exit documents real application/proposal differences. It is outside acceptance.

The existing six quality jobs run on PR #19, including dependency-gated loopback. [PR and exact-revision checks](https://github.com/i243086-dotcom/Medihub-SQE/pull/19/checks). The live PR is the source of truth for analysis of the latest merge checkout. Original security/passive, accessibility and load workloads were not repeated for these test-only changes.

The [first reconstruction CI run](https://github.com/i243086-dotcom/Medihub-SQE/actions/runs/46138086837) passed five gates. Its native Sonar gate passed, while the separate overall Security A criterion failed. The reviewed disposition guard correctly declined to replay the old finding after the shared pinned auth fixture changed. That fixture was restored byte-for-byte. Generated fixture setup now lives in `tests/team/generated_case_support.py`. The gate, application and disposition rules are unchanged. [Native before measures](sonar-fail-before-measures.json) · [Guard disposition](sonar-fail-before-disposition.json) · [Targeted pytest after helper isolation](generated-fixture-isolation.xml).

## Tool provenance

[Current Windows executable paths and environment versions](windows-tools.json).

- In Windows PowerShell use `& .\.venv\Scripts\python.exe -m pip show pytest coverage playwright pytest-playwright pytest-html PyYAML openapi-spec-validator openapi-schema-validator pip-audit` and `& .\.venv\Scripts\python.exe -m playwright --version`. Playwright 1.65.2 and installed Chromium were part of the team environment. [Phase 2 tool inventory](../phase2/verification/tool-versions-release.json).
- The Python Sonar scanner is `.venv\Scripts\pysonar.exe`, with version command `--version`. The protected CI uses SonarQube Community Build 26.11.0.134175 and exact reviewed disposition checks. Use [PR #19 checks](https://github.com/i243086-dotcom/Medihub-SQE/pull/19/checks) or the archived scanner output. The local dashboard requires the existing Sonar service. No locally replayed disposition is inferred.
- Cosmic Ray 8.9.0 executable is `.venv\Scripts\cosmic-ray.exe`. [Native mutation result and operators](../phase2/independent-closure/final-ci/mutation/summary.json).
- Lighthouse 12.8.2, axe-core 4.11.4, Node Playwright and Chrome paths and the original authenticated reports are described in the [Phase 3 native index](../phase3/native/README.md).
- ZAP 2.17.0 and pip-audit 2.10.1 versions, native exports and exact commands are recorded in the [Phase 4 native index](../phase4/native/README.md). No active scan was needed.
- Grafana k6 OSS 2.4.0 is documented at `C:\Program Files\k6\k6.exe`. [Installed binary provenance](../phase5/k6-installation.json). The [Phase 5 index](../phase5/README.md) links the original k6 JSONL, console and HTML exports.

The development database SHA-256 remained `27be0512bd93cfadb49d7819cff68fe6088334b50b1d2f5a9489d488df6554f5`. Historical evidence, the original schedule, and the `baseline-v0` tag are preserved. The Word report contains existing original figures and no pending Phase 2 image placeholders.
