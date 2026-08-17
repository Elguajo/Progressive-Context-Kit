import unittest,tempfile,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/'tools/init_project.py'

class InitTests(unittest.TestCase):
    def run_cmd(self,target,*args):
        return subprocess.run([sys.executable,str(SCRIPT),str(target),*args],capture_output=True,text=True)

    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'p'
            result=self.run_cmd(target,'--dry-run')
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertFalse(target.exists())

    def test_personal_install_uses_hidden_runtime_and_personal_router(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'p'
            result=self.run_cmd(target,'--profile','personal')
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn('.progressive/',(target/'AGENTS.md').read_text(encoding='utf-8'))
            self.assertEqual((target/'.progressive/PROFILE').read_text().strip(),'personal')
            self.assertEqual((target/'.progressive/AGENT_TARGET').read_text().strip(),'both')
            self.assertIn('NOTE Codex Personal',result.stdout)
            self.assertIn('NOTE Claude Personal',result.stdout)
            self.assertIn('@AGENTS.md',(target/'CLAUDE.md').read_text(encoding='utf-8'))
            self.assertTrue((target/'.progressive/system/QUALITY_PROTOCOL.md').is_file())
            self.assertFalse((target/'docs').exists())
            self.assertFalse((target/'global').exists())
            audit=subprocess.run([sys.executable,str(target/'.progressive/tools/audit.py'),'--root',str(target)],capture_output=True,text=True)
            self.assertEqual(audit.returncode,0,audit.stdout+audit.stderr)

    def test_agent_target_keeps_portable_skill_mirrors_without_global_folder(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'p'
            result=self.run_cmd(target,'--profile','personal','--agent','claude')
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertEqual((target/'.progressive/AGENT_TARGET').read_text().strip(),'claude')
            self.assertIn('NOTE Claude Personal',result.stdout)
            self.assertNotIn('NOTE Codex Personal',result.stdout)
            self.assertTrue((target/'.agents/skills').is_dir())
            self.assertTrue((target/'.claude/skills').is_dir())
            self.assertFalse((target/'global').exists())

    def test_standalone_install_is_zero_setup(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'p'
            result=self.run_cmd(target,'--profile','standalone')
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn('Standalone Project Runtime needs no user-level global',result.stdout)
            self.assertEqual((target/'.progressive/PROFILE').read_text().strip(),'standalone')
            audit=subprocess.run([sys.executable,str(target/'.progressive/tools/audit.py'),'--root',str(target)],capture_output=True,text=True)
            self.assertEqual(audit.returncode,0,audit.stdout+audit.stderr)

    def test_update_preserves_project_state(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'p'
            self.assertEqual(self.run_cmd(target,'--profile','standalone').returncode,0)
            brief=target/'.progressive/project/PROJECT_BRIEF.md'
            brief.write_text('USER PROJECT STATE',encoding='utf-8')
            result=self.run_cmd(target,'--profile','standalone','--update-framework')
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertEqual(brief.read_text(encoding='utf-8'),'USER PROJECT STATE')

    def test_update_refuses_unmarked_repo(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'p'; target.mkdir(); (target/'AGENTS.md').write_text('USER')
            result=self.run_cmd(target,'--update-framework')
            self.assertNotEqual(result.returncode,0)
            self.assertEqual((target/'AGENTS.md').read_text(),'USER')

if __name__=='__main__': unittest.main()
