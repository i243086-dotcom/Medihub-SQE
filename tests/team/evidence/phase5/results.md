# Phase 5 performance results

This derived analysis uses the native k6 summary percentiles, native request counts and tagged check points. The unchanged decision thresholds were committed before all measurements. The official dashboard shows whole-run totals including authentication and warm-up. The table uses only the steady operation.

| Trial | VUs | Common marker span, s | Completed | p95, ms | Completed req/s | Unexpected | HTTP status counts | Failed checks | Latency / failure gates | Exit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | --- | ---: |
| P5-L01 | 1 | 65.143 | 234 | 44.67 | 3.60 | 0/234 (0.00%) | 200: 234 | 0 | PASS / PASS | 0 |
| P5-L02 | 1 | 65.057 | 230 | 55.04 | 3.54 | 0/230 (0.00%) | 200: 230 | 0 | PASS / PASS | 0 |
| P5-L03 | 5 | 64.798 | 1123 | 100.50 | 17.28 | 0/1123 (0.00%) | 200: 1123 | 0 | PASS / PASS | 0 |
| P5-L04 | 5 | 64.836 | 1093 | 118.38 | 16.82 | 0/1093 (0.00%) | 200: 1093 | 0 | PASS / PASS | 0 |

Rates divide the number of completed measured operation requests by the fixed 65-second start window. A request is measured if it starts inside the window and reports a completion. The tail lets those requests finish. Each user emits one entry and one exit marker from its running iteration. The common span is earliest exit minus latest entry. Each marker can lag its boundary by one paced iteration, which explains small differences on either side of 65 seconds. All spans imply at least 60 seconds at the target VU level. Five setup logins and any warm-up samples are outside the scored totals.

| Trial | Start PKT | End PKT | Average, ms | Median, ms | p99, ms | Maximum, ms | HTTP errors |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| P5-L01 | 21:09:49.915 | 21:11:14.815 | 25.58 | 23.12 | 59.44 | 66.50 | 0 |
| P5-L02 | 21:11:18.646 | 21:12:43.012 | 29.63 | 25.55 | 85.20 | 109.01 | 0 |
| P5-L03 | 21:12:47.380 | 21:14:12.076 | 36.29 | 26.22 | 147.01 | 178.54 | 0 |
| P5-L04 | 21:14:15.909 | 21:15:40.051 | 44.03 | 32.56 | 154.33 | 199.91 | 0 |

All runs took place on November 27, 2026 PKT. UTC timestamps and complete commands are in each run record.

- At one user the repeat differed by 10.37 ms p95 and 0.06 completed requests/s.
- At five users the repeat differed by 17.88 ms p95 and 0.46 completed requests/s.
- The five-user average throughput was 4.78 times the one-user average. Five-user p95 values were 100.50?118.38 ms versus 44.67?55.04 ms for one user.
- Unexpected failures totaled 0 of 2,680 measured requests. HTTP errors and response-check failures are recorded separately.

The closed workload pauses briefly after each request. Shared CPU, thread scheduling and local SQLite reads are plausible contributors to the observed spread. These trials do not estimate production capacity or establish a saturation point.

The earlier cold series contains a setup login timeout and a prevented launch. Both are archived separately. See [native output and retries](README.md).
