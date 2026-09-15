import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from runtime_layout import write_runtime


class RuntimeSkillResolutionTests(unittest.TestCase):
    def make_runtime(self, parent):
        runtime = Path(parent) / 'runtime'
        write_runtime(ROOT, runtime, profile='standalone', agent='both')
        return runtime

    def run_audit(self, runtime, home):
        env = os.environ.copy()
        env['HOME'] = str(home)
        return subprocess.run(
            [sys.executable, str(runtime / '.progressive/tools/audit.py'), '--root', str(runtime)],
            capture_output=True,
            text=True,
            env=env,
        )

    def add_global_skill(self, home, root, name):
        path = home / root / name / 'SKILL.md'
        path.parent.mkdir(parents=True)
        path.write_text('global skill\n', encoding='utf-8')
        return path

    def test_project_skill_wins_over_same_named_global_skills(self):
        with tempfile.TemporaryDirectory() as d:
            parent = Path(d)
            runtime = self.make_runtime(parent)
            home = parent / 'home'
            codex = self.add_global_skill(home, '.codex/skills', 'implementation-execution')
            agents = self.add_global_skill(home, '.agents/skills', 'implementation-execution')

            result = self.run_audit(runtime, home)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            primary = (runtime / '.agents/skills/implementation-execution/SKILL.md').resolve()
            self.assertIn(f'PRIMARY: {primary}', result.stdout)
            self.assertIn(f'ALSO FOUND: {codex}', result.stdout)
            self.assertIn(str(agents), result.stdout)
            self.assertIn('project-local wins', result.stdout)

    def test_missing_project_skill_fails_even_when_global_skill_exists(self):
        with tempfile.TemporaryDirectory() as d:
            parent = Path(d)
            runtime = self.make_runtime(parent)
            home = parent / 'home'
            global_skill = self.add_global_skill(home, '.codex/skills', 'implementation-execution')
            (runtime / '.agents/skills/implementation-execution/SKILL.md').unlink()

            result = self.run_audit(runtime, home)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Expected project Skill is missing', result.stdout)
            self.assertIn(f'ALSO FOUND: {global_skill}', result.stdout)

    def test_unique_global_skill_does_not_fail_project_runtime_audit(self):
        with tempfile.TemporaryDirectory() as d:
            parent = Path(d)
            runtime = self.make_runtime(parent)
            home = parent / 'home'
            self.add_global_skill(home, '.codex/skills', 'unique-global-skill')

            result = self.run_audit(runtime, home)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertNotIn('unique-global-skill', result.stdout)


if __name__ == '__main__':
    unittest.main()
