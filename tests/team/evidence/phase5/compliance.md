# Phase 5 compliance

The official assignment's Section 5 is on page 5 of `docs/team/_codex_inputs/SQE_Final_Project Fall 2026(6).pdf`. Each status is scoped to the localhost experiment and the injected pre-commit fault.

| Requirement | Status | Evidence |
| --- | --- | --- |
| Select a real operation relevant to booking or cancellation | PASS | [Availability route, Vue caller and contract](targets.md) |
| Define and justify p95 and unexpected failure limits before execution | PASS | [Predeclared limits](targets.json) in commit `fc61465aebac79dc43b24690d5a8211d01a6e804), [rationale](targets.md) |
| Run genuine Grafana k6 OSS with one repeatable workload script | PASS | [Signed Windows MSI evidence and executable](k6-installation.json), [workload](../../phase5/availability.js) |
| Run two independent one-user trials | PASS | [L01](runs/P5-L01/run.json), [L02](runs/P5-L02/run.json) |
| Run two independent trials at five or more concurrent users | PASS | [L03](runs/P5-L03/run.json), [L04](runs/P5-L04/run.json) |
| Measure at least 60 seconds after attaining each target | PASS | [Tagged steady-state request counts and duration](results.json), [raw metric index](README.md#final-matched-series) |
| Hold application build, machine, server and starting data constant | PASS | [Environment](environment.md), [fixture integrity and development DB verification](runs/database-safety.json), four [run records](README.md#final-matched-series) |
| Report p95 milliseconds, operation requests/s and unexpected failure percentage for each run | PASS | [Comparison and target evaluation](results.md), [native summaries and streams](README.md#final-matched-series) |
| Verify HTTP contract, status counts, failed checks and threshold results | PASS | [Per-run derived evidence](results.json), [native terminal outputs](README.md#final-matched-series) |
| Trigger a controlled dependency failure before booking persistence completes | PASS | [Executed recovery test](../../api/test_phase5_booking_recovery.py), [prepared but uncommitted row and HTTP failure](recovery/state.json), [JUnit](recovery/junit.xml) |
| Verify no partial SQLite state persists after failure | PASS | [Before and after failure SQLite states](recovery/state.json) |
| Restore dependency, retry successfully and verify one valid final appointment | PASS | [Same request, successful retry, rejected duplicate and final readback](recovery/state.json), [native pytest report](recovery/pytest.html) |
| Save native outputs, run environment, reproduction commands and dashboard exports | PASS | [Evidence and commands](README.md), [environment](environment.md). Unmodified summaries are retained locally. Committed copies redact the synthetic login tokens. |
| Supply genuine full screenshots and accurate cumulative report | PASS | [Dashboard, terminal and pytest PNGs](screenshots/), [rendered Word layout verification](word-layout.json), [continuous Word report](../../../../docs/team/MediHub_SQE_Continuous_Report_Verified.docx) |

The interrupted initial setup attempt is preserved separately. The final matched series applies the original thresholds and includes independent results for all four trials. [Attempt history](README.md#initial-series-and-retry)
