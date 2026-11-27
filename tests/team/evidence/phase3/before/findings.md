# Phase 3 unified issue register

One row per screen, rule and affected element. Lighthouse DOM paths and axe selectors are retained in the JSON register. SEO checks are counted per screen and have no axe severity.

| ID | Screen | Rule and element | Source | Impact / priority | Cause and user impact | Proposed correction | Status / risk |
|---|---|---|---|---|---|---|---|
| P3-01 | booking | button-name `.alert-success > .btn-close[type="button"]` | axe-core, Lighthouse | critical / High | The icon-only close button lacks an accessible name. Screen readers cannot identify the dismiss button. | Give the dismiss button an accessible name. | Baseline / P3-R01 |
| P3-02 | booking | color-contrast `.alert-success` | axe-core, Lighthouse | serious / High | The rendered text and background colors produce insufficient contrast. Text can be difficult to read for people with low vision. | Increase text contrast against its actual background. | Baseline / P3-R01 |
| P3-03 | booking | color-contrast `.btn-outline-secondary.btn-sm.btn:nth-child(3) > div:nth-child(2)` | axe-core, Lighthouse | serious / High | The rendered text and background colors produce insufficient contrast. Text can be difficult to read for people with low vision. | Increase text contrast against its actual background. | Baseline / P3-R01 |
| P3-04 | booking | color-contrast `.btn-outline-secondary.btn-sm.btn:nth-child(4) > div:nth-child(2)` | axe-core, Lighthouse | serious / High | The rendered text and background colors produce insufficient contrast. Text can be difficult to read for people with low vision. | Increase text contrast against its actual background. | Baseline / P3-R01 |
| P3-05 | booking | color-contrast `.btn-outline-secondary.btn-sm.btn:nth-child(5) > div:nth-child(2)` | axe-core, Lighthouse | serious / High | The rendered text and background colors produce insufficient contrast. Text can be difficult to read for people with low vision. | Increase text contrast against its actual background. | Baseline / P3-R01 |
| P3-06 | booking | color-contrast `.btn-outline-secondary.btn-sm.btn:nth-child(6) > div:nth-child(2)` | axe-core, Lighthouse | serious / High | The rendered text and background colors produce insufficient contrast. Text can be difficult to read for people with low vision. | Increase text contrast against its actual background. | Baseline / P3-R01 |
| P3-07 | booking | color-contrast `.btn-outline-secondary.btn-sm.btn:nth-child(7) > div:nth-child(2)` | axe-core, Lighthouse | serious / High | The rendered text and background colors produce insufficient contrast. Text can be difficult to read for people with low vision. | Increase text contrast against its actual background. | Baseline / P3-R01 |
| P3-08 | booking | color-contrast `.btn-outline-secondary.btn-sm.btn:nth-child(8) > div:nth-child(2)` | axe-core, Lighthouse | serious / High | The rendered text and background colors produce insufficient contrast. Text can be difficult to read for people with low vision. | Increase text contrast against its actual background. | Baseline / P3-R01 |
| P3-09 | booking | heading-order `#book > .card.mb-4 > .card-header.justify-content-between.align-items-center > .mb-0` | axe-core, Lighthouse | moderate / Medium | A task heading skips a level in the dashboard hierarchy. Heading navigation does not reflect the hierarchy. | Use a task heading at the appropriate semantic level. | Baseline / P3-R01 |
| P3-10 | booking | label `#book input[type="date"]` | axe-core, Lighthouse | critical / High | The visible Date label has no programmatic association with the date input. Screen readers cannot identify the purpose of the date input. | Associate the visible Date label with its input. | Baseline / P3-R01 |
| P3-11 | booking | landmark-one-main `html` | axe-core | moderate / Medium | The dashboard markup lacks a main landmark. Landmark navigation cannot jump to the primary content. | Wrap the primary content in a main landmark. | Baseline / P3-R01 |
| P3-12 | booking | page-has-heading-one `html` | axe-core | moderate / Medium | The dashboard markup lacks an h1. Heading navigation offers no top-level page name. | Identify the dashboard with an h1. | Baseline / P3-R01 |
| P3-13 | booking | region `.alert-success` | axe-core | moderate / Medium | The element sits outside recognised landmarks. Landmark navigation can miss this part of the page. | Place the element in an appropriate landmark. | Baseline / P3-R01 |
| P3-14 | booking | region `.container > .mb-4:nth-child(1)` | axe-core | moderate / Medium | The element sits outside recognised landmarks. Landmark navigation can miss this part of the page. | Place the element in an appropriate landmark. | Baseline / P3-R01 |
| P3-15 | booking | region `.g-3` | axe-core | moderate / Medium | The element sits outside recognised landmarks. Landmark navigation can miss this part of the page. | Place the element in an appropriate landmark. | Baseline / P3-R01 |
| P3-16 | booking | region `#patientTabs` | axe-core | moderate / Medium | The element sits outside recognised landmarks. Landmark navigation can miss this part of the page. | Place the element in an appropriate landmark. | Baseline / P3-R01 |
| P3-17 | booking | region `#book` | axe-core | moderate / Medium | The element sits outside recognised landmarks. Landmark navigation can miss this part of the page. | Place the element in an appropriate landmark. | Baseline / P3-R01 |
| P3-18 | booking | meta-description `document metadata` | Lighthouse | SEO (unrated) / Low | The shared document has no meta description. Indexable pages lack a summary for search engines. | Add a description to the public page when discoverability is intended. | Baseline / P3-R03 |
| P3-19 | booking | robots-txt `/robots.txt` | Lighthouse | SEO (unrated) / Low | The SPA fallback serves HTML for /robots.txt. Crawlers receive invalid robots directives from this URL. | Serve a valid robots.txt for the public site and keep patient data private. | Baseline / P3-R03 |
| P3-20 | cancellation | button-name `.alert-success > .btn-close[type="button"]` | axe-core, Lighthouse | critical / High | The icon-only close button lacks an accessible name. Screen readers cannot identify the dismiss button. | Give the dismiss button an accessible name. | Baseline / P3-R01 |
| P3-21 | cancellation | color-contrast `.alert-success` | axe-core, Lighthouse | serious / High | The rendered text and background colors produce insufficient contrast. Text can be difficult to read for people with low vision. | Increase text contrast against its actual background. | Baseline / P3-R01 |
| P3-22 | cancellation | heading-order `.bg-white > .mb-0` | axe-core, Lighthouse | moderate / Medium | A task heading skips a level in the dashboard hierarchy. Heading navigation does not reflect the hierarchy. | Use a task heading at the appropriate semantic level. | Baseline / P3-R01 |
| P3-23 | cancellation | landmark-one-main `html` | axe-core | moderate / Medium | The dashboard markup lacks a main landmark. Landmark navigation cannot jump to the primary content. | Wrap the primary content in a main landmark. | Baseline / P3-R01 |
| P3-24 | cancellation | page-has-heading-one `html` | axe-core | moderate / Medium | The dashboard markup lacks an h1. Heading navigation offers no top-level page name. | Identify the dashboard with an h1. | Baseline / P3-R01 |
| P3-25 | cancellation | region `.alert-success` | axe-core | moderate / Medium | The element sits outside recognised landmarks. Landmark navigation can miss this part of the page. | Place the element in an appropriate landmark. | Baseline / P3-R01 |
| P3-26 | cancellation | region `.container > .mb-4:nth-child(1)` | axe-core | moderate / Medium | The element sits outside recognised landmarks. Landmark navigation can miss this part of the page. | Place the element in an appropriate landmark. | Baseline / P3-R01 |
| P3-27 | cancellation | region `.row.g-3.mb-4` | axe-core | moderate / Medium | The element sits outside recognised landmarks. Landmark navigation can miss this part of the page. | Place the element in an appropriate landmark. | Baseline / P3-R01 |
| P3-28 | cancellation | region `#patientTabs` | axe-core | moderate / Medium | The element sits outside recognised landmarks. Landmark navigation can miss this part of the page. | Place the element in an appropriate landmark. | Baseline / P3-R01 |
| P3-29 | cancellation | region `#patient-appointments` | axe-core | moderate / Medium | The element sits outside recognised landmarks. Landmark navigation can miss this part of the page. | Place the element in an appropriate landmark. | Baseline / P3-R01 |
| P3-30 | cancellation | meta-description `document metadata` | Lighthouse | SEO (unrated) / Low | The shared document has no meta description. Indexable pages lack a summary for search engines. | Add a description to the public page when discoverability is intended. | Baseline / P3-R03 |
| P3-31 | cancellation | robots-txt `/robots.txt` | Lighthouse | SEO (unrated) / Low | The SPA fallback serves HTML for /robots.txt. Crawlers receive invalid robots directives from this URL. | Serve a valid robots.txt for the public site and keep patient data private. | Baseline / P3-R03 |

## Workflow observations

| ID | Screen and controls | Impact and correction | Evidence |
|---|---|---|---|
| P3-M01 | Booking, specialty and doctor cards | High, P3-R01. Click-only containers excluded keyboard users. Use native buttons with visible focus. | [Baseline task](playwright.html) |
| P3-M02 | Booking, conflict alert | Medium, P3-R02. The UI relayed the API reason with no recovery instruction. Tell patients to choose another available time. | [Baseline rejection](../screenshots/before/booking-rejection.png) |

## Phase 3 risk register extension

| Risk | Priority | Control and remaining exposure |
|---|---|---|
| P3-R01 Patients cannot perceive content or operate controls | High | Rechecked booking with keyboard and automated audits. Shared welcome alert and landmark findings remain. |
| P3-R02 Patients cannot recover from a slot conflict | Medium | Verified corrective guidance and successful retry. The related Phase 2 double-booking risk remains tracked as R02. |
| P3-R03 Public pages expose confusing crawl metadata | Low | Review public metadata separately and retain private patient data behind authentication. |

See the [Phase 2 risk register](../../../../../docs/team/phase2-defect-and-risk-report.md#residual-risk-assessment-and-exit-control) and the [evidence index](../README.md).
