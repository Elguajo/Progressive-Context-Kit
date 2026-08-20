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
        self.assertIn('small task into environment setup', text)

    def test_quality_protocol_stops_after_sufficient_required_evidence(self):
        text = (ROOT / 'docs/system/QUALITY_PROTOCOL.md').read_text(encoding='utf-8')
        for phrase in [
            'current acceptance criteria',
            'stop validating',
            'do not add',
            'only for reassurance',
            'Convergence never',
            'justifies skipping a required check',
        ]:
            self.assertIn(phrase, text)

    def test_repeated_failure_pivots_and_debugging_skill_mirrors(self):
        canonical = (ROOT / '.agents/skills/systematic-debugging/SKILL.md').read_text(encoding='utf-8')
        mirror = (ROOT / '.claude/skills/systematic-debugging/SKILL.md').read_text(encoding='utf-8')

        self.assertEqual(canonical, mirror)
        for phrase in [
            'same check fails twice',
            'same underlying reason',
            'treat that as evidence',
            'against the approach',
            'one materially different hypothesis or corrective path',
        ]:
            self.assertIn(phrase, canonical)

    def test_quality_protocol_routes_wrong_approach_to_systematic_debugging(self):
        text = (ROOT / 'docs/system/QUALITY_PROTOCOL.md').read_text(encoding='utf-8')
        self.assertIn('route to `systematic-debugging`', text)
        self.assertIn('rather than continuing symptom patches', text)


if __name__ == '__main__':
    unittest.main()
