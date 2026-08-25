import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class ReleaseWorkflowTests(unittest.TestCase):
    def test_release_branch_prepares_gates_tags_then_publishes(self):
        workflow = (ROOT / '.github/workflows/release.yml').read_text(encoding='utf-8')
        self.assertIn("- 'release/v*'", workflow)
        self.assertIn('python3 tools/prepare_release.py --version "$VERSION_FROM_BRANCH" --notes-file "$NOTES"', workflow)
        self.assertIn('python3 tools/gate.py', workflow)
        self.assertIn('git push origin "refs/tags/${TAG}"', workflow)
        self.assertIn("startsWith(github.ref, 'refs/heads/release/v')", workflow)
        self.assertIn('TAG_SHA="$(gh api "repos/${GITHUB_REPOSITORY}/git/ref/tags/${TAG}" --jq .object.sha)"', workflow)
        self.assertIn('Tag $TAG points at $TAG_SHA, not this run\'s verified commit', workflow)

    def test_normal_branch_dispatch_remains_build_only(self):
        workflow = (ROOT / '.github/workflows/release.yml').read_text(encoding='utf-8')
        self.assertIn('Build-only verification (no release ref, no publish)', workflow)
        self.assertIn("!startsWith(github.ref, 'refs/tags/') && !startsWith(github.ref, 'refs/heads/release/v')", workflow)

    def test_existing_tag_cannot_be_moved_to_another_commit(self):
        workflow = (ROOT / '.github/workflows/release.yml').read_text(encoding='utf-8')
        self.assertIn('EXISTING_SHA', workflow)
        self.assertIn('Tag $TAG already points at $EXISTING_SHA, not prepared commit $RELEASE_SHA.', workflow)
        self.assertNotIn('git tag -f', workflow)
        self.assertNotIn('git push --force', workflow)


if __name__ == '__main__':
    unittest.main()
