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

    def test_codex_global_is_progressive_aware_and_under_budget(self):
        text=(ROOT/'global/AGENTS.codex.md').read_text(encoding='utf-8')
        for heading in ['# Global Codex Working Agreement','## Role','## Progressive Context','## Grounding','## Engineering','## Safety and approvals','## Completion']:
            self.assertIn(heading,text)
        self.assertLessEqual(len(text),5500)
        self.assertIn('Silently classify work before acting:',text)
        self.assertIn('canonical project/workflow layer',text)
        self.assertIn('Pasted code without a question is a review request',text)

    def test_claude_global_is_progressive_aware_and_under_budget(self):
        text=(ROOT/'global/CLAUDE.md').read_text(encoding='utf-8')
        for heading in ['# Global Claude Code Working Agreement','## Role','## Progressive Context','## Grounding','## Engineering','## Safety and approvals','## Completion']:
            self.assertIn(heading,text)
        self.assertLessEqual(len(text),5500)
        self.assertIn('Silently classify work before acting:',text)
        self.assertIn('canonical project/workflow layer',text)
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

    def test_action_first_semantics_exist_in_both_global_adapters(self):
        required = [
            'minimum sufficient information',
            'Correctness > Safety > Task completeness > Actionability > Concision',
            'location -> cause -> fix',
        ]
        for rel in ['global/AGENTS.codex.md', 'global/CLAUDE.md']:
            text = (ROOT / rel).read_text(encoding='utf-8')
            for phrase in required:
                self.assertIn(phrase, text)
            self.assertIn('time estimates', text)
            self.assertIn('next action', text)

    def test_execution_efficiency_grounding_exists_in_both_global_adapters(self):
        required = [
            'batch independent facts',
            'inspect smallest sufficient slices',
            'never truncate data to transform/copy',
        ]
        for rel in ['global/AGENTS.codex.md', 'global/CLAUDE.md']:
            text = (ROOT / rel).read_text(encoding='utf-8')
            for phrase in required:
                self.assertIn(phrase, text)

    def test_progressive_aware_globals_delegate_conditional_policy(self):
        for rel in ['global/AGENTS.codex.md', 'global/CLAUDE.md']:
            text=(ROOT/rel).read_text(encoding='utf-8')
            self.assertIn('canonical project/workflow layer',text)
            self.assertIn('This contract owns universal behavior only',text)
            self.assertIn('use repository implementation/testing/quality procedures when available',text)
            self.assertIn('use repository governance for durable policy/decision docs',text)
            self.assertIn('Final report: **Result**; **Manual check** only when useful',text)
            self.assertNotIn('lightweight dev-only test framework may be added autonomously',text)
            self.assertNotIn('Automatically keep narrowly affected usage/setup docs',text)

    def test_execution_efficiency_grounding_is_generated_into_standalone(self):
        standalone = (ROOT/'profiles/standalone/AGENTS.md').read_text(encoding='utf-8')
        self.assertIn('batch independent facts', standalone)
        self.assertIn('inspect smallest sufficient slices', standalone)
        self.assertIn('never truncate data to transform/copy', standalone)

    def test_action_first_is_generated_not_duplicated_in_personal_router(self):
        standalone = (ROOT/'profiles/standalone/AGENTS.md').read_text(encoding='utf-8')
        personal = (ROOT/'profiles/personal/AGENTS.md').read_text(encoding='utf-8')
        self.assertIn('minimum sufficient information', standalone)
        self.assertNotIn('minimum sufficient information', personal)

if __name__ == '__main__': unittest.main()
