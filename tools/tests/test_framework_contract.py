import json, unittest, sys, tempfile, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from framework_contract import validate

class FrameworkContractTests(unittest.TestCase):
    def test_framework_contract_passes(self):
        errors,warns=validate(ROOT); self.assertEqual(errors,[])
    def test_all_rules_have_static_scenario_coverage(self):
        c=json.loads((ROOT/'docs/contracts/FRAMEWORK_CONTRACT.json').read_text())
        s=json.loads((ROOT/'docs/evals/static/FRAMEWORK_SCENARIOS.json').read_text())
        self.assertEqual({r['id'] for r in c['rules']},{rid for sc in s['scenarios'] for rid in sc['covers']})
    def test_framework_rule_count(self):
        c=json.loads((ROOT/'docs/contracts/FRAMEWORK_CONTRACT.json').read_text()); self.assertGreaterEqual(c['rule_count'],60); self.assertEqual(c['rule_count'],len(c['rules']))
    def test_execution_efficiency_rules_are_pinned_and_scenario_covered(self):
        c=json.loads((ROOT/'docs/contracts/FRAMEWORK_CONTRACT.json').read_text())
        s=json.loads((ROOT/'docs/evals/static/FRAMEWORK_SCENARIOS.json').read_text())
        rules={r['id']:r for r in c['rules']}
        expected={f'FW-{n:03d}' for n in range(42,48)}
        self.assertTrue(expected.issubset(rules))
        scenario=next(sc for sc in s['scenarios'] if sc['id']=='execution-efficiency')
        self.assertEqual(expected,set(scenario['covers']))
        self.assertEqual(rules['FW-042']['owner'],'global/AGENTS.codex.md')
        self.assertEqual(rules['FW-043']['owner'],'global/CLAUDE.md')
        self.assertEqual(rules['FW-044']['owner'],'.agents/skills/implementation-execution/SKILL.md')
        self.assertEqual(rules['FW-045']['owner'],'docs/system/QUALITY_PROTOCOL.md')
        self.assertEqual(rules['FW-046']['owner'],'.agents/skills/systematic-debugging/SKILL.md')
        self.assertEqual(rules['FW-047']['owner'],'.agents/skills/implementation-execution/SKILL.md')
    def test_execution_efficiency_measurement_is_paired_and_source_only(self):
        c=json.loads((ROOT/'docs/contracts/FRAMEWORK_CONTRACT.json').read_text())
        s=json.loads((ROOT/'docs/evals/static/FRAMEWORK_SCENARIOS.json').read_text())
        rules={r['id']:r for r in c['rules']}
        expected={'FW-048','FW-049'}
        scenario=next(sc for sc in s['scenarios'] if sc['id']=='execution-efficiency-measurement')
        self.assertEqual(expected,set(scenario['covers']))
        self.assertEqual(rules['FW-048']['owner'],'docs/evals/agent/EXECUTION_EFFICIENCY_PROTOCOL.md')
        self.assertEqual(rules['FW-049']['owner'],'docs/evals/agent/README.md')
    def test_autoresearch_loop_is_single_hypothesis_quality_gated_terminal_and_release_validated(self):
        c=json.loads((ROOT/'docs/contracts/FRAMEWORK_CONTRACT.json').read_text())
        s=json.loads((ROOT/'docs/evals/static/FRAMEWORK_SCENARIOS.json').read_text())
        rules={r['id']:r for r in c['rules']}
        expected={'FW-050','FW-051','FW-052','FW-053'}
        scenario=next(sc for sc in s['scenarios'] if sc['id']=='autoresearch-optimization-loop')
        self.assertEqual(expected,set(scenario['covers']))
        for rid in {'FW-050','FW-051','FW-052'}:
            self.assertEqual(rules[rid]['owner'],'docs/evals/agent/autoresearch/README.md')
        self.assertEqual(rules['FW-053']['owner'],'tools/build_release.py')
    def test_progressive_aware_v25_rules_are_owned_and_covered(self):
        c=json.loads((ROOT/'docs/contracts/FRAMEWORK_CONTRACT.json').read_text())
        s=json.loads((ROOT/'docs/evals/static/FRAMEWORK_SCENARIOS.json').read_text())
        rules={r['id']:r for r in c['rules']}
        expected={f'FW-{n:03d}' for n in range(54,61)}
        scenario=next(sc for sc in s['scenarios'] if sc['id']=='progressive-aware-universal-v2-5')
        self.assertEqual(expected,set(scenario['covers']))
        self.assertEqual(rules['FW-054']['owner'],'global/AGENTS.codex.md')
        self.assertEqual(rules['FW-055']['owner'],'global/CLAUDE.md')
        self.assertEqual(rules['FW-056']['owner'],'.agents/skills/architecture-decision/SKILL.md')
        self.assertEqual(rules['FW-057']['owner'],'.agents/skills/implementation-execution/SKILL.md')
        self.assertEqual(rules['FW-058']['owner'],'.agents/skills/documentation-governance/SKILL.md')
        self.assertEqual(rules['FW-059']['owner'],'global/AGENTS.codex.md')
        self.assertEqual(rules['FW-060']['owner'],'global/CLAUDE.md')
    def test_anchor_loss_fails(self):
        with tempfile.TemporaryDirectory() as d:
            dst=Path(d)/'r'; shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('dist','__pycache__'))
            p=dst/'profiles/personal/AGENTS.md'; p.write_text(p.read_text().replace('Do not interrupt a tiny task just to install tooling','Tiny tasks may install everything'))
            errors,_=validate(dst); self.assertTrue(any('FW-010' in x for x in errors))
    def test_lineage_not_normal_context(self):
        text=(ROOT/'profiles/personal/AGENTS.md').read_text(); self.assertIn('docs/system/LINEAGE.md',text); self.assertIn('Never warm up',text)
if __name__=='__main__': unittest.main()
