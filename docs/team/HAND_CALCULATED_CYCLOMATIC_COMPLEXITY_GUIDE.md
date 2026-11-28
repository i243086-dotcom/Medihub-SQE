# Hand-calculated booking complexity

## Start with a small example

Draw four boxes for entry, an `if` condition, an action, and a shared exit. Draw entry → condition, true → action, action → exit, and false → exit. With four nodes, four directed edges and one connected component, the calculation is `4 − 4 + 2 = 2`. Count one independent choice plus the initial path. If a return exists on each side, draw both returns and join them to the same exit. Splitting a straight-line box adds one node and one edge and leaves the result unchanged.

## Draw MediHub by hand

Open [book_appointment, lines 213–339](../../backend/routes/patient.py#L213) beside the [source-linked numbered graph](../../tests/team/evidence/phase2/closure/booking-cfg.md). The graph contains all node labels and all 91 numbered edge labels. Draw its intake/validation, time-and-capacity, and persistence sections on three areas of the page. Keep a single return sink. Number the entry 1 and exit 2. The historical graph enumerates the other nodes backwards from the last return, so trace edges forward rather than assuming numbering is execution order.

1. Start at node 1. Follow the patient lookup, profile/blacklist guards, JSON-object check and required-field guards. Each reject return leads to node 2.
2. Draw doctor ID coercion and its handler, then domain bounds and doctor lookup. Draw the date parse and its handler, then the past-date rejection.
3. Draw the start-time type and parse guards, notes validation, hour-band branches and the nested same-day cutoff. At the evening branch, trace the incoming false edge from the morning check. Both successful bands lead toward the date/cutoff decision.
4. Draw availability, doctor conflict, patient conflict and commit branches. Every failure and the successful response join node 2. A handled-exception path is counted once per local handler. Framework decorators and uncaught runtime failures are outside this graph convention.
5. Tick each edge once in the complete graph. Count `N = 69`, `E = 91`, `P = 1`. The hand result is **91 − 69 + 2 = 24**. Independently count every extra successor beyond the single straight-line successor. There are **23** nodes with two successors, 45 with one and one sink. The tally gives `23×2 + 45 = 91`, and `1 + 23 = 24`.

## Explain the differences in the viva

- Under the statement-level convention, a compound predicate is one decision. Expand short-circuiting in the ID guard, the active doctor guard, the notes guard and both chained time inequalities. This gives five extra decisions, five more nodes and ten more edges, so `101 − 74 + 2 = 29`.
- Expand the inline range-prefix conditional at line 269 as a separate choice to reach 30. Radon 6.0.1 measures the function at **30** using its Python AST rules. The adjusted result matches Radon under the illustrated convention.
- The saved native SonarQube analysis shows **82** for the entire patient route file, including its other functions, and gives a different project total. The project API used by the workflow returns the file metric. There is no verified function-level Sonar result in these artifacts. Do not compare 82 with 24 as measurements of the same object.

[Independent edge and source verification](../../tests/team/evidence/final-reconstruction/cfg-verification.json) · [Saved Radon output](../../tests/team/evidence/phase2/independent-closure/radon-patient.json) · [Sonar file measures](../../tests/team/evidence/phase2/independent-closure/final-ci/sonar/evidence/sonar-measures.json)
