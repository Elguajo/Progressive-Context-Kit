import unittest,tempfile,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/'tools/init_project.py'
sys.path.insert(0,str(ROOT/'tools'))
from runtime_layout import PROJECT_INSTRUCTIONS_SENTINEL, render_agent_profile

class InitTests(unittest.TestCase):
    def run_cmd(self,target,*args):
        return subprocess.run([sys.executable,str(SCRIPT),str(target),*args],capture_output=True,text=True)

    def snapshot(self,target):
        return {p.relative_to(target).as_posix():p.read_bytes()
                for p in target.rglob('*') if p.is_file()}

    def legacy_install(self,target,profile):
        self.assertEqual(self.run_cmd(target,'--profile',profile).returncode,0)
        legacy=(ROOT/f'tools/tests/fixtures/legacy_profiles/v3.0.0-{profile}.md').read_text(encoding='utf-8')
        (target/'AGENTS.md').write_text(legacy,encoding='utf-8')
        return legacy

    def test_standard_legacy_profiles_update_without_git_or_losing_project_state(self):
        for profile in ('personal','standalone'):
            with self.subTest(profile=profile),tempfile.TemporaryDirectory() as d:
                target=Path(d)/'p'
                self.legacy_install(target,profile)
                preserved={
                    '.progressive/project/PROJECT_BRIEF.md':'USER BRIEF',
                    '.progressive/project/NEXT_SESSION.md':'USER HANDOFF',
                    '.progressive/phases/01-phase.md':'USER PHASE',
                    '.progressive/phases/01-phase.prompts.md':'USER PROMPT HISTORY',
                    '.progressive/completions/00-complete.md':'USER EVIDENCE',
                    '.progressive/decisions/ADR-001.md':'USER DECISION',
                    'src/app.py':'USER SOURCE',
                }
                for rel,text in preserved.items():
                    path=target/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
                before=self.snapshot(target)
                dry=self.run_cmd(target,'--update-framework','--dry-run')
                self.assertEqual(dry.returncode,0,dry.stdout+dry.stderr)
                self.assertEqual(self.snapshot(target),before)
                result=self.run_cmd(target,'--update-framework')
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                self.assertEqual((target/'.progressive/PROFILE').read_text().strip(),profile)
                self.assertEqual((target/'AGENTS.md').read_text(),
                                 render_agent_profile(ROOT,profile).rstrip()+'\n'+PROJECT_INSTRUCTIONS_SENTINEL)
                for rel in preserved:self.assertEqual((target/rel).read_bytes(),before[rel])
                self.assertFalse((target/'.git').exists())
                updated=self.snapshot(target)
                self.assertEqual(self.run_cmd(target,'--update-framework').returncode,0)
                self.assertEqual(self.snapshot(target),updated)

    def test_legacy_appended_custom_instructions_are_preserved_under_boundary(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'p'
            legacy=self.legacy_install(target,'standalone')
            suffix='\n\n## Local rules\nUse pnpm only.\nKeep Cyrillic: Проверка.\n'
            (target/'AGENTS.md').write_text(legacy.rstrip()+suffix)
            result=self.run_cmd(target,'--update-framework')
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            _,actual=(target/'AGENTS.md').read_text().split(PROJECT_INSTRUCTIONS_SENTINEL,1)
            self.assertEqual(actual,suffix)

    def test_inline_edits_to_legacy_framework_prefix_are_not_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'p'
            legacy=self.legacy_install(target,'standalone')
            (target/'AGENTS.md').write_text(legacy.replace('## Context routing','## LOCAL CUSTOM CONTEXT'))
            before=self.snapshot(target)
            for args in (('--update-framework','--dry-run'),('--update-framework',)):
                result=self.run_cmd(target,*args)
                self.assertEqual(result.returncode,2,result.stdout+result.stderr)
                self.assertIn('not a recognized Progressive',result.stdout)
                self.assertEqual(self.snapshot(target),before)

    def test_unknown_claude_blocks_legacy_upgrade_before_any_write_including_dry_run(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'p'
            self.legacy_install(target,'standalone')
            (target/'CLAUDE.md').write_text('CUSTOM UNKNOWN CLAUDE')
            before=self.snapshot(target)
            for args in (('--update-framework','--dry-run'),('--update-framework',)):
                result=self.run_cmd(target,*args)
                self.assertEqual(result.returncode,2,result.stdout+result.stderr)
                self.assertIn('CLAUDE.md is not a recognized',result.stdout)
                self.assertEqual(self.snapshot(target),before)

    def test_new_installs_have_a_boundary_for_future_framework_updates(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'p'
            self.assertEqual(self.run_cmd(target,'--profile','standalone').returncode,0)
            agents=target/'AGENTS.md'
            self.assertIn(PROJECT_INSTRUCTIONS_SENTINEL,agents.read_text())
            agents.write_text(agents.read_text()+'LOCAL CONSTRAINT\n')
            self.assertEqual(self.run_cmd(target,'--update-framework').returncode,0)
            self.assertTrue(agents.read_text().endswith('LOCAL CONSTRAINT\n'))

    def test_explicit_profile_switch_recognizes_the_installed_legacy_profile(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'p'
            self.legacy_install(target,'personal')
            result=self.run_cmd(target,'--profile','standalone','--update-framework')
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn(render_agent_profile(ROOT,'standalone').rstrip(),(target/'AGENTS.md').read_text())
            self.assertEqual((target/'.progressive/PROFILE').read_text().strip(),'standalone')

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

    def test_update_without_explicit_profile_keeps_existing_profile(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'p'
            self.assertEqual(self.run_cmd(target,'--profile','standalone').returncode,0)
            result=self.run_cmd(target,'--update-framework')
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertEqual((target/'.progressive/PROFILE').read_text().strip(),'standalone')

    def test_update_refuses_unrecognized_claude_md(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'p'
            self.assertEqual(self.run_cmd(target,'--profile','standalone').returncode,0)
            (target/'CLAUDE.md').write_text('USER CUSTOM CLAUDE INSTRUCTIONS',encoding='utf-8')
            result=self.run_cmd(target,'--update-framework')
            self.assertNotEqual(result.returncode,0)
            self.assertEqual((target/'CLAUDE.md').read_text(encoding='utf-8'),'USER CUSTOM CLAUDE INSTRUCTIONS')

    def test_adopt_existing_preserves_unrecognized_claude_md_via_sentinel(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'p'; target.mkdir()
            (target/'CLAUDE.md').write_text('USER CUSTOM CLAUDE INSTRUCTIONS',encoding='utf-8')
            result=self.run_cmd(target,'--profile','standalone','--adopt-existing')
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            merged=(target/'CLAUDE.md').read_text(encoding='utf-8')
            self.assertIn('USER CUSTOM CLAUDE INSTRUCTIONS',merged)
            self.assertIn('PROJECT-SPECIFIC-CLAUDE-INSTRUCTIONS',merged)
            self.assertEqual((target/'.progressive/adoption-backup/CLAUDE.before.md').read_text(encoding='utf-8'),'USER CUSTOM CLAUDE INSTRUCTIONS')

    def test_update_refuses_unmarked_repo(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'p'; target.mkdir(); (target/'AGENTS.md').write_text('USER')
            result=self.run_cmd(target,'--update-framework')
            self.assertNotEqual(result.returncode,0)
            self.assertEqual((target/'AGENTS.md').read_text(),'USER')

if __name__=='__main__': unittest.main()
