import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class ExecutionEfficiencyTests(unittest.TestCase):
    def test_implementation_skill_batches_known_environment_prerequisites(self):
        canonical = (ROOT / '.agents/skills/implementation-execution/SKILL.md').read_text(encoding='utf-8')
        mirror = (ROOT / '.claude/skills/implementation-execution/SKILL.md').read_text(encoding='utf-8')

        self.assertEqual(canonical, mirror)
        for phrase in [
            'one grouped probe',
            'Resolve only confirmed missing prerequisites',
            'do not install speculative packages',
            'A later probe is justified only by new evidence',
        ]:
            self.assertIn(phrase, canonical)

    def test_environment_probe_preserves_scope_and_approval_guards(self):
        text = (ROOT / '.agents/skills/implementation-execution/SKILL.md').read_text(encoding='utf-8')
        self.assertIn('respect existing dependency/approval policy', text)
        self.assertIn('do not install speculative packages', text)
        self.assertIn('do not', text)
        self.assertIn('small task into environment setup', text)


if __name__ == '__main__':
    unittest.main()
