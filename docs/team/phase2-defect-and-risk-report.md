# Phase 2 defect, risk and completion review

## Confirmed defects

| GitHub issue | Severity / priority | Phase 2 observations and disposition |
|---|---|---|
| [#5](https://github.com/i243086-dotcom/Medihub-SQE/issues/5) Rebook cancelled slot | High/high | Stage D and the current suite reproduce HTTP 500 and one unchanged cancelled row. Open, remediation pending. |
| [#6](https://github.com/i243086-dotcom/Medihub-SQE/issues/6) Doctor reopening | Medium/medium, triaged | Observed and preserved. The immutable-cancellation assertion remains a failing provisional oracle. A doctor transition policy is required before that assertion can become an agreed requirement. |
| [#7](https://github.com/i243086-dotcom/Medihub-SQE/issues/7) Arbitrary admin status | Medium/medium | Fix candidate rejects unknown labels before assigning or flushing updates. Tests cover rejection from booked, cancelled and completed. Existing recognized historical labels still work. |
| [#8](https://github.com/i243086-dotcom/Medihub-SQE/issues/8), [#9](https://github.com/i243086-dotcom/Medihub-SQE/issues/9), [#10](https://github.com/i243086-dotcom/Medihub-SQE/issues/10) malformed time and JSON | Medium/medium | Fix candidate produces controlled HTTP 400 and leaves rows unchanged. The focused GitHub check changed from 3 FAIL / 1 PASS to 4 PASS. |
| [#12](https://github.com/i243086-dotcom/Medihub-SQE/issues/12) concurrent booking | High/high | Same patient and different doctors produced two booked rows from two 200 responses. Same doctor and different patients produced one row, one 200 and one 500. Open, remediation pending. |

Fix candidates are in the unmerged [PR #11](https://github.com/i243086-dotcom/Medihub-SQE/pull/11). Current retesting does not imply a merged fix or closed issue. Proposed exact-hour, past-slot display and doctor reopening policies are excluded from confirmed-defect totals.

### RCA 1 · Cancelled slot cannot be rebooked (#5)

| Why | Evidence-based answer |
|---|---|
| 1. Why does the patient see an error? | The second booking returns 500 after the cancel succeeded. The original row remains cancelled. |
| 2. Why does the second insert fail? | SQLite rejects a duplicate doctor/date/time key. |
| 3. Why is the cancelled row a duplicate? | The model uniqueness constraint treats cancelled and booked rows the same. |
| 4. Why did the available slot reach that insert? | The slot display and booking pre-check count only rows whose status is booked. |
| 5. Why was the disagreement shipped in the baseline? | The baseline had no executable book→cancel→rebook regression that checks both the visible availability and final row history. The first retained regression appears in Stage D. |

| Fishbone category | Observed contributing cause |
|---|---|
| Code | Availability and persistence use different predicates for the same slot. |
| Data | Keeping the cancelled row preserves history and reserves the all-status unique key. |
| Method | A sequential happy-path booking or cancellation alone cannot expose the mismatch. |
| Environment | SQLite applies the constraint during commit. Disposable SQLite confirmed the same boundary. |
| Test basis | A-01 says the slot becomes bookable. The existing schema enforces a different rule. |

Corrective action is to align uniqueness and allocation with the agreed active-state policy and preserve historical rows. Validate migration against a disposable copy with old and conflicting data before touching any developer or shared database. Prevent recurrence by requiring the book→cancel→rebook regression with source/readback assertions. Current regression `test_d1_book_cancel_rebook_same_slot` remains red. Fix and post-migration retest are pending.

### RCA 2 · Concurrent booking conflicts (#12)

| Why | Evidence-based answer |
|---|---|
| 1. Why are two incompatible bookings stored? | Two normal requests for one patient and one time with different doctors each returned 200 and committed a row. |
| 2. Why did neither request reject? | Both reached the point after the conflict lookup before inserting. Each saw the initial free state. |
| 3. Why did the database allow both writes? | They use different doctor keys. There is no corresponding uniqueness constraint for the patient/time invariant. |
| 4. Why does the other concurrent scenario behave differently? | The same doctor key protects the row count, but the losing request reaches an unhandled uniqueness exception and returns 500. |
| 5. Why was the timing gap absent from earlier evidence? | The original Stage D repeat submission was sequential and did not coordinate simultaneous lookups and writes. |

| Fishbone category | Observed contributing cause |
|---|---|
| Code | Separate conflict lookups and persistence admit a check-then-write gap. |
| Data | Doctor-slot uniqueness enforces one invariant. The patient-time invariant lacks a database constraint. |
| Method | Sequential negative tests observe only the case with an already committed row. |
| Environment | Separate requests use independent transactions on a shared disposable SQLite file. |
| Test basis | FR-05 concerns committed state across all requests. Both response and row count need assertions. |

Corrective action is to enforce both invariants atomically across concurrent writers, handle conflicts as a controlled HTTP rejection, and plan existing-row reconciliation before migration. Prevent recurrence by keeping the two concurrency cases in the required API check. Both current cases remain red. The JUnit records contain actual HTTP outcomes and persisted rows. No fix or safe migration approval was recorded in this run.

## Pareto and monitoring

Confirmed issue population is #5, #7, #8, #9, #10 and #12. Each issue contributes once by its GitHub primary category.

| Category | Count | Fraction | Cumulative |
|---|---:|---:|---:|
| Validation | 4 | 66.7% | 66.7% |
| State integrity | 2 | 33.3% | 100.0% |

Week of 23 November 2026. Audit data and actual technical results were produced for static analysis, white-box, generated API, UI, mutation and Actions. Control actions were to add guarded CI on main, refine assertions after mutation, retest the validation corrections, and retain release HOLD on the integrity issues. Effort reports are still incomplete. The only logged person-hours are 1.5 for setup. The planning forecasts remain 129.8 for Section 2 and 156.5 for the wider project.

| GQM measure | Actual denominator and result |
|---|---|
| Scoped requirement acceptance | 8/10 original FRs met their scoped oracle (80%). FR-03 has the open cancelled-slot outcome and FR-05 has the two concurrent cases. Proposed FR-11/12 and open policies are tracked separately. |
| Confirmed defect density | 6 confirmed issues / 1.011 scoped KLOC = **5.93 issues/KLOC**. Count includes nonblank/noncomment source lines from the same function/model/decorator inventory as scoped coverage. |
| Reopen rate | N/A. No resolved issue was observed. |
| Test execution | 556 passed and 4 failed across 560 executable cases on `9126fef`. The four are two integrity failures under #12, rebooking under #5, and the provisional oracle under #6. |

## Residual risk assessment and exit control

Likelihood and impact below are proposed team-review scores for planning. They use the actual evidence where available and are not measured probabilities.

| Risk | Residual L×I | Rationale / control |
|---|---:|---|
| R01 Cancelled-slot rebooking | 4×5 = 20 | #5 reproduced. Hold until preserving both history and active capacity is proven. |
| R02 Double booking | 4×5 = 20 | Concurrent patient conflict reproduced. Require persisted-state concurrency regression. |
| R03 Authorization/ownership | 2×5 = 10 | Scoped checks passed. Defensive security assessment remains a later phase. |
| R04 Boundaries/timezone | 3×4 = 12 | IST cutoff and hours reproduced. Exact-hour and past-slot policies remain pending. |
| R05 Doctor/date availability | 2×4 = 8 | Discovery, period updates and seeded horizon exercised. Production calendar policy remains a separate decision. |
| R06 State transitions | 3×4 = 12 | Invalid labels rejected in the fix candidate. Valid doctor reopening policy needs team sign-off. |
| R07 Blacklist | 1×4 = 4 | Eligible and blacklisted patient pairs plus the admin toggle executed. |
| R08 Malformed values | 2×3 = 6 | Controlled booking errors and spec-driven cases passed on the updated build. Continue regression with representative invalid inputs. |
| R09 Consistency/recovery | 3×5 = 15 | Simulated availability commit failure rolled back. Full performance/recovery phase remains outstanding. |
| R10 Security/configuration | 4×5 = 20 | Sonar overall security rating remains below the release threshold. Phase 4 was outside this run. |
| P01 CI/Sonar service | 2×4 = 8 | Local server and isolated runner scans executed. Required quality thresholds remain unmet. |
| P02 Isolation/team review | 3×4 = 12 | Protected data hashes match. Real reviewer sign-off and complete effort records remain pending. |

| Exit criterion | Actual versus target |
|---|---|
| EC-01 Critical integrity | **Unmet.** #5 and #12 reproduced on exact test rows. |
| EC-02 Ownership and role | **Met for scoped Phase 2 assertions.** Patient-role and assigned-record checks and MCC blacklist cases passed. |
| EC-03 White-box and agreed policy | **Unmet overall.** 703/703 statements, 226/226 branch arcs, all 64 MCC cases and six MC/DC pairs passed for the measured scope. Policy acceptance for recognized doctor/admin transitions remains pending. |
| EC-04 Generated invalid input | **Met for the active spec.** All 196 active generated cases passed, including 4xx handling and unchanged-row readback for rejected writes. |
| EC-05 PR quality | **Unmet.** Required checks remain red and teammate approvals are pending. |

**Release decision: HOLD.** The user must decide unresolved policy and have genuine teammate review. Integrity remediation needs an agreed migration path and post-fix retest. Maintain the Phase 2 gate on every PR.
