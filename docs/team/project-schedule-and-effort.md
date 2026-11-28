# Project schedule, ownership and reported effort

The team supplied these approximate allocations. They are not independently verified timesheets, and they do not prove who authored particular commits or tests. The timeline uses PKT. Registration was reported on 22 November. An independent registration receipt was not available. Native files retain their original timestamps, including the k6 executions on 27 November; the 28 November row represents the team-reported Phase 5 allocation and audit activity.

## Timeline and date-wise effort

| Date | Activity | Status | Ayaan | Shaheer | Momin | Total |
|---|---|---|---|---|---|---|
| 2026-11-22 | Repository selection, initial setup and registration-sheet completion | Team-reported completed | 2 | 2 | 2 | 6 |
| 2026-11-23 | Phase 1 | Team-reported completed | 5 | 5 | 5 | 15 |
| 2026-11-24 | Phase 2 | Team-reported completed | 8 | 7 | 6 | 21 |
| 2026-11-25 | Phase 2 continuation | Team-reported completed | 8 | 8 | 6 | 22 |
| 2026-11-26 | Phase 2 completion and verification | Team-reported completed | 7 | 8 | 6 | 21 |
| 2026-11-27 | Phases 3 and 4 | Team-reported completed | 8 | 7 | 9 | 24 |
| 2026-11-28 | Phase 5, final review and audit | Team-reported completed | 10 | 11 | 14 | 35 |
| 2026-11-29 | Final checks, README and ZIP verification, submission readiness | PLANNED | 2 | 2 | 2 | 6 |
| Total | Allocation through 29 November | Projected | 50 | 50 | 50 | 150 |

The four-column [time log](../../tests/team/evidence/time_log.csv) has exactly 24 member/date entries. The three entries dated 2026-11-29 are planned only. The 22–28 November entries total approximately 48 hours per person, or 144 combined. Planned 29 November effort is 2 hours per person, or 6 combined.

## Primary responsibilities

| Member | Primary area | Agreed use cases |
|---|---|---|
| Ayaan | Static analysis, CFG, white-box, MCC, MC/DC, mutation/custom operators and CI | UC01–UC02 |
| Shaheer | API testing/integration, OpenAPI, test-data generation, EP and BVA | UC03–UC04 |
| Momin | Use cases, browser automation, usability, accessibility, defensive security and performance | UC05–UC06 |

All members support selection, setup, coordination, test management, review and submission preparation. Primary technical ownership and use-case ownership are separate records.

## Task-based view of the same allocation

| Task | Ayaan | Shaheer | Momin | Total |
|---|---|---|---|---|
| Repository selection, setup and registration | 2 | 2 | 2 | 6 |
| Static analysis and CFG | 10 | 1 | 1 | 12 |
| White-box testing and test design | 8 | 2 | 1 | 11 |
| Mutation testing and custom operators | 7 | 1 | 1 | 9 |
| CI configuration and quality gates | 6 | 2 | 1 | 9 |
| API testing and test-data generation | 2 | 14 | 2 | 18 |
| Use-case development and testing | 2 | 2 | 10 | 14 |
| Usability, accessibility, security and performance | 1 | 1 | 10 | 12 |
| Cross-phase integration, defect review and verification | 7 | 15 | 12 | 34 |
| Documentation, audit and submission preparation | 3 | 8 | 8 | 19 |
| Final checks and submission readiness | 2 | 2 | 2 | 6 |
| Allocation total | 50 | 50 | 50 | 150 |

The task and date tables are two views of the same hours. The final-readiness task is planned. Do not add the two tables together. [Editable task allocation](../../tests/team/evidence/phase2/release-gate/effort-plan.csv)

## Three-point comparison

PERT E = (O + 4M + P) / 6. Original estimates are retained. Expected totals use unrounded inputs.

| Area | O | M | P | E hours |
|---|---|---|---|---|
| Static analysis and CFG | 6 | 10 | 15 | 10.17 |
| Unit testing, MCC and MC/DC | 12 | 24 | 40 | 24.67 |
| API and OpenAPI generator | 12 | 22 | 36 | 22.67 |
| Playwright use cases | 10 | 20 | 32 | 20.33 |
| Mutation and custom operators | 10 | 18 | 32 | 19.00 |
| GitHub CI gates and PRs | 8 | 14 | 24 | 14.67 |
| Management, defects and monitoring | 10 | 18 | 28 | 18.33 |
| Original seven areas | 68 | 126 | 207 | 129.83 |
| Usability, accessibility, security and performance | 14 | 26 | 42 | 26.67 |
| Extended eight areas | 82 | 152 | 249 | 156.50 |

Projected allocation through 29 November is 150 hours. Projected difference versus the extended estimate is 150 − 156.50 = **−6.50 hours**. The 144 hours through 28 November are team-reported approximate completed effort; the additional 6 hours are planned. Neither this projection nor the task breakdown supplies independently verified per-area actuals or a final actual variance.
