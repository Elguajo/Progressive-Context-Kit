import unittest, tempfile, subprocess, sys, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
VERSION=(ROOT/'VERSION').read_text().strip()

class RuntimeReleaseTests(unittest.TestCase):
    def test_project_runtime_is_hidden_self_contained_and_audits(self):
        build=subprocess.run([sys.executable,str(ROOT/'tools/build_runtime.py')],capture_output=True,text=True)
        self.assertEqual(build.returncode,0,build.stdout+build.stderr)
        z=ROOT/f'dist/Progressive-Context-Project-Runtime-v{VERSION}.zip'; self.assertTrue(z.is_file())
        with tempfile.TemporaryDirectory() as d:
            with zipfile.ZipFile(z) as zf: zf.extractall(d)
            runtime=Path(d)/f'Progressive-Context-Project-Runtime-v{VERSION}'
            # Only standard agent entrypoints + hidden framework dirs should exist before app code is added.
            visible={p.name for p in runtime.iterdir() if not p.name.startswith('.')}
            self.assertEqual(visible,{'AGENTS.md','CLAUDE.md'})
            for leaked in ['docs','global','integrations','profiles','prompts','templates','tools']:
                self.assertFalse((runtime/leaked).exists(), leaked)
            self.assertTrue((runtime/'.progressive/project/PROJECT_BRIEF.md').is_file())
            self.assertTrue((runtime/'.progressive/tools/context_compile.py').is_file())
            self.assertTrue((runtime/'.claude/skills').is_dir())
            self.assertTrue((runtime/'.agents/skills').is_dir())
            self.assertEqual((runtime/'.progressive/PROFILE').read_text().strip(),'standalone')
            self.assertIn('.progressive/project/',(runtime/'AGENTS.md').read_text(encoding='utf-8'))
            self.assertNotIn('docs/project/',(runtime/'AGENTS.md').read_text(encoding='utf-8'))
            audit=subprocess.run([sys.executable,str(runtime/'.progressive/tools/audit.py'),'--root',str(runtime)],capture_output=True,text=True)
            self.assertEqual(audit.returncode,0,audit.stdout+audit.stderr)
            compile_=subprocess.run([sys.executable,str(runtime/'.progressive/tools/context_compile.py'),'--root',str(runtime)],capture_output=True,text=True)
            self.assertEqual(compile_.returncode,0,compile_.stdout+compile_.stderr)

    def test_legacy_build_starter_command_builds_runtime(self):
        result=subprocess.run([sys.executable,str(ROOT/'tools/build_starter.py')],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('Progressive-Context-Project-Runtime',result.stdout)

if __name__=='__main__': unittest.main()
