import unittest, json, hashlib, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

class MigrationTests(unittest.TestCase):
    def test_all_archived_sections_are_covered(self):
        archived=(ROOT/'docs/migration/ORIGINAL_CUSTOM_INSTRUCTIONS.txt').read_text(encoding='utf-8')
        expected=set(re.findall(r'<([A-Z_]+)>',archived))
        data=json.loads((ROOT/'docs/migration/COVERAGE_MATRIX.json').read_text(encoding='utf-8'))
        self.assertEqual(set(data['sections']),expected)

    def test_all_targets_exist(self):
        data=json.loads((ROOT/'docs/migration/COVERAGE_MATRIX.json').read_text(encoding='utf-8'))
        for targets in data['sections'].values():
            for target in targets:
                self.assertTrue((ROOT/target).is_file(),target)

    def test_archived_custom_instructions_hash_is_pinned(self):
        src=ROOT/'docs/migration/ORIGINAL_CUSTOM_INSTRUCTIONS.txt'
        expected=(ROOT/'docs/migration/ORIGINAL_CUSTOM_INSTRUCTIONS.sha256').read_text().split()[0]
        self.assertEqual(hashlib.sha256(src.read_bytes()).hexdigest(),expected)

    def test_documentation_approval_has_on_demand_owner(self):
        data=json.loads((ROOT/'docs/migration/COVERAGE_MATRIX.json').read_text(encoding='utf-8'))
        self.assertIn('.agents/skills/documentation-governance/SKILL.md',data['sections']['DOCUMENTATION_UPDATE_APPROVAL'])


    def test_atomic_behavior_contract_exists(self):
        data=json.loads((ROOT/'docs/migration/BEHAVIOR_CONTRACT.json').read_text(encoding='utf-8'))
        self.assertGreaterEqual(data['rule_count'],147)

if __name__=='__main__': unittest.main()
