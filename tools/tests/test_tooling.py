import json, unittest, sys, tempfile, shutil, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

class ToolingTests(unittest.TestCase):
    def test_registry_has_preferred_brands_and_official_sources(self):
        d=json.loads((ROOT/'integrations/TOOL_REGISTRY.json').read_text())
        expected={'semble':'Semble','serena':'Serena','rtk':'RTK','superpowers':'Superpowers','gstack':'gstack','context7':'Context7','github_spec_kit':'GitHub Spec Kit'}
        self.assertEqual({k:v['brand'] for k,v in d['tools'].items()},expected)
        for v in d['tools'].values(): self.assertTrue(v['official'].startswith('https://github.com/'))
    def test_status_cache_covers_registry(self):
        r=json.loads((ROOT/'integrations/TOOL_REGISTRY.json').read_text()); s=json.loads((ROOT/'docs/project/TOOLING_STATUS.json').read_text())
        self.assertEqual(set(r['tools']),set(s['tools']))
    def test_tooling_bootstrap_profile_selection(self):
        script=ROOT/'tools/tooling_bootstrap.py'
        a=subprocess.run([sys.executable,str(script),'--root',str(ROOT),'--tier','S','--risk','Low'],capture_output=True,text=True); self.assertIn('selected_profile: minimal',a.stdout)
        b=subprocess.run([sys.executable,str(script),'--root',str(ROOT),'--tier','M','--risk','Medium'],capture_output=True,text=True); self.assertIn('selected_profile: recommended',b.stdout); self.assertIn('Semble',b.stdout)
        c=subprocess.run([sys.executable,str(script),'--root',str(ROOT),'--tier','L','--risk','High','--advanced-spec'],capture_output=True,text=True); self.assertIn('selected_profile: advanced_spec',c.stdout); self.assertIn('GitHub Spec Kit',c.stdout)
    def test_status_set_persists_without_network(self):
        with tempfile.TemporaryDirectory() as d:
            dst=Path(d)/'r'; shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('dist','__pycache__'))
            script=dst/'tools/tooling_status.py'
            r=subprocess.run([sys.executable,str(script),'--root',str(dst),'--set','semble','--status','configured','--version','test','--evidence','unit'],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            s=json.loads((dst/'docs/project/TOOLING_STATUS.json').read_text()); self.assertEqual(s['tools']['semble']['status'],'configured')
            self.assertIn('configured',(dst/'docs/project/TOOLING_STATUS.md').read_text())
    def test_profiles_keep_installed_not_loaded_rule(self):
        self.assertIn('Installed ≠ loaded ≠ invoked',(ROOT/'integrations/PROFILES.md').read_text())
if __name__=='__main__': unittest.main()
