# Phase 3 usability and accessibility evidence

The two cases exercise the real Vue patient dashboard served by Flask at `http://127.0.0.1:5001/`. The SPA uses the same URL for both authenticated panels. `context-*.json` records the selected panel, visible login-state check, viewport and tool versions for each audit.

## Executed evidence

| Evidence | Original application | Corrected application |
|---|---|---|
| Booking and cancellation Playwright report | [HTML](before/playwright.html) · [JUnit](before/playwright.xml) · [Log](before/playwright.log.txt) | [HTML](after/playwright.html) · [JUnit](after/playwright.xml) · [Log](after/playwright.log.txt) |
| Booking Lighthouse | [HTML](before/lighthouse-booking.html) · [JSON](before/lighthouse-booking.json) · [Screenshot](screenshots/before/lighthouse-booking.png) | [HTML](after/lighthouse-booking.html) · [JSON](after/lighthouse-booking.json) · [Screenshot](screenshots/after/lighthouse-booking.png) |
| Cancellation Lighthouse | [HTML](before/lighthouse-cancellation.html) · [JSON](before/lighthouse-cancellation.json) · [Screenshot](screenshots/before/lighthouse-cancellation.png) | [HTML](after/lighthouse-cancellation.html) · [JSON](after/lighthouse-cancellation.json) · [Screenshot](screenshots/after/lighthouse-cancellation.png) |
| Booking axe-core | [HTML](before/axe-booking.html) · [JSON](before/axe-booking.json) · [Screenshot](screenshots/before/axe-booking.png) | [HTML](after/axe-booking.html) · [JSON](after/axe-booking.json) · [Screenshot](screenshots/after/axe-booking.png) |
| Cancellation axe-core | [HTML](before/axe-cancellation.html) · [JSON](before/axe-cancellation.json) · [Screenshot](screenshots/before/axe-cancellation.png) | [HTML](after/axe-cancellation.html) · [JSON](after/axe-cancellation.json) · [Screenshot](screenshots/after/axe-cancellation.png) |
| Verified active audit panels | [Booking](before/context-booking.json) · [Cancellation](before/context-cancellation.json) · [Audit log](before/audit.log.txt) | [Booking](after/context-booking.json) · [Cancellation](after/context-cancellation.json) · [Audit log](after/audit.log.txt) |
| Matching booking screen captures | [Original](screenshots/before/booking-audited.png) | [Corrected](screenshots/after/booking-audited.png) |
| Matching cancellation screen captures | [Original](screenshots/before/cancellation-audited.png) | [Rerun](screenshots/after/cancellation-audited.png) |
| Original booking form and workflow evidence | [Form](screenshots/before/booking-form.png) · [Rejection](screenshots/before/booking-rejection.png) · [Success](screenshots/before/booking-success.png) | [Form](screenshots/after/booking-form.png) · [Rejection](screenshots/after/booking-rejection.png) · [Success](screenshots/after/booking-success.png) |
| Keyboard focus | [Date](screenshots/before/booking-keyboard-focus.png) | [Specialty](screenshots/after/booking-specialty-focus.png) · [Date](screenshots/after/booking-keyboard-focus.png) |
| Cancellation evidence | [Active](screenshots/before/cancellation-active.png) · [Confirmation](screenshots/before/cancellation-success.png) | [Active](screenshots/after/cancellation-active.png) · [Confirmation](screenshots/after/cancellation-success.png) |
| Unified element-level findings | [Baseline register](before/findings.md) · [Data](before/findings.json) | [Unified register](findings.md) · [Data and comparison](findings.json) |
| Existing Chromium use-case regression | | [JUnit](after/booking-cancellation-regression.xml) · [Log](after/booking-cancellation-regression.log.txt) |

HTML reports are self-contained. Open the downloaded HTML in Chrome for the interactive report. The axe-core HTML lists all violated rules and affected elements. Selectors, human impact and corrections are in the unified register.

## Measured comparison

| Authenticated screen | Accessibility | Best Practices | SEO | Axe affected rule-element pairs | Deduplicated tool findings |
|---|---:|---:|---:|---:|---:|
| Booking before | 85 | 100 | 60 | 17 | 19 |
| Booking after | 91 | 100 | 60 | 9 | 11 |
| Cancellation before | 89 | 100 | 60 | 10 | 12 |
| Cancellation after | 89 | 100 | 60 | 10 | 12 |

On the original booking form, specialty and doctor selection required a pointer. The date, time, notes and submit controls were already reachable by keyboard. The corrected run verified that native specialty and doctor buttons entered the keyboard sequence, visible focus reached the date, Space selected a time and Enter submitted. The new conflict message explicitly instructs the patient to choose another time. Both workflows passed in each run. The separate regression suite passed all 30 existing Chromium flows.

## Code and reproducibility

- [Booking test](../../phase3/test_phase3_booking.py), [cancellation test](../../phase3/test_phase3_cancellation.py), [application fixture](../../e2e/test_appointment_flows.py), [synthetic records](../../phase2_support.py).
- [Audit server](../../tools/phase3_audit_server.py), [Lighthouse and axe runner](../../tools/phase3_audits.mjs), [register generator](../../tools/phase3_findings.py).
- [Corrected booking view](../../../../frontend/js/patient.js) and [scoped focus styles](../../../../frontend/custom.css).
- [Environment and integrity](environment.md) records the source identities, tools, reproduction commands and protected database readback.
- [Assignment checklist](../../../../docs/team/phase3-compliance.md) and [continuous Word report](../../../../docs/team/MediHub_SQE_Continuous_Report_Verified.docx).
