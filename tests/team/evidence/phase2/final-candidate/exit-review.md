# Phase 2 remediation exit assessment

The earlier RCA and Pareto remain the evidence for the discovery phase. The final build verifies the corrections before merge and before any rollout migration.

| ID | Final status | Final evidence |
|---|---|---|
| #5 | High, fix verified on candidate | Book, cancel and rebook each returned 200. The same slot had two distinct rows, one historical cancelled and one active booked. |
| #12 | High, fix verified on candidate | Five repeats per conflict type. Each pair returned 200 and 400, persisted one booked row, and produced no 500. A patient cannot book two active rows at the same stored date and start. |
| #7–#10 | Medium, fix verified on candidate | Unknown status rejected from all five source states. Malformed time, numeric time and null requests returned 400 without writes. |
| #6 | Characterized, team disposition pending | Assigned doctor can reopen a free cancelled slot. A conflicting reopen gets 400 and rolls back. The old terminal-state oracle remains historical evidence. |

The migration was tested on two isolated scenarios. A read-only SQLite backup of the development schema migrated successfully and passed integrity and foreign-key checks. Synthetic legacy fixtures verified actual history and treatment retention, both post-upgrade uniqueness constraints, idempotency and rollback with seeded existing conflicts. Rollout requires team approval, a backup and confirmation that existing active rows do not conflict. The development database was preserved.

| Exit criterion | Candidate result |
|---|---|
| EC-01 Critical integrity | Met on the candidate. Rollout migration pending. |
| EC-02 Role and ownership | Met for the assigned scope. |
| EC-03 White-box and documented decisions | Met for appointment scope and existing actor contract. |
| EC-04 Active generated contract | Met. All 205 active generated cases passed. |
| EC-05 PR quality | Unmet. Sonar overall security and genuine teammate review remain pending. |

**HOLD**. Real team ownership and actual effort totals remain outstanding. A stronger doctor reopening or interval overlap rule needs an explicit policy. The current MIS stores start times and no duration. An automated deployment gate could not be demonstrated because the repository has no deployment target.
