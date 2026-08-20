import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class ProgressiveAwareV25Tests(unittest.TestCase):
    def text(self, rel):
        return (ROOT / rel).read_text(encoding='utf-8')

    def test_universal_adapters_delegate_project_workflow(self):
        for rel in ['global/AGENTS.codex.md', 'global/CLAUDE.md']:
            text = self.text(rel)
            self.assertIn('canonical project/workflow layer', text)
            self.assertIn('This contract owns universal behavior only', text)
            self.assertIn('Efficiency may reduce context/reads/tool calls/turns/waiting, never correctness', text)

    def test_universal_adapters_do_not_duplicate_conditional_workflows(self):
        for rel in ['global/AGENTS.codex.md', 'global/CLAUDE.md']:
            text = self.text(rel)
            self.assertIn('use repository implementation/testing/quality procedures when available', text)
            self.assertIn('use repository governance for durable policy/decision docs', text)
            self.assertNotIn('lightweight dev-only test framework may be added autonomously', text)
            self.assertNotIn('Automatically keep narrowly affected usage/setup docs', text)
            self.assertNotIn('## Testing', text)
            self.assertNotIn('## Documentation', text)

    def test_architecture_decision_has_no_fixed_option_count(self):
        text = self.text('.agents/skills/architecture-decision/SKILL.md')
        self.assertIn('all materially different viable strategies', text)
        self.assertIn('Use no fixed count and never invent filler', text)
        self.assertNotIn('A — Pragmatic / Fast', text)
        self.assertNotIn('C — Balanced / Hybrid', text)

    def test_implementation_owns_richer_testing_policy(self):
        text = self.text('.agents/skills/implementation-execution/SKILL.md')
        self.assertIn('## Testing', text)
        self.assertIn('lightweight development-only framework may be added autonomously', text)
        self.assertIn('does not materially expand scope, complexity,', text)
        self.assertIn('Prefer a regression test reproducing the original defect', text)

    def test_documentation_governance_owns_detailed_policy(self):
        text = self.text('.agents/skills/documentation-governance/SKILL.md')
        self.assertIn('Update automatically when required by the approved implementation', text)
        self.assertIn('README usage/setup affected by the change', text)
        self.assertIn('Stop and ask before materially changing durable governance', text)

    def test_result_first_final_report_is_shared(self):
        for rel in ['global/AGENTS.codex.md', 'global/CLAUDE.md']:
            text = self.text(rel)
            self.assertIn('Final report: **Result**; **Manual check** only when useful', text)
            self.assertNotIn('Report: **Implemented**', text)


if __name__ == '__main__':
    unittest.main()
