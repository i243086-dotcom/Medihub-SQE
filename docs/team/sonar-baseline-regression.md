# SonarQube baseline disposition regression

PR #16 head `66d5a05116250b93cb37d012edcc8782faf18d86` failed the SonarQube check in run [45997392409](https://github.com/i243086-dotcom/Medihub-SQE/actions/runs/45997392409). GitHub's tested merge revision was `65830cdd02f0906138847b9396fa4e51ae03a0b8`. The base scan analyzed `436c9ff1b6d9fd29c717be719ec187ce0b93f37d`.

The failing job logged `Reviewed Sonar disposition: skipped Base application differs from the originally reviewed source`. The scanner completed, source inventory and coverage checks passed, and the native gate reported OK with zero new violations. The separate repository gate failed Security A because the disposable server still had the exact inherited `python:S4502` finding open at `backend/app.py:15`. The loopback deployment job was skipped. [Failed Sonar job](https://github.com/i243086-dotcom/Medihub-SQE/actions/runs/45997392409/job/140500111711)

In passing PR #13, the base was still the Phase 2 tree `0b15192`, the approved disposition replayed, and Security A passed. PR #13 also separately corrected `javascript:S8786` in booking guidance. The PR #16 artifact reported zero new issues and no recurrence of that regex finding. [Prior passing Sonar job](https://github.com/i243086-dotcom/Medihub-SQE/actions/runs/45987360108/job/140466290507)

The earlier guard pinned the base to the original reviewed Phase 2 source even after the known Phase 3 presentation changes became main. The corrected guard requires both the scanned base and merge checkout to match an ancestral approved source snapshot across the entire scoped application, scanner configuration and authentication test inputs. The second approved snapshot already existed in the decision record. It differs from the original only in the checked booking UI and stylesheet. Any changed protected source outside those exact snapshots requires a fresh reviewed disposition.

The exact rule, file, line, issue hash, signed-in local disposition history, two original PR #11 approval IDs and comment hashes, repository identity and disposable loopback server guards remain mandatory. No quality thresholds, production analysis scope, required checks or approval rules changed.

Local validation matched the original Phase 2 base, the integrated Phase 3 main and Phase 4 head. It rejected the original upstream tag and the pre-correction Phase 3 source. All 26 transport regression tests passed. CI execution and live disposition evidence are recorded in the linked correction PR checks.
