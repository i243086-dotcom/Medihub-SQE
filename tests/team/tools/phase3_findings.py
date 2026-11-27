"""Build the element-level Phase 3 register from saved audit reports."""

from collections import Counter
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1] / 'evidence' / 'phase3'
PRIORITY = {'critical': 'High', 'serious': 'High', 'moderate': 'Medium', 'SEO (unrated)': 'Low'}
DETAILS = {
    'button-name': ('The icon-only close button lacks an accessible name.', 'Screen readers cannot identify the dismiss button.', 'Give the dismiss button an accessible name.', 'P3-R01'),
    'color-contrast': ('The rendered text and background colors produce insufficient contrast.', 'Text can be difficult to read for people with low vision.', 'Increase text contrast against its actual background.', 'P3-R01'),
    'heading-order': ('A task heading skips a level in the dashboard hierarchy.', 'Heading navigation does not reflect the hierarchy.', 'Use a task heading at the appropriate semantic level.', 'P3-R01'),
    'label': ('The visible Date label has no programmatic association with the date input.', 'Screen readers cannot identify the purpose of the date input.', 'Associate the visible Date label with its input.', 'P3-R01'),
    'landmark-one-main': ('The dashboard markup lacks a main landmark.', 'Landmark navigation cannot jump to the primary content.', 'Wrap the primary content in a main landmark.', 'P3-R01'),
    'page-has-heading-one': ('The dashboard markup lacks an h1.', 'Heading navigation offers no top-level page name.', 'Identify the dashboard with an h1.', 'P3-R01'),
    'region': ('The element sits outside recognised landmarks.', 'Landmark navigation can miss this part of the page.', 'Place the element in an appropriate landmark.', 'P3-R01'),
    'meta-description': ('The shared document has no meta description.', 'Indexable pages lack a summary for search engines.', 'Add a description to the public page when discoverability is intended.', 'P3-R03'),
    'robots-txt': ('The SPA fallback serves HTML for /robots.txt.', 'Crawlers receive invalid robots directives from this URL.', 'Serve a valid robots.txt for the public site and keep patient data private.', 'P3-R03'),
}


def read(stage, tool, screen):
    return json.loads((ROOT / stage / f'{tool}-{screen}.json').read_text(encoding='utf-8'))


def rows(stage, screen):
    axe = read(stage, 'axe', screen)
    lighthouse = read(stage, 'lighthouse', screen)
    failed = {key: item for key, item in lighthouse['audits'].items() if item['score'] == 0}
    for violation in axe['violations']:
        rule = violation['id']
        nodes = violation['nodes']
        matches = failed.pop(rule, {}).get('details', {}).get('items', [])
        if matches:
            # The same axe rule produces the same ordered set of affected elements.
            # Fail on a mismatch instead of pairing disagreeing tool results.
            assert len(matches) == len(nodes), (stage, screen, rule)
            for axe_node, match in zip(nodes, matches):
                snippet = match['node']['snippet']
                tag = re.match(r'<[\w-]+', snippet)[0]
                assert axe_node['html'].startswith(tag), (stage, screen, rule, snippet)
        for index, node in enumerate(nodes):
            target = ' / '.join(map(str, node['target']))
            if rule == 'label' and 'input[min=' in target:
                target = '#book input[type="date"]'
            yield {
                'rule': rule, 'element': target, 'impact': node['impact'],
                'axe': node['target'],
                'lighthouse': matches[index]['node'] if matches else None,
            }
    for rule, item in failed.items():
        assert rule in ('meta-description', 'robots-txt'), (stage, screen, rule)
        yield {'rule': rule, 'element': 'document metadata' if rule == 'meta-description' else '/robots.txt',
               'impact': 'SEO (unrated)', 'axe': None, 'lighthouse': item['title']}


def build(stages):
    reports = 'before/' if 'after' in stages else ''
    base = '' if 'after' in stages else '../'
    combined = {}
    summary = {}
    for screen in ('booking', 'cancellation'):
        summary[screen] = {}
        for stage in stages:
            issues = list(rows(stage, screen))
            report = read(stage, 'lighthouse', screen)
            summary[screen][stage] = {
                'scores': {key: round(item['score'] * 100) for key, item in report['categories'].items()},
                'axe_rules': len(read(stage, 'axe', screen)['violations']),
                'axe_elements': sum(item['axe'] is not None for item in issues),
                'unique': len(issues),
                'severity': Counter(item['impact'] for item in issues),
            }
            for item in issues:
                key = (screen, item['rule'], item['element'])
                combined.setdefault(key, {})[stage] = item

    table = ['# Phase 3 unified issue register', '',
             'One row per screen, rule and affected element. Lighthouse DOM paths and axe selectors are retained in the JSON register. SEO checks are counted per screen and have no axe severity.', '',
             '| ID | Screen | Rule and element | Source | Impact / priority | Cause and user impact | Proposed correction | Status / risk |',
             '|---|---|---|---|---|---|---|---|']
    entries = []
    for index, ((screen, rule, element), evidence) in enumerate(combined.items(), 1):
        cause, impact, fix, risk = DETAILS[rule]
        sources = [name for key, name in (('axe', 'axe-core'), ('lighthouse', 'Lighthouse'))
                   if any(item[key] for item in evidence.values())]
        status = 'Baseline' if len(stages) == 1 else 'Remains' if 'after' in evidence else 'Resolved in rerun'
        severity = next(iter(evidence.values()))['impact']
        priority = PRIORITY[severity]
        label = f'P3-{index:02d}'
        entries.append(dict(id=label, screen=screen, status=status, user_impact=impact,
                            root_cause=cause, priority=priority, risk=risk, proposed_fix=fix, evidence=evidence))
        safe_element = element.replace('|', '\\|')
        table.append(f'| {label} | {screen} | {rule} `{safe_element}` | {", ".join(sources)} | {severity} / {priority} | {cause} {impact} | {fix} | {status} / {risk} |')
    table.extend(['', '## Workflow observations', '',
                  '| ID | Screen and controls | Impact and correction | Evidence |',
                  '|---|---|---|---|',
                  f'| P3-M01 | Booking, specialty and doctor cards | High, P3-R01. Click-only containers excluded keyboard users. Use native buttons with visible focus. | [Baseline task]({reports}playwright.html) |',
                  f'| P3-M02 | Booking, conflict alert | Medium, P3-R02. The UI relayed the API reason with no recovery instruction. Tell patients to choose another available time. | [Baseline rejection]({base}screenshots/before/booking-rejection.png) |'])
    if 'after' in stages:
        table.extend(['', 'Both workflow observations were addressed and verified by the [after Playwright report](after/playwright.html), [focus capture](screenshots/after/booking-specialty-focus.png) and [rejection capture](screenshots/after/booking-rejection.png).'])
    table.extend(['', '## Phase 3 risk register extension', '',
                  '| Risk | Priority | Control and remaining exposure |',
                  '|---|---|---|',
                  '| P3-R01 Patients cannot perceive content or operate controls | High | Rechecked booking with keyboard and automated audits. Shared welcome alert and landmark findings remain. |',
                  '| P3-R02 Patients cannot recover from a slot conflict | Medium | Verified corrective guidance and successful retry. The related Phase 2 double-booking risk remains tracked as R02. |',
                  '| P3-R03 Public pages expose confusing crawl metadata | Low | Review public metadata separately and retain private patient data behind authentication. |',
                  '', f'See the [Phase 2 risk register]({base}../../../../docs/team/phase2-defect-and-risk-report.md#residual-risk-assessment-and-exit-control) and the [evidence index]({base}README.md).', ''])
    return '\n'.join(table), dict(summary=summary, entries=entries)


if __name__ == '__main__':
    baseline = '--baseline' in sys.argv
    markdown, data = build(('before',) if baseline else ('before', 'after'))
    output = ROOT / 'before' if baseline else ROOT
    (output / 'findings.md').write_text(markdown, encoding='utf-8')
    (output / 'findings.json').write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
