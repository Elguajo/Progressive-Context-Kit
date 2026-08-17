import unittest, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from sync_profiles import compose

class ProfileTests(unittest.TestCase):
    def test_root_is_personal_profile_mirror(self):
        self.assertEqual((ROOT/'AGENTS.md').read_bytes(), (ROOT/'profiles/personal/AGENTS.md').read_bytes())

    def test_standalone_is_generated_composition(self):
        self.assertEqual((ROOT/'profiles/standalone/AGENTS.md').read_text(encoding='utf-8'), compose(ROOT))

    def test_claude_imports_active_root_profile_not_standalone_directly(self):
        text=(ROOT/'CLAUDE.md').read_text(encoding='utf-8')
        self.assertIn('@AGENTS.md', text)
        self.assertNotIn('@profiles/standalone/AGENTS.md', text)

    def test_codex_global_is_comprehensive_but_under_budget(self):
        text=(ROOT/'global/AGENTS.codex.md').read_text(encoding='utf-8')
        for heading in ['# Global Codex Working Agreement','## Role','## Grounding','## Engineering','## Safety and approvals','## Completion']:
            self.assertIn(heading,text)
        self.assertLessEqual(len(text),5000)
        self.assertIn('Silently classify work before acting',text)
        self.assertIn('Pasted code without a question is a review request',text)

    def test_claude_global_is_comprehensive_but_under_budget(self):
        text=(ROOT/'global/CLAUDE.md').read_text(encoding='utf-8')
        for heading in ['# Global Claude Code Working Agreement','## Role','## Grounding','## Engineering','## Safety and approvals','## Completion']:
            self.assertIn(heading,text)
        self.assertLessEqual(len(text),5000)
        self.assertIn('Silently classify work before acting',text)
        self.assertIn('Pasted code without a question is a review request',text)

    def test_personal_router_is_project_specific_and_vendor_neutral(self):
        text=(ROOT/'profiles/personal/AGENTS.md').read_text(encoding='utf-8')
        self.assertIn('Universal engineering behavior is supplied by the user-global layer', text)
        self.assertNotIn('global/AGENTS.codex.md', text)
        self.assertNotIn('global/CLAUDE.md', text)
        self.assertIn('## Context routing', text)
        self.assertIn('## Workflow routing', text)
        self.assertNotIn('## Safety and approvals', text)
        self.assertNotIn("The user's global Codex Custom Instructions", text)
        self.assertIn('implementation-execution', text)

if __name__ == '__main__': unittest.main()
