import json, unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from behavior_contract import validate

class BehaviorContractTests(unittest.TestCase):
    def test_behavior_contract_passes(self):
        errors,warns=validate(ROOT)
        self.assertEqual(errors,[])

    def test_atomic_rule_count_is_high_fidelity(self):
        data=json.loads((ROOT/'docs/migration/BEHAVIOR_CONTRACT.json').read_text(encoding='utf-8'))
        self.assertGreaterEqual(data['rule_count'],147)
        self.assertEqual(data['rule_count'],len(data['rules']))

    def test_every_rule_has_scenario_coverage(self):
        contract=json.loads((ROOT/'docs/migration/BEHAVIOR_CONTRACT.json').read_text(encoding='utf-8'))
        scenarios=json.loads((ROOT/'docs/evals/static/BEHAVIOR_SCENARIOS.json').read_text(encoding='utf-8'))
        rule_ids={r['id'] for r in contract['rules']}
        covered={rid for s in scenarios['scenarios'] for rid in s['covers']}
        self.assertEqual(rule_ids,covered)

    def test_exact_critical_behaviors_have_active_owners(self):
        data=json.loads((ROOT/'docs/migration/BEHAVIOR_CONTRACT.json').read_text(encoding='utf-8'))
        by_id={r['id']:r for r in data['rules']}
        critical=['TASK-06','DEC-08','DEC-11','REV-05','IMP-14','VAL-06','VAL-10','SAFE-11','DOC-06','FINAL-08']
        for rid in critical:
            r=by_id[rid]
            text=(ROOT/r['owner']).read_text(encoding='utf-8')
            self.assertIn(r['anchor'],text,rid)

    def test_architecture_decision_preserves_stop_rule(self):
        text=(ROOT/'.agents/skills/architecture-decision/SKILL.md').read_text(encoding='utf-8')
        self.assertIn('Then stop',text)
        self.assertIn('Do not implement until direction is chosen',text)

    def test_review_preserves_top_findings_and_do_nothing(self):
        text=(ROOT/'.agents/skills/code-review/SKILL.md').read_text(encoding='utf-8')
        self.assertIn('top 3–4 significant issues',text)
        self.assertIn('do nothing',text.lower())

    def test_validation_preserves_failure_classification(self):
        text=(ROOT/'docs/system/QUALITY_PROTOCOL.md').read_text(encoding='utf-8')
        self.assertIn('caused by the change',text)
        self.assertIn('pre-existing',text)
        self.assertIn('environmental',text)
        self.assertIn('exact command/check the user should run',text)


    def test_stop_rule_is_independently_pinned(self):
        data=json.loads((ROOT/'docs/migration/BEHAVIOR_CONTRACT.json').read_text(encoding='utf-8'))
        by_id={r['id']:r for r in data['rules']}
        self.assertEqual(by_id['DEC-08B']['source_lines'],'65')
        self.assertEqual(by_id['DEC-08B']['anchor'],'Then stop')

if __name__=='__main__': unittest.main()
