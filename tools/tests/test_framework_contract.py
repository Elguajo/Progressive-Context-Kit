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
        c=json.loads((ROOT/'docs/contracts/FRAMEWORK_CONTRACT.json').read_text()); self.assertGreaterEqual(c['rule_count'],26); self.assertEqual(c['rule_count'],len(c['rules']))
    def test_anchor_loss_fails(self):
        with tempfile.TemporaryDirectory() as d:
            dst=Path(d)/'r'; shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('dist','__pycache__'))
            p=dst/'profiles/personal/AGENTS.md'; p.write_text(p.read_text().replace('Do not interrupt a tiny task just to install tooling','Tiny tasks may install everything'))
            errors,_=validate(dst); self.assertTrue(any('FW-010' in x for x in errors))
    def test_lineage_not_normal_context(self):
        text=(ROOT/'profiles/personal/AGENTS.md').read_text(); self.assertIn('docs/system/LINEAGE.md',text); self.assertIn('Never warm up',text)
if __name__=='__main__': unittest.main()
