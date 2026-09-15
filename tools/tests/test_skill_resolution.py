import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / 'tools/init_project.py'


class SkillResolutionTests(unittest.TestCase):
    def install_runtime(self, target):
        result = subprocess.run(
            [sys.executable, str(INIT), str(target), '--profile', 'standalone'],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def run_runtime_audit(self, target, home):
        env = {**os.environ, 'HOME': str(home)}
        return subprocess.run(
            [sys.executable, str(target / '.progressive/tools/audit.py'), '--root', str(target)],
            capture_output=True,
            text=True,
            env=env,
        )

    def add_global_skill(self, home, root_name, name):
        skill = home / root_name / 'skills' / name / 'SKILL.md'
        skill.parent.mkdir(parents=True)
        skill.write_text('---\nname: '+name+'\n---\n', encoding='utf-8')
        return skill

    def test_router_declares_repo_root_relative_project_skill_resolution(self):
        required = 'Routed `.agents/...` paths are repository-root-relative; project-local wins, never same-named global fallback.'
        for rel in ['profiles/personal/AGENTS.md', 'AGENTS.md', 'profiles/standalone/AGENTS.md']:
            self.assertIn(required, (ROOT / rel).read_text(encoding='utf-8'))

    def test_project_local_skill_wins_over_global_collisions(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            target = base / 'project'
            home = base / 'home'
            self.install_runtime(target)
            codex = self.add_global_skill(home, '.codex', 'implementation-execution')
            agents = self.add_global_skill(home, '.agents', 'implementation-execution')
            result = self.run_runtime_audit(target, home)
            primary = target / '.agents/skills/implementation-execution/SKILL.md'
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('Skill collision: implementation-execution', result.stdout)
            self.assertIn('PRIMARY: '+str(primary.resolve()), result.stdout)
            self.assertIn(str(codex), result.stdout)
            self.assertIn(str(agents), result.stdout)
            self.assertIn('Resolution: project-local wins; no same-named global fallback.', result.stdout)

    def test_missing_project_skill_is_an_error_without_global_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            target = base / 'project'
            home = base / 'home'
            self.install_runtime(target)
            self.add_global_skill(home, '.codex', 'implementation-execution')
            missing = target / '.agents/skills/implementation-execution/SKILL.md'
            missing.unlink()
            missing.parent.rmdir()
            result = self.run_runtime_audit(target, home)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Expected project Skill is missing: '+str(missing.resolve()), result.stdout)

    def test_unique_global_skill_does_not_conflict_with_project_routing(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            target = base / 'project'
            home = base / 'home'
            self.install_runtime(target)
            self.add_global_skill(home, '.codex', 'external-only')
            result = self.run_runtime_audit(target, home)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertNotIn('external-only', result.stdout)


if __name__ == '__main__':
    unittest.main()
