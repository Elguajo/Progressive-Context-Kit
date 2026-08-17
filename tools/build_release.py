#!/usr/bin/env python3
"""Build and verify the user-facing Project Runtime from canonical Framework Source.

This is the release entrypoint. Framework Source is the only editable source of
truth; Project Runtime is disposable generated output under dist/.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile


def run(root: Path, *args: str) -> None:
    cmd = [sys.executable, *args]
    print("+", " ".join(str(x) for x in cmd))
    result = subprocess.run(cmd, cwd=root)
    if result.returncode:
        raise SystemExit(result.returncode)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_commit(root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip() or None
    except (OSError, subprocess.CalledProcessError):
        return None


def verify_source(root: Path, run_unit_tests: bool) -> None:
    # Generated mirrors must already be synchronized. Release builds fail on
    # drift rather than mutating canonical Source silently.
    for script in [
        "tools/sync_profiles.py",
        "tools/sync_skills.py",
        "tools/behavior_contract.py",
        "tools/framework_contract.py",
        "tools/duplication_audit.py",
        "tools/audit.py",
    ]:
        run(root, script)

    if run_unit_tests:
        print("+", sys.executable, "-m unittest discover -s tools/tests -v")
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tools/tests", "-v"],
            cwd=root,
        )
        if result.returncode:
            raise SystemExit(result.returncode)


def build_runtime(root: Path, profile: str, agent: str) -> Path:
    run(root, "tools/build_runtime.py", "--profile", profile, "--agent", agent)
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    suffix = "" if profile == "standalone" else "-Personal"
    artifact = root / "dist" / f"Progressive-Context-Project-Runtime{suffix}-v{version}.zip"
    if not artifact.is_file():
        raise SystemExit(f"runtime artifact was not produced: {artifact}")
    return artifact


def verify_runtime(root: Path, artifact: Path) -> None:
    with zipfile.ZipFile(artifact) as zf:
        bad = zf.testzip()
        if bad:
            raise SystemExit(f"runtime ZIP integrity failure at {bad}")
        with tempfile.TemporaryDirectory(prefix="pc-runtime-") as tmp:
            zf.extractall(tmp)
            entries = [p for p in Path(tmp).iterdir() if p.is_dir()]
            if len(entries) != 1:
                raise SystemExit("runtime ZIP must contain exactly one top-level directory")
            runtime = entries[0]
            run(root, str(runtime / ".progressive/tools/audit.py"), "--root", str(runtime))
            run(root, str(runtime / ".progressive/tools/context_compile.py"), "--root", str(runtime))


def write_release_metadata(root: Path, artifact: Path, profile: str, agent: str) -> tuple[Path, Path]:
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    digest = sha256_file(artifact)
    manifest = {
        "schema": 1,
        "artifact": artifact.name,
        "version": version,
        "profile": profile,
        "agent_target": agent,
        "source_of_truth": "Framework Source",
        "generated": True,
        "source_commit": git_commit(root),
        "sha256": digest,
        "size_bytes": artifact.stat().st_size,
        "validation": {
            "source_contracts": True,
            "source_audit": True,
            "runtime_audit": True,
            "runtime_context_compile": True,
        },
    }
    manifest_path = artifact.with_suffix(".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    checksums = root / "dist" / "SHA256SUMS.txt"
    checksums.write_text(f"{digest}  {artifact.name}\n", encoding="utf-8")
    return manifest_path, checksums


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Verify Framework Source and generate the Project Runtime release artifact."
    )
    ap.add_argument("--profile", choices=["standalone", "personal"], default="standalone")
    ap.add_argument("--agent", choices=["codex", "claude", "both"], default="both")
    ap.add_argument(
        "--skip-unit-tests",
        action="store_true",
        help="Skip unittest discovery. Intended only for the release-builder unit test or local iteration.",
    )
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]
    verify_source(root, run_unit_tests=not args.skip_unit_tests)
    artifact = build_runtime(root, args.profile, args.agent)
    verify_runtime(root, artifact)
    manifest, checksums = write_release_metadata(root, artifact, args.profile, args.agent)

    print("RELEASE BUILD: PASS")
    print(f"Artifact: {artifact}")
    print(f"Manifest: {manifest}")
    print(f"Checksums: {checksums}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
