import unittest,subprocess,sys,shutil,tempfile,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

class AuditTests(unittest.TestCase):
    def run_audit(self,root):
        return subprocess.run([sys.executable,str(ROOT/'tools/audit.py'),'--root',str(root)],capture_output=True,text=True)

    def test_source_passes(self):
        result=self.run_audit(ROOT)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_missing_coverage_target_fails(self):
        with tempfile.TemporaryDirectory() as d:
            dst=Path(d)/'r'; shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('dist','__pycache__'))
            p=dst/'docs/migration/COVERAGE_MATRIX.json'; data=json.loads(p.read_text()); data['sections']['ROLE']=['missing.md']; p.write_text(json.dumps(data))
            self.assertNotEqual(self.run_audit(dst).returncode,0)

    def test_global_budget_fails(self):
        with tempfile.TemporaryDirectory() as d:
            dst=Path(d)/'r'; shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('dist','__pycache__'))
            (dst/'global/AGENTS.codex.md').write_text('x'*5001)
            self.assertNotEqual(self.run_audit(dst).returncode,0)

    def test_personal_root_mirror_drift_fails(self):
        with tempfile.TemporaryDirectory() as d:
            dst=Path(d)/'r'; shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('dist','__pycache__'))
            (dst/'AGENTS.md').write_text('drift')
            self.assertNotEqual(self.run_audit(dst).returncode,0)

    def test_standalone_composition_drift_fails(self):
        with tempfile.TemporaryDirectory() as d:
            dst=Path(d)/'r'; shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('dist','__pycache__'))
            p=dst/'profiles/standalone/AGENTS.md'; p.write_text(p.read_text()+'drift')
            self.assertNotEqual(self.run_audit(dst).returncode,0)

    def test_skill_drift_fails(self):
        with tempfile.TemporaryDirectory() as d:
            dst=Path(d)/'r'; shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('dist','__pycache__'))
            p=next((dst/'.claude/skills').glob('*/SKILL.md')); p.write_text('drift')
            self.assertNotEqual(self.run_audit(dst).returncode,0)

    def test_archive_hash_mutation_fails(self):
        with tempfile.TemporaryDirectory() as d:
            dst=Path(d)/'r'; shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('dist','__pycache__'))
            p=dst/'docs/migration/ORIGINAL_CUSTOM_INSTRUCTIONS.txt'; p.write_text(p.read_text()+'mutation')
            self.assertNotEqual(self.run_audit(dst).returncode,0)

    def test_legacy_completed_phase_without_record_warns_not_fails(self):
        with tempfile.TemporaryDirectory() as d:
            dst=Path(d)/'r'; shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('dist','__pycache__'))
            phase=dst/'docs/phases/00-legacy.md'; phase.write_text('# Phase 00 — Legacy\n\n## Goal\nDone\n')
            (dst/'docs/project/ROADMAP.md').write_text('# Roadmap\n- [x] Legacy `docs/phases/00-legacy.md`\n')
            result=self.run_audit(dst)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn('completed phase lacks durable Completion Record',result.stdout)

    def test_planned_future_phase_may_remain_roadmap_only(self):
        with tempfile.TemporaryDirectory() as d:
            dst=Path(d)/'r'; shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('dist','__pycache__'))
            active=dst/'docs/phases/90-active.md'; active.write_text('# Phase 90 — Active\n\n## Goal\nContinue.\n')
            future=dst/'docs/phases/91-future.md'
            if future.exists(): future.unlink()
            (dst/'docs/project/ROADMAP.md').write_text(
                '# Roadmap\n'
                '- [>] Phase 90 — `docs/phases/90-active.md`\n'
                '- [ ] Phase 91 — `docs/phases/91-future.md`\n'
            )
            result=self.run_audit(dst)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertFalse(future.exists())

    def test_missing_active_phase_file_still_fails(self):
        with tempfile.TemporaryDirectory() as d:
            dst=Path(d)/'r'; shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('dist','__pycache__'))
            missing=dst/'docs/phases/99-missing-active.md'
            if missing.exists(): missing.unlink()
            (dst/'docs/project/ROADMAP.md').write_text('# Roadmap\n- [>] Phase 99 — `docs/phases/99-missing-active.md`\n')
            result=self.run_audit(dst)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('Roadmap phase file missing',result.stdout)

    def test_behavior_anchor_loss_fails(self):
        with tempfile.TemporaryDirectory() as d:
            dst=Path(d)/'r'; shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('dist','__pycache__'))
            p=dst/'.agents/skills/architecture-decision/SKILL.md'
            p.write_text(p.read_text().replace('Then stop','Then continue'))
            # keep Claude mirror aligned so failure is specifically behavior-contract loss
            q=dst/'.claude/skills/architecture-decision/SKILL.md'; q.write_text(p.read_text())
            self.assertNotEqual(self.run_audit(dst).returncode,0)

if __name__=='__main__': unittest.main()
