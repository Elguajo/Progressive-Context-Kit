import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))

from runtime_layout import runtime_entries, write_runtime


class UbiquitousLanguageTests(unittest.TestCase):
    def test_project_brief_template_owns_compact_optional_vocabulary(self):
        template = (ROOT / 'templates/PROJECT_BRIEF.template.md').read_text(encoding='utf-8')
        self.assertIn('## Ubiquitous Language', template)
        self.assertIn('Optional: 0–12 project-specific terms only', template)
        self.assertIn('<Term> — <precise project meaning>', template)

    def test_protocol_is_runtime_available_but_not_always_loaded(self):
        sources = {src.resolve() for src, _, _ in runtime_entries(ROOT, 'standalone')}
        protocol = (ROOT / 'docs/system/UBIQUITOUS_LANGUAGE.md').resolve()
        self.assertIn(protocol, sources)
        for rel in ['AGENTS.md', 'profiles/personal/AGENTS.md', 'global/AGENTS.codex.md', 'global/CLAUDE.md']:
            text = (ROOT / rel).read_text(encoding='utf-8')
            self.assertNotIn('UBIQUITOUS_LANGUAGE.md', text, rel)

    def test_lifecycle_prompts_route_semantics_without_separate_glossary(self):
        start = (ROOT / 'prompts/START_NEW_PROJECT.md').read_text(encoding='utf-8')
        adopt = (ROOT / 'prompts/ADOPT_EXISTING_PROJECT.md').read_text(encoding='utf-8')
        change = (ROOT / 'prompts/CHANGE_REQUEST.md').read_text(encoding='utf-8')
        self.assertIn('UBIQUITOUS_LANGUAGE.md', start)
        self.assertIn('UBIQUITOUS_LANGUAGE.md', adopt)
        self.assertIn('evidence-backed meanings', adopt)
        self.assertIn('domain semantics', change)
        self.assertIn('do not create a separate glossary', change)

    def test_context_invariant_pins_brief_as_domain_language_owner(self):
        contract = (ROOT / 'docs/contracts/PROGRESSIVE_CONTEXT_INVARIANTS.json').read_text(encoding='utf-8')
        ownership = (ROOT / 'docs/system/LAYER_OWNERSHIP.md').read_text(encoding='utf-8')
        self.assertIn('"id": "PC-013"', contract)
        self.assertIn('Project-domain vocabulary belongs in the **Project Brief**', (ROOT / 'docs/system/UBIQUITOUS_LANGUAGE.md').read_text(encoding='utf-8'))
        self.assertIn('Ubiquitous Language', ownership)
        self.assertIn('must not become a parallel glossary layer', ownership)

    def test_runtime_audit_warns_when_vocabulary_exceeds_compact_budget(self):
        with tempfile.TemporaryDirectory() as d:
            runtime = Path(d) / 'runtime'
            write_runtime(ROOT, runtime)
            terms = '\n'.join(f'- Term{i} — Meaning {i}.' for i in range(1, 14))
            brief = runtime / '.progressive/project/PROJECT_BRIEF.md'
            brief.write_text('# Project Brief\n\n## Ubiquitous Language\n' + terms + '\n', encoding='utf-8')
            result = subprocess.run(
                [sys.executable, str(runtime / '.progressive/tools/audit.py'), '--root', str(runtime)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('exceeds 12-term guidance: 13 terms', result.stdout)
            self.assertIn('RUNTIME AUDIT: PASS', result.stdout)

    def test_runtime_audit_warns_on_duplicate_canonical_term(self):
        with tempfile.TemporaryDirectory() as d:
            runtime = Path(d) / 'runtime'
            write_runtime(ROOT, runtime)
            brief = runtime / '.progressive/project/PROJECT_BRIEF.md'
            brief.write_text(
                '# Project Brief\n\n## Ubiquitous Language\n'
                '- Capture — Charge an authorized payment.\n'
                '- Capture — Finalize the transaction.\n',
                encoding='utf-8',
            )
            result = subprocess.run(
                [sys.executable, str(runtime / '.progressive/tools/audit.py'), '--root', str(runtime)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('repeats canonical terms: capture', result.stdout)


if __name__ == '__main__':
    unittest.main()
