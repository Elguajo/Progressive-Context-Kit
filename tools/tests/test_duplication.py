import unittest, tempfile, shutil, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from duplication_audit import validate

class DuplicationTests(unittest.TestCase):
    def test_source_has_no_canonical_duplicate(self): self.assertEqual(validate(ROOT),[])
    def test_exact_long_duplicate_fails(self):
        with tempfile.TemporaryDirectory() as d:
            dst=Path(d)/'r'; shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('dist','__pycache__'))
            source=(dst/'global/AGENTS.codex.md').read_text().split('\n\n')[2]
            p=dst/'docs/system/QUALITY_PROTOCOL.md'; p.write_text(p.read_text()+'\n\n'+source+'\n')
            self.assertTrue(validate(dst))
if __name__=='__main__': unittest.main()
