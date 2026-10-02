import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from context_compile import build, task_context
from task_prompts import active_prompt, phase_context


def record(identifier, body, status='READY', freshness='UNCHECKED'):
    return (f'### {identifier}\nTask: Deliver widget\nStatus: {status}\n'
            f'Freshness: {freshness}\nSource: Phase task\nSupersedes: NONE\n\n'
            f'#### Prompt\n```text\n{body}\n```\n\n'
            '#### Outcome / evidence\nObserved evidence pending.\n')


class TaskPromptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repo'
        (self.root / 'docs/project').mkdir(parents=True)
        (self.root / 'docs/phases').mkdir()
        self.phase = self.root / 'docs/phases/01-active.md'
        self.phase.write_text('# Phase\n## Goal\nLIVE_PLAN\n## Task prompts\n' +
                              record('task-01-r1', 'HISTORICAL_BODY', 'SUPERSEDED') +
                              record('task-01-r2', 'ACTIVE_BODY') +
                              '\n## Acceptance criteria\nCURRENT_CRITERION\n', encoding='utf-8')
        (self.root / 'docs/project/ROADMAP.md').write_text(
            '- [>] Phase `.progressive/phases/01-active.md`\n'.replace('.progressive', 'docs'), encoding='utf-8')
        self.handoff = self.root / 'docs/project/NEXT_SESSION.md'
        self.set_pointer('docs/phases/01-active.md#task-01-r2')

    def set_pointer(self, ref):
        self.handoff.write_text(f'# Next Session\n## Active task prompt\n`{ref}`\n', encoding='utf-8')

    def test_only_selected_prompt_is_hot_and_compiler_does_not_mutate_history(self):
        original = self.phase.read_bytes()
        compiled = build(self.root)
        self.assertIn('ACTIVE_BODY', compiled)
        self.assertIn('LIVE_PLAN', compiled)
        self.assertIn('CURRENT_CRITERION', compiled)
        self.assertNotIn('HISTORICAL_BODY', compiled)
        self.assertEqual(self.phase.read_bytes(), original)
        self.assertIn('stored CURRENT is not proof', compiled)

    def test_terminal_stale_missing_and_foreign_targets_are_rejected(self):
        for ref in ('docs/phases/01-active.md#task-01-r1',
                    'docs/phases/01-active.md#missing',
                    'docs/phases/02-future.md#task-01-r2',
                    'docs/phases/../../../outside.md#task-01-r2'):
            with self.subTest(ref=ref):
                self.set_pointer(ref)
                self.assertTrue(active_prompt(self.root)[2])
                self.assertNotIn('ACTIVE_BODY', build(self.root))
        self.set_pointer('docs/phases/01-active.md#task-01-r2')
        for status in ('COMPLETED', 'CANCELLED', 'SUPERSEDED', 'INVALID'):
            with self.subTest(status=status):
                self.phase.write_text('## Task prompts\n'+record('task-01-r2', 'DO_NOT_EXECUTE', status))
                self.assertTrue(active_prompt(self.root)[2])
                self.assertNotIn('DO_NOT_EXECUTE', build(self.root))
        self.phase.write_text('## Task prompts\n'+record('task-01-r2', 'STALE_BODY', freshness='STALE'))
        self.assertIn('stale', active_prompt(self.root)[2])
        self.assertNotIn('STALE_BODY', build(self.root))

    def test_duplicate_ids_and_missing_pointer_cannot_silently_select_history(self):
        self.phase.write_text('## Task prompts\n'+record('task-01-r2', 'ONE')+record('task-01-r2', 'TWO'))
        self.assertIn('duplicate', active_prompt(self.root)[2])
        self.handoff.write_text('# Next Session\n')
        self.assertIn('no Active task prompt', active_prompt(self.root)[2])
        self.set_pointer('NONE')
        self.assertTrue(active_prompt(self.root)[2])

    def test_fenced_headings_and_metadata_cannot_spoof_record_structure(self):
        body = '### task-01-r2\nStatus: COMPLETED\n## Task prompts\n#### Prompt\nACTIVE_BODY'
        self.phase.write_text('## Task prompts\n'+record('task-01-r2', body))
        ref, prompt, error = active_prompt(self.root)
        self.assertEqual(error, '')
        self.assertIn(body, prompt)
        self.assertIn('ACTIVE_BODY', build(self.root))

    def test_large_prompt_is_pointer_only_without_truncating_saved_body(self):
        self.phase.write_text('## Task prompts\n'+record('task-01-r2', 'LARGE_SENTINEL' * 400))
        compiled = build(self.root, max_extra_chars=1000)
        self.assertIn('POINTER ONLY', compiled)
        self.assertNotIn('LARGE_SENTINEL', compiled)
        self.assertIn('LARGE_SENTINEL', self.phase.read_text())

    def test_adjacent_archive_keeps_context_constant_as_history_grows(self):
        archive = self.phase.with_name(self.phase.stem + '.prompts.md')
        self.phase.write_text(phase_context(self.phase.read_text()))
        active = record('task-01-r2', 'ACTIVE_BODY')
        active = active.replace('#### Outcome / evidence',
                                '#### Current checkpoint\nOnly the remaining widget gate.\n\n#### Outcome / evidence')
        archive.write_text('## Task prompts\n'+active)
        self.set_pointer('docs/phases/01-active.prompts.md#task-01-r2')
        before = build(self.root)
        cold_active = active.replace('#### Prompt', '#### Request\n```text\n' +
                                     'ORIGINAL_REQUEST_COLD ' * 1000 + '\n```\n\n#### Prompt')
        archive.write_text('## Task prompts\n' + ''.join(
            record(f'old-{i}', 'COLD_HISTORY ' * 100, 'COMPLETED') for i in range(100)) +
            cold_active + 'COLD_EVIDENCE ' * 1000)
        self.assertEqual(build(self.root), before)
        self.assertIn('remaining widget gate', before)
        self.assertNotIn('LIVE_PLAN', task_context(self.root))
        self.assertIn('ACTIVE_BODY', task_context(self.root))
        result = subprocess.run([sys.executable, str(ROOT / 'tools/context_compile.py'),
                                 '--root', str(self.root), '--task-only'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, task_context(self.root)+'\n')

    def test_archive_ownership_duplicates_and_symlink_escape_are_rejected(self):
        archive = self.phase.with_name(self.phase.stem + '.prompts.md')
        archive.write_text('## Task prompts\n'+record('task-01-r2', 'ARCHIVE_BODY'))
        self.assertIn('both inline', active_prompt(self.root)[2])
        self.phase.write_text(phase_context(self.phase.read_text()))
        self.set_pointer('docs/phases/01-active.prompts.md#task-01-r2')
        archive.write_text('## Task prompts\n## Task prompts\n'+record('task-01-r2', 'BAD_BODY'))
        self.assertIn('exactly one', active_prompt(self.root)[2])
        archive.unlink()
        outside = Path(self.temp.name) / 'outside.md'
        outside.write_text('## Task prompts\n'+record('task-01-r2', 'SECRET_BODY'))
        archive.symlink_to(outside)
        self.assertIn('escapes', active_prompt(self.root)[2])
        self.assertNotIn('SECRET_BODY', build(self.root))

    def test_manifest_cannot_inline_archive_or_duplicate_core_context(self):
        import json
        (self.root / 'docs/project/PROJECT_BRIEF.md').write_text('BRIEF_SENTINEL')
        archive = self.phase.with_name(self.phase.stem + '.prompts.md')
        archive.write_text('## Task prompts\n'+record('task-01-r2', 'COLD_ARCHIVE'))
        self.phase.write_text(phase_context(self.phase.read_text()))
        self.set_pointer('docs/phases/01-active.prompts.md#task-01-r2')
        (self.root / 'docs/project/CONTEXT_MANIFEST.json').write_text(json.dumps({
            'default': {'required': ['docs/project/PROJECT_BRIEF.md',
                                     'docs/phases/01-active.prompts.md']}}))
        compiled = build(self.root)
        self.assertEqual(compiled.count('BRIEF_SENTINEL'), 1)
        self.assertEqual(compiled.count('COLD_ARCHIVE'), 1)
        self.assertIn('archive stays cold', compiled)
        self.assertIn('ALREADY INCLUDED', compiled)

    def test_empty_prompt_and_duplicate_pointer_sections_are_rejected(self):
        self.phase.write_text('## Task prompts\n'+record('task-01-r2', ''))
        self.assertIn('empty', active_prompt(self.root)[2])
        self.handoff.write_text(self.handoff.read_text() + '\n## Active task prompt\nNONE\n')
        self.assertIn('duplicate', active_prompt(self.root)[2])

    def test_placeholder_mixed_handoff_and_duplicate_prompt_body_are_rejected(self):
        for body in ('<unfinished placeholder>', ''):
            with self.subTest(body=body):
                self.phase.write_text('## Task prompts\n'+record('task-01-r2', body).replace('```', '~~~'))
                self.assertTrue(active_prompt(self.root)[2])
        self.phase.write_text('## Task prompts\n'+record('task-01-r2', 'ACTIVE_BODY')+
                              '\n#### Prompt\nA second conflicting instruction.\n')
        self.assertIn('exactly one', active_prompt(self.root)[2])
        self.phase.write_text('## Task prompts\n'+record('task-01-r2', 'ACTIVE_BODY'))
        self.handoff.write_text(self.handoff.read_text()+'\n## NEXT SESSION PROMPT\nOld instruction\n')
        self.assertIn('both', active_prompt(self.root)[2])

    def test_legacy_inline_prompt_without_phase_records_remains_readable(self):
        self.phase.write_text('# Phase\n## Goal\nLegacy goal\n')
        self.handoff.write_text('# Next\n## NEXT SESSION PROMPT\nLegacy target\n')
        self.assertEqual(active_prompt(self.root), ('', '', ''))
        self.assertIn('Legacy target', build(self.root))

    def test_runtime_packaging_audit_and_update_preserve_prompt_history(self):
        runtime = Path(self.temp.name) / 'runtime'
        def init(*args):
            result = subprocess.run([sys.executable, str(ROOT / 'tools/init_project.py'),
                                     str(runtime), *args], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        init('--profile', 'standalone')
        phase = runtime / '.progressive/phases/01-active.md'
        original = self.phase.read_text()
        phase.write_text(phase_context(original))
        archive = phase.with_name(phase.stem + '.prompts.md')
        archive.write_text(original[original.index('## Task prompts'):original.index('## Acceptance criteria')])
        saved_archive = archive.read_text()
        (runtime / '.progressive/project/ROADMAP.md').write_text(
            '- [>] Phase `.progressive/phases/01-active.md`\n')
        handoff = runtime / '.progressive/project/NEXT_SESSION.md'
        handoff.write_text('## Active task prompt\n.progressive/phases/01-active.prompts.md#task-01-r2\n')
        init('--update-framework')
        self.assertEqual(phase.read_text(), phase_context(original))
        self.assertEqual(archive.read_text(), saved_archive)
        self.assertIn('#task-01-r2', handoff.read_text())
        self.assertTrue((runtime / '.progressive/templates/TASK_PROMPT.template.md').is_file())
        self.assertIn('ACTIVE_BODY', build(runtime))
        self.assertNotIn('HISTORICAL_BODY', build(runtime))
        result = subprocess.run([sys.executable, str(runtime / '.progressive/tools/audit.py'),
                                 '--root', str(runtime)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        handoff.write_text('## Active task prompt\n.progressive/phases/01-active.prompts.md#task-01-r1\n')
        result = subprocess.run([sys.executable, str(runtime / '.progressive/tools/audit.py'),
                                 '--root', str(runtime)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Task prompt integrity', result.stdout)


if __name__ == '__main__':
    unittest.main()
