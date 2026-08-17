#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, json


def validate(root: Path):
    errors=[]; warns=[]
    contract_p=root/'docs/contracts/FRAMEWORK_CONTRACT.json'
    ids_p=root/'docs/contracts/FRAMEWORK_IDS.sha256'
    scenarios_p=root/'docs/evals/static/FRAMEWORK_SCENARIOS.json'
    for p in [contract_p,ids_p,scenarios_p]:
        if not p.is_file(): errors.append('missing framework contract evidence: '+str(p.relative_to(root)))
    if errors: return errors,warns
    try:
        contract=json.loads(contract_p.read_text(encoding='utf-8'))
        scenarios=json.loads(scenarios_p.read_text(encoding='utf-8'))
    except Exception as exc:
        return ['invalid framework contract JSON: '+str(exc)],warns
    rules=contract.get('rules',[])
    if contract.get('rule_count') != len(rules): errors.append('FRAMEWORK_CONTRACT rule_count mismatch')
    ids=[r.get('id') for r in rules]
    if len(ids)!=len(set(ids)): errors.append('duplicate framework rule IDs')
    canonical='\n'.join(sorted(x for x in ids if x))+'\n'
    expected=ids_p.read_text(encoding='utf-8').split()[0].lower()
    actual=hashlib.sha256(canonical.encode()).hexdigest()
    if actual!=expected: errors.append('FRAMEWORK_IDS.sha256 mismatch; rule set changed without pin update')
    covered=set()
    for sc in scenarios.get('scenarios',[]):
        for rid in sc.get('covers',[]): covered.add(rid)
    missing=set(ids)-covered
    extra=covered-set(ids)
    if missing: errors.append('framework rules missing static scenario coverage: '+', '.join(sorted(missing)))
    if extra: errors.append('static framework scenarios reference unknown rules: '+', '.join(sorted(extra)))
    for r in rules:
        owner=root/r.get('owner','')
        if not owner.is_file():
            errors.append(f"{r.get('id')} owner missing: {r.get('owner')}")
            continue
        anchor=r.get('anchor','')
        if anchor and anchor not in owner.read_text(encoding='utf-8'):
            errors.append(f"{r.get('id')} anchor missing from {r.get('owner')}: {anchor}")
    return errors,warns


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); a=ap.parse_args(); root=Path(a.root).resolve()
    errors,warns=validate(root)
    for x in errors: print('ERROR:',x)
    for x in warns: print('WARN:',x)
    if errors:
        print(f'FRAMEWORK CONTRACT: FAIL ({len(errors)} errors, {len(warns)} warnings)'); return 1
    data=json.loads((root/'docs/contracts/FRAMEWORK_CONTRACT.json').read_text(encoding='utf-8'))
    sc=json.loads((root/'docs/evals/static/FRAMEWORK_SCENARIOS.json').read_text(encoding='utf-8'))
    print(f"FRAMEWORK CONTRACT: PASS ({data.get('rule_count',0)} rules, {len(sc.get('scenarios',[]))} scenarios)")
    return 0
if __name__=='__main__': raise SystemExit(main())
