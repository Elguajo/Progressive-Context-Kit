import shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from runtime_layout import write_runtime


class RoutingIntegrityTests(unittest.TestCase):
    def run_tool(self, root, runtime=False):
        tool = root / ('.progressive/tools/routing_integrity.py' if runtime else 'tools/routing_integrity.py')
        return subprocess.run([sys.executable, str(tool), '--root', str(root)], capture_output=True, text=True)

    def copy_source(self, parent):
        dst = Path(parent) / 'repo'
        shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns('dist', '__pycache__'))
        return dst

    def test_source_passes(self):
        result = self.run_tool(ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('ROUTING INTEGRITY: PASS', result.stdout)

    def test_automatic_skill_must_be_routed(self):
        with tempfile.TemporaryDirectory() as d:
            dst = self.copy_source(d)
            router = dst / 'profiles/personal/AGENTS.md'
            text = router.read_text(encoding='utf-8')
            text = text.replace('- unclear/inconsistent project state → `project-doctor`\n', '')
            router.write_text(text, encoding='utf-8')
            result = self.run_tool(dst)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('automatic Skill not routed: project-doctor', result.stdout)

    def test_dangling_router_target_fails(self):
        with tempfile.TemporaryDirectory() as d:
            dst = self.copy_source(d)
            router = dst / 'profiles/personal/AGENTS.md'
            text = router.read_text(encoding='utf-8')
            text = text.replace('For implementation completion use', '- synthetic route → `ghost-skill`\n\nFor implementation completion use')
            router.write_text(text, encoding='utf-8')
            result = self.run_tool(dst)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('router references missing Skill: ghost-skill', result.stdout)

    def test_explicit_skill_must_not_be_auto_routed(self):
        with tempfile.TemporaryDirectory() as d:
            dst = self.copy_source(d)
            router = dst / 'profiles/personal/AGENTS.md'
            text = router.read_text(encoding='utf-8')
            text = text.replace('For implementation completion use', '- framework audit → `workflow-audit`\n\nFor implementation completion use')
            router.write_text(text, encoding='utf-8')
            result = self.run_tool(dst)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('explicit Skill routed automatically: workflow-audit', result.stdout)

    def test_missing_required_path_fails(self):
        with tempfile.TemporaryDirectory() as d:
            dst = self.copy_source(d)
            skill = dst / '.agents/skills/project-bootstrap/SKILL.md'
            text = skill.read_text(encoding='utf-8').replace(
                'requires: ["prompts/START_NEW_PROJECT.md", "docs/system/PLANNING_DEPTH.md"]',
                'requires: ["missing.md"]',
            )
            skill.write_text(text, encoding='utf-8')
            result = self.run_tool(dst)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('project-bootstrap requires missing path: missing.md', result.stdout)

    def test_missing_delegate_target_fails(self):
        with tempfile.TemporaryDirectory() as d:
            dst = self.copy_source(d)
            skill = dst / '.agents/skills/implementation-execution/SKILL.md'
            text = skill.read_text(encoding='utf-8').replace(
                'may_delegate: ["systematic-debugging"]',
                'may_delegate: ["ghost-skill"]',
            )
            skill.write_text(text, encoding='utf-8')
            result = self.run_tool(dst)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('implementation-execution may_delegate target missing: ghost-skill', result.stdout)

    def test_delegate_cannot_target_explicit_only_skill(self):
        with tempfile.TemporaryDirectory() as d:
            dst = self.copy_source(d)
            skill = dst / '.agents/skills/implementation-execution/SKILL.md'
            text = skill.read_text(encoding='utf-8').replace(
                'may_delegate: ["systematic-debugging"]',
                'may_delegate: ["workflow-audit"]',
            )
            skill.write_text(text, encoding='utf-8')
            result = self.run_tool(dst)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('implementation-execution may_delegate targets explicit-only Skill: workflow-audit', result.stdout)

    def test_generated_runtime_routes_and_transformed_dependencies_pass(self):
        with tempfile.TemporaryDirectory() as d:
            runtime = Path(d) / 'runtime'
            write_runtime(ROOT, runtime, profile='standalone', agent='both')
            result = self.run_tool(runtime, runtime=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('ROUTING INTEGRITY: PASS', result.stdout)
            skill = runtime / '.agents/skills/project-bootstrap/SKILL.md'
            text = skill.read_text(encoding='utf-8')
            self.assertIn('.progressive/prompts/START_NEW_PROJECT.md', text)
            self.assertIn('.progressive/system/PLANNING_DEPTH.md', text)


if __name__ == '__main__':
    unittest.main()
