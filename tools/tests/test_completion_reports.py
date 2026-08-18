import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / 'tools/init_project.py'


class PhaseCompletionReportTests(unittest.TestCase):
    def run_init(self, target, *args):
        return subprocess.run(
            [sys.executable, str(INIT), str(target), *args],
            capture_output=True,
            text=True,
        )

    def test_new_runtime_contains_completion_layer_and_template(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / 'project'
            result = self.run_init(target, '--profile', 'standalone')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((target / '.progressive/completions').is_dir())
            self.assertTrue((target / '.progressive/templates/PHASE_COMPLETION.template.md').is_file())
            handoff = (target / '.progressive/system/HANDOFF_PROTOCOL.md').read_text(encoding='utf-8')
            self.assertIn('.progressive/completions/', handoff)

    def test_framework_update_preserves_user_completion_report(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / 'project'
            first = self.run_init(target, '--profile', 'standalone')
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            report = target / '.progressive/completions/00-example.md'
            report.write_text('# USER PHASE REPORT\n\nDurable implementation history.\n', encoding='utf-8')
            result = self.run_init(target, '--update-framework')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(
                report.read_text(encoding='utf-8'),
                '# USER PHASE REPORT\n\nDurable implementation history.\n',
            )

    def test_legacy_completed_phase_without_report_remains_audit_compatible(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / 'project'
            result = self.run_init(target, '--profile', 'standalone')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            phase = target / '.progressive/phases/00-legacy.md'
            phase.write_text(
                '# Phase 00 — Legacy\n\n## Completion Record\nDelivered: legacy result\n',
                encoding='utf-8',
            )
            roadmap = target / '.progressive/project/ROADMAP.md'
            roadmap.write_text(
                '# Roadmap\n\n- [x] Phase 00 — `.progressive/phases/00-legacy.md`\n',
                encoding='utf-8',
            )
            audit = subprocess.run(
                [sys.executable, str(target / '.progressive/tools/audit.py'), '--root', str(target)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(audit.returncode, 0, audit.stdout + audit.stderr)


if __name__ == '__main__':
    unittest.main()
