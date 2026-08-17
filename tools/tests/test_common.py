import os, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from common import safe_join

class SafeJoinTests(unittest.TestCase):
    def test_rejects_absolute_path(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                safe_join(Path(d),'/etc/passwd')

    def test_rejects_parent_traversal(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'repo'; root.mkdir()
            (Path(d)/'secret.md').write_text('TOP SECRET')
            with self.assertRaises(ValueError):
                safe_join(root,'../secret.md')

    def test_rejects_symlink_escape(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'repo'; root.mkdir()
            (Path(d)/'secret.md').write_text('TOP SECRET')
            link=root/'escape.md'
            try:
                os.symlink(Path(d)/'secret.md',link)
            except (OSError, NotImplementedError):
                self.skipTest('symlinks unsupported on this platform')
            with self.assertRaises(ValueError):
                safe_join(root,'escape.md')

    def test_allows_normal_relative_path(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'repo'; root.mkdir()
            (root/'docs').mkdir()
            (root/'docs'/'ARCHITECTURE.md').write_text('x')
            self.assertTrue(safe_join(root,'docs/ARCHITECTURE.md').is_file())

    def test_rejects_empty_path(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                safe_join(Path(d),'')

if __name__=='__main__': unittest.main()
