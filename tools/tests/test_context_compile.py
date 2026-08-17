import json, unittest, tempfile, shutil, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from context_compile import build

class ContextCompileTests(unittest.TestCase):
    def test_compiler_excludes_lineage_and_framework_docs(self):
        text=build(ROOT); self.assertNotIn('Token-Efficient Spec Kit → Progressive',text); self.assertNotIn('BEHAVIOR_CONTRACT',text)

    def test_compiler_reads_current_phase_and_manifest_hints(self):
        with tempfile.TemporaryDirectory() as d:
            dst=Path(d)/'r'; shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('dist','__pycache__'))
            phase=dst/'docs/phases/001-test.md'; phase.write_text('# Phase 01 — Test\n\n## Goal\nShip X\n')
            (dst/'docs/project/ROADMAP.md').write_text('# Roadmap\n- [>] Test `docs/phases/001-test.md`\n')
            (dst/'docs/decisions/ADR-001.md').write_text('# ADR\nImportant choice\n')
            m={'schema':1,'default':{'required':[],'skills':[],'notes':[]},'phases':{'docs/phases/001-test.md':{'required':['docs/decisions/ADR-001.md'],'skills':['security-sensitive-change'],'notes':['critical path']}}}
            (dst/'docs/project/CONTEXT_MANIFEST.json').write_text(json.dumps(m))
            text=build(dst); self.assertIn('Ship X',text); self.assertIn('ADR-001',text); self.assertIn('security-sensitive-change',text); self.assertIn('critical path',text)

    def test_compiler_carries_only_previous_completion_record(self):
        with tempfile.TemporaryDirectory() as d:
            dst=Path(d)/'r'; shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('dist','__pycache__'))
            prev=dst/'docs/phases/00-foundation.md'
            prev.write_text(
                '# Phase 00 — Foundation\n\n'
                '## Goal\nOld goal\n\n'
                '## Tasks\n- [x] SECRET OLD TASK BODY SHOULD NOT LOAD\n\n'
                '## Completion Record\n'
                '### Delivered\n- Auth and schema operational.\n\n'
                '### Validation Evidence\n- build → PASS\n\n'
                '### Handoff to Next Phase\n- Phase 01 may rely on authenticated project ownership.\n'
            )
            cur=dst/'docs/phases/01-assets.md'
            cur.write_text('# Phase 01 — Assets\n\n## Goal\nShip asset upload\n')
            (dst/'docs/project/ROADMAP.md').write_text(
                '# Roadmap\n'
                '- [x] Foundation `docs/phases/00-foundation.md`\n'
                '- [>] Assets `docs/phases/01-assets.md`\n'
            )
            text=build(dst)
            self.assertIn('Previous phase completion bridge',text)
            self.assertIn('Auth and schema operational',text)
            self.assertIn('authenticated project ownership',text)
            self.assertNotIn('SECRET OLD TASK BODY SHOULD NOT LOAD',text)

    def test_large_manifest_file_becomes_pointer(self):
        with tempfile.TemporaryDirectory() as d:
            dst=Path(d)/'r'; shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('dist','__pycache__'))
            big=dst/'big.txt'; big.write_text('x'*5000)
            m=json.loads((dst/'docs/project/CONTEXT_MANIFEST.json').read_text()); m['default']['required']=['big.txt']; (dst/'docs/project/CONTEXT_MANIFEST.json').write_text(json.dumps(m))
            self.assertIn('POINTER ONLY',build(dst,max_extra_chars=1000))

    def test_manifest_absolute_path_is_rejected_not_read(self):
        with tempfile.TemporaryDirectory() as d:
            dst=Path(d)/'r'; shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('dist','__pycache__'))
            secret=Path(d)/'outside-secret.txt'; secret.write_text('SUPER SECRET VALUE')
            m=json.loads((dst/'docs/project/CONTEXT_MANIFEST.json').read_text()); m['default']['required']=[str(secret)]; (dst/'docs/project/CONTEXT_MANIFEST.json').write_text(json.dumps(m))
            text=build(dst)
            self.assertNotIn('SUPER SECRET VALUE',text)
            self.assertIn('REJECTED',text)

    def test_manifest_parent_traversal_is_rejected_not_read(self):
        with tempfile.TemporaryDirectory() as d:
            dst=Path(d)/'r'; shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('dist','__pycache__'))
            secret=Path(d)/'outside-secret.txt'; secret.write_text('SUPER SECRET VALUE')
            m=json.loads((dst/'docs/project/CONTEXT_MANIFEST.json').read_text()); m['default']['required']=['../outside-secret.txt']; (dst/'docs/project/CONTEXT_MANIFEST.json').write_text(json.dumps(m))
            text=build(dst)
            self.assertNotIn('SUPER SECRET VALUE',text)
            self.assertIn('REJECTED',text)

    def test_manifest_required_file_count_is_capped(self):
        with tempfile.TemporaryDirectory() as d:
            dst=Path(d)/'r'; shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('dist','__pycache__'))
            names=[]
            for i in range(20):
                fn=f'extra{i}.txt'; (dst/fn).write_text(f'content {i}'); names.append(fn)
            m=json.loads((dst/'docs/project/CONTEXT_MANIFEST.json').read_text()); m['default']['required']=names; (dst/'docs/project/CONTEXT_MANIFEST.json').write_text(json.dumps(m))
            text=build(dst)
            self.assertIn('additional manifest-required file(s) omitted',text)
            self.assertNotIn('extra19.txt',text)

    def test_manifest_total_chars_budget_is_enforced(self):
        with tempfile.TemporaryDirectory() as d:
            dst=Path(d)/'r'; shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('dist','__pycache__'))
            names=[]
            for i in range(10):
                fn=f'chunk{i}.txt'; (dst/fn).write_text('y'*3000); names.append(fn)
            m=json.loads((dst/'docs/project/CONTEXT_MANIFEST.json').read_text()); m['default']['required']=names; (dst/'docs/project/CONTEXT_MANIFEST.json').write_text(json.dumps(m))
            text=build(dst,max_extra_chars=4000)
            self.assertIn('manifest total-context budget',text)

    def test_roadmap_phase_traversal_path_is_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            dst=Path(d)/'r'; shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('dist','__pycache__'))
            secret=dst.parent/'outside-phase-secret.md'; secret.write_text('PHASE SECRET SHOULD NOT LOAD')
            (dst/'docs/project/ROADMAP.md').write_text('# Roadmap\n- [>] Escape `docs/phases/../../../outside-phase-secret.md`\n')
            text=build(dst)
            self.assertNotIn('PHASE SECRET SHOULD NOT LOAD',text)

if __name__=='__main__': unittest.main()
