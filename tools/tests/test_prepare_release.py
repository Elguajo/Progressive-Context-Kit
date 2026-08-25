import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
import sys
sys.path.insert(0, str(ROOT / 'tools'))

from prepare_release import RELEASE_VERSION_DOCS, prepare


class PrepareReleaseTests(unittest.TestCase):
    def make_fixture(self, root: Path):
        (root / 'VERSION').write_text('1.9.0\n', encoding='utf-8')
        (root / 'CHANGELOG.md').write_text('# Changelog\n\n## 1.9.0 — 2026-08-20\n\n- Old.\n', encoding='utf-8')
        for rel in RELEASE_VERSION_DOCS:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                'asset: Progressive-Context-Project-Runtime-v1.9.0.zip\n'
                'manifest: Progressive-Context-Project-Runtime-v1.9.0.manifest.json\n',
                encoding='utf-8',
            )
        notes = root / 'docs/releases/v2.0.0.md'
        notes.parent.mkdir(parents=True, exist_ok=True)
        notes.write_text('## 2.0.0 — 2026-08-25\n\n- Major release.\n', encoding='utf-8')
        return notes

    def test_prepare_updates_release_surface_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            notes = self.make_fixture(root)
            changed = prepare(root, '2.0.0', notes)
            self.assertIn('VERSION', changed)
            self.assertIn('CHANGELOG.md', changed)
            self.assertEqual((root / 'VERSION').read_text(encoding='utf-8'), '2.0.0\n')
            changelog = (root / 'CHANGELOG.md').read_text(encoding='utf-8')
            self.assertTrue(changelog.startswith('# Changelog\n\n## 2.0.0 — 2026-08-25'))
            self.assertEqual(changelog.count('## 2.0.0 —'), 1)
            for rel in RELEASE_VERSION_DOCS:
                text = (root / rel).read_text(encoding='utf-8')
                self.assertIn('Progressive-Context-Project-Runtime-v2.0.0', text)
                self.assertNotIn('Progressive-Context-Project-Runtime-v1.9.0', text)
            self.assertEqual(prepare(root, '2.0.0', notes), [])

    def test_prepare_rejects_notes_for_another_version(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            notes = self.make_fixture(root)
            notes.write_text('## 2.1.0 — 2026-08-25\n\n- Wrong version.\n', encoding='utf-8')
            with self.assertRaises(ValueError):
                prepare(root, '2.0.0', notes)

    def test_prepare_rejects_non_stable_semver(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            notes = self.make_fixture(root)
            with self.assertRaises(ValueError):
                prepare(root, '2.0', notes)


if __name__ == '__main__':
    unittest.main()
