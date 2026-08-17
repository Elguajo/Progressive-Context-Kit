#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, json, re, sys

MIN_ATOMIC_RULES = 147

EXPECTED_SECTIONS = {
    'ROLE','TASK_CLASSIFICATION','REPOSITORY_GROUNDING','ENGINEERING_PRINCIPLES',
    'DECISION_WORKFLOW','CODE_REVIEW_MODE','IMPLEMENTATION','VALIDATION_LOOP',
    'SAFETY_AND_APPROVALS','DOCUMENTATION_UPDATE_APPROVAL','FINAL_REPORT','COMMUNICATION_STYLE'
}


def parse_source_lines(spec: str) -> set[int]:
    out: set[int] = set()
    for part in str(spec).split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            a, b = part.split('-', 1)
            if a.isdigit() and b.isdigit():
                out.update(range(int(a), int(b) + 1))
        elif part.isdigit():
            out.add(int(part))
    return out


def validate(root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warns: list[str] = []
    contract_p = root / 'docs/migration/BEHAVIOR_CONTRACT.json'
    scenarios_p = root / 'docs/evals/static/BEHAVIOR_SCENARIOS.json'
    original_p = root / 'docs/migration/ORIGINAL_CUSTOM_INSTRUCTIONS.txt'
    ids_pin_p = root / 'docs/migration/BEHAVIOR_IDS.sha256'
    for p in [contract_p, scenarios_p, original_p, ids_pin_p]:
        if not p.is_file():
            errors.append(f'missing behavior evidence: {p.relative_to(root)}')
    if errors:
        return errors, warns

    try:
        contract = json.loads(contract_p.read_text(encoding='utf-8'))
        scenarios = json.loads(scenarios_p.read_text(encoding='utf-8'))
    except Exception as exc:
        return [f'invalid behavior JSON: {exc}'], warns

    rules = contract.get('rules', [])
    if contract.get('rule_count') != len(rules):
        errors.append('BEHAVIOR_CONTRACT rule_count does not match rules length')
    if len(rules) < MIN_ATOMIC_RULES:
        errors.append(f'behavior contract lost atomic rules: only {len(rules)} rules (<{MIN_ATOMIC_RULES})')

    ids = [r.get('id') for r in rules]
    if len(ids) != len(set(ids)):
        errors.append('duplicate behavior rule IDs')
    if any(not isinstance(x, str) or not x for x in ids):
        errors.append('behavior rule with missing/invalid id')
    try:
        expected_ids_hash = ids_pin_p.read_text(encoding='utf-8').split()[0].lower()
        actual_ids_hash = hashlib.sha256(('\n'.join(sorted(ids)) + '\n').encode()).hexdigest()
        if actual_ids_hash != expected_ids_hash:
            errors.append('behavior rule ID set changed without updating BEHAVIOR_IDS.sha256')
    except Exception as exc:
        errors.append(f'cannot verify behavior ID pin: {exc}')

    original = original_p.read_text(encoding='utf-8')
    original_lines = original.splitlines()
    original_sections = set(re.findall(r'<([A-Z_]+)>', original)) or EXPECTED_SECTIONS
    contract_sections = {r.get('source_section') for r in rules}
    if contract_sections != original_sections:
        errors.append('atomic behavior sections differ from archived Custom Instructions sections')

    referenced_source_lines: set[int] = set()
    for r in rules:
        rid = r.get('id', '<missing>')
        source_refs = parse_source_lines(r.get('source_lines', ''))
        if not source_refs:
            errors.append(f'{rid}: missing/invalid source_lines')
        elif max(source_refs) > len(original_lines):
            errors.append(f'{rid}: source_lines exceed archived source length')
        referenced_source_lines.update(source_refs)
        owner = r.get('owner')
        anchor = r.get('anchor')
        if not isinstance(owner, str) or not owner:
            errors.append(f'{rid}: missing owner')
            continue
        p = root / owner
        if not p.is_file():
            errors.append(f'{rid}: owner missing: {owner}')
            continue
        if not isinstance(anchor, str) or not anchor:
            errors.append(f'{rid}: missing anchor')
        elif anchor not in p.read_text(encoding='utf-8'):
            errors.append(f'{rid}: behavior anchor missing from {owner}: {anchor!r}')

    # Every behavior-bearing archived line must be traceable to at least one atomic rule.
    # These two lines are structural labels with no independent behavior.
    ignored_structural = {
        'Classification precedence:', 'Before proposing or implementing anything non-trivial:',
        'Use this format:', '**Options:**', '**Pivot rule:**',
        'When reviewing code, evaluate four dimensions but report only real findings:',
        'A complete change includes:', 'For bug fixes:',
        'After implementation, validate from narrowest to broadest:', 'On failure:',
        'If validation cannot run, state:', '**Worktree**', '**Security**',
        'Refuse to implement:', 'State:', 'After completion, report concisely:'
    }
    uncovered_lines = []
    for n, line in enumerate(original_lines, 1):
        st = line.strip()
        if not st or re.fullmatch(r'</?[A-Z_]+>', st) or st in ignored_structural:
            continue
        if n not in referenced_source_lines:
            uncovered_lines.append(n)
    if uncovered_lines:
        errors.append('archived behavior-bearing source lines without atomic mapping: ' + ', '.join(map(str, uncovered_lines)))

    all_ids = set(ids)
    covered: set[str] = set()
    valid_skills = {p.parent.name for p in (root / '.agents/skills').glob('*/SKILL.md')}
    scenario_ids = set()
    for s in scenarios.get('scenarios', []):
        sid = s.get('id')
        if not sid or sid in scenario_ids:
            errors.append(f'duplicate/missing scenario id: {sid!r}')
        scenario_ids.add(sid)
        cov = s.get('covers', [])
        if not isinstance(cov, list) or not cov:
            errors.append(f'{sid}: scenario covers no behavior rules')
        for rid in cov:
            if rid not in all_ids:
                errors.append(f'{sid}: references unknown behavior id {rid}')
            covered.add(rid)
        for route in s.get('expected_route', []):
            if route not in valid_skills:
                errors.append(f'{sid}: expected route references missing skill {route}')
        if not s.get('must'):
            errors.append(f'{sid}: missing expected behavior statement')

    missing_scenarios = all_ids - covered
    if missing_scenarios:
        errors.append('behavior rules without eval scenario coverage: ' + ', '.join(sorted(missing_scenarios)))
    if scenarios.get('scenario_count') != len(scenarios.get('scenarios', [])):
        errors.append('BEHAVIOR_SCENARIOS scenario_count mismatch')

    return errors, warns


def main() -> int:
    ap = argparse.ArgumentParser(description='Verify atomic migration coverage and behavior scenarios.')
    ap.add_argument('--root', default='.')
    args = ap.parse_args()
    root = Path(args.root).resolve()
    errors, warns = validate(root)
    for x in errors: print('ERROR:', x)
    for x in warns: print('WARN:', x)
    if errors:
        print(f'BEHAVIOR CONTRACT: FAIL ({len(errors)} errors, {len(warns)} warnings)')
        return 1
    contract = json.loads((root/'docs/migration/BEHAVIOR_CONTRACT.json').read_text(encoding='utf-8'))
    scenarios = json.loads((root/'docs/evals/static/BEHAVIOR_SCENARIOS.json').read_text(encoding='utf-8'))
    print(f"BEHAVIOR CONTRACT: PASS ({contract['rule_count']} atomic rules, {scenarios['scenario_count']} scenarios)")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
