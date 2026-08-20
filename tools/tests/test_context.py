import unittest, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import context_report

class ContextTests(unittest.TestCase):
    def test_personal_quality_first_hard_budget(self):
        d=context_report.collect(ROOT,'personal')
        self.assertLessEqual(d['global_chars'],5500)  # Progressive-aware v2.5 ceiling target
        self.assertLessEqual(d['repo_chars'],3600)
        self.assertLessEqual(d['always_loaded_chars'],9100)


    def test_claude_personal_quality_first_hard_budget(self):
        d=context_report.collect(ROOT,'personal','claude')
        self.assertLessEqual(d['global_chars'],5500)
        self.assertLessEqual(d['repo_chars'],3600)
        self.assertLessEqual(d['always_loaded_chars'],9100)
        self.assertGreater(d['reduction_vs_old_custom_alone_pct'],20)

    def test_personal_still_reduces_old_custom_alone(self):
        # v1.2 deliberately spends more persistent context on universal quality guarantees.
        # It must still be materially smaller than the archived 11.5k custom prompt alone.
        d=context_report.collect(ROOT,'personal')
        self.assertGreater(d['reduction_vs_old_custom_alone_pct'],20)

    def test_standalone_under_quality_first_budget(self):
        self.assertLessEqual(context_report.collect(ROOT,'standalone')['always_loaded_chars'],9300)

    def test_skill_count(self):
        self.assertEqual(context_report.collect(ROOT,'personal')['skill_count'],12)

    def test_archived_baseline_is_measured_not_hardcoded(self):
        d=context_report.collect(ROOT,'personal')
        self.assertEqual(d['archived_old_custom_instructions_chars'],len((ROOT/'docs/migration/ORIGINAL_CUSTOM_INSTRUCTIONS.txt').read_text(encoding='utf-8')))

    def test_skill_accounting_splits_metadata_from_body(self):
        d=context_report.collect(ROOT,'personal')
        self.assertIn('skill_metadata_chars_loaded',d)
        self.assertIn('skill_full_body_chars_not_loaded',d)
        self.assertGreater(d['skill_metadata_chars_loaded'],0)
        self.assertGreater(d['skill_full_body_chars_not_loaded'],d['skill_metadata_chars_loaded'])
        self.assertNotIn('all_skill_chars_not_normally_loaded',d)

if __name__=='__main__': unittest.main()
