import unittest,tempfile,subprocess,sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; SCRIPT=ROOT/'tools/init_project.py'

class AdoptionTests(unittest.TestCase):
    def run_cmd(self,target,*args): return subprocess.run([sys.executable,str(SCRIPT),str(target),*args],capture_output=True,text=True)
    def test_adoption_dry_run_preserves_repo(self):
        with tempfile.TemporaryDirectory() as d:
            t=Path(d)/'p'; t.mkdir(); (t/'AGENTS.md').write_text('OLD RULES')
            r=self.run_cmd(t,'--adopt-existing','--dry-run'); self.assertEqual(r.returncode,0,r.stdout+r.stderr); self.assertEqual((t/'AGENTS.md').read_text(),'OLD RULES'); self.assertFalse((t/'.progressive').exists())
    def test_adoption_preserves_existing_agents_as_project_specific(self):
        with tempfile.TemporaryDirectory() as d:
            t=Path(d)/'p'; t.mkdir(); (t/'AGENTS.md').write_text('# Existing\nUse pnpm only.\n')
            r=self.run_cmd(t,'--adopt-existing'); self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            text=(t/'AGENTS.md').read_text(); self.assertIn('Progressive Context Kit — Personal Repository Router',text); self.assertIn('PROJECT-SPECIFIC-INSTRUCTIONS',text); self.assertIn('Use pnpm only.',text)
            self.assertTrue((t/'.progressive/adoption-backup/AGENTS.before.md').is_file())
            audit=subprocess.run([sys.executable,str(t/'.progressive/tools/audit.py'),'--root',str(t)],capture_output=True,text=True); self.assertEqual(audit.returncode,0,audit.stdout+audit.stderr)
    def test_update_preserves_project_specific_suffix(self):
        with tempfile.TemporaryDirectory() as d:
            t=Path(d)/'p'; t.mkdir(); (t/'AGENTS.md').write_text('LOCAL CONSTRAINT')
            self.assertEqual(self.run_cmd(t,'--adopt-existing').returncode,0)
            self.assertEqual(self.run_cmd(t,'--update-framework').returncode,0)
            self.assertIn('LOCAL CONSTRAINT',(t/'AGENTS.md').read_text())
    def test_framework_collision_marks_adoption_pending(self):
        with tempfile.TemporaryDirectory() as d:
            t=Path(d)/'p'; (t/'.progressive/integrations').mkdir(parents=True); (t/'.progressive/integrations/PROFILES.md').write_text('USER PROFILE')
            r=self.run_cmd(t,'--adopt-existing'); self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            self.assertEqual((t/'.progressive/ADOPTION_STATE').read_text().strip(),'pending')
            c=json.loads((t/'.progressive/ADOPTION_CONFLICTS.json').read_text()); self.assertIn('.progressive/integrations/PROFILES.md',c['conflicts'])
            audit=subprocess.run([sys.executable,str(t/'.progressive/tools/audit.py'),'--root',str(t)],capture_output=True,text=True); self.assertNotEqual(audit.returncode,0)
if __name__=='__main__': unittest.main()
