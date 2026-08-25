#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

RELEASE_VERSION_DOCS = [
    'README.md',
    'README_RU.md',
    'docs/human/GETTING_STARTED.md',
    'docs/human/GETTING_STARTED.ru.md',
]
RUNTIME_REF_RE = re.compile(r'Progressive-Context-Project-Runtime-v\d+\.\d+\.\d+')
SEMVER_RE = re.compile(r'^\d+\.\d+\.\d+$')


def prepare(root: Path, version: str, notes_file: Path) -> list[str]:
    root = root.resolve()
    if not SEMVER_RE.fullmatch(version):
        raise ValueError(f'version must be stable SemVer X.Y.Z, got {version!r}')

    notes_path = notes_file if notes_file.is_absolute() else root / notes_file
    if not notes_path.is_file():
        raise FileNotFoundError(f'release notes not found: {notes_path}')
    notes = notes_path.read_text(encoding='utf-8').strip()
    expected_heading = f'## {version} — '
    if not notes.startswith(expected_heading):
        raise ValueError(
            f'release notes must start with {expected_heading!r}; got {notes.splitlines()[0] if notes else "<empty>"!r}'
        )

    changed: list[str] = []

    version_path = root / 'VERSION'
    desired_version = version + '\n'
    if version_path.read_text(encoding='utf-8') != desired_version:
        version_path.write_text(desired_version, encoding='utf-8')
        changed.append('VERSION')

    replacement = f'Progressive-Context-Project-Runtime-v{version}'
    for rel in RELEASE_VERSION_DOCS:
        path = root / rel
        text = path.read_text(encoding='utf-8')
        updated, count = RUNTIME_REF_RE.subn(replacement, text)
        if count == 0:
            raise ValueError(f'{rel} has no Project Runtime version reference to update')
        if updated != text:
            path.write_text(updated, encoding='utf-8')
            changed.append(rel)

    changelog_path = root / 'CHANGELOG.md'
    changelog = changelog_path.read_text(encoding='utf-8')
    marker = f'## {version} — '
    if marker in changelog:
        if notes not in changelog:
            raise ValueError(f'CHANGELOG.md already contains {marker!r} but does not match the release notes')
    else:
        prefix = '# Changelog\n\n'
        if not changelog.startswith(prefix):
            raise ValueError('CHANGELOG.md must start with "# Changelog"')
        changelog = prefix + notes + '\n\n' + changelog[len(prefix):]
        changelog_path.write_text(changelog, encoding='utf-8')
        changed.append('CHANGELOG.md')

    return changed


def main() -> int:
    ap = argparse.ArgumentParser(description='Prepare a Progressive Context release commit deterministically.')
    ap.add_argument('--version', required=True, help='Stable SemVer without leading v, e.g. 2.0.0')
    ap.add_argument('--notes-file', required=True, help='Markdown section beginning with "## X.Y.Z — YYYY-MM-DD"')
    ap.add_argument('--root', default='.')
    args = ap.parse_args()

    root = Path(args.root)
    try:
        changed = prepare(root, args.version, Path(args.notes_file))
    except (OSError, ValueError) as exc:
        print(f'RELEASE PREPARE: FAIL ({exc})')
        return 1

    if changed:
        print('RELEASE PREPARE: UPDATED ' + ', '.join(changed))
    else:
        print('RELEASE PREPARE: PASS (already prepared)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
