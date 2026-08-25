#!/usr/bin/env python3
"""Run the canonical Progressive Context Kit Framework Source verification gate.

This is an orchestration entrypoint only. Individual contracts/audits remain independently
executable and keep ownership of their own validation logic.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys

BASELINE_CHARS = 11540


@dataclass(frozen=True)
class Check:
    id: str
    label: str
    args: tuple[str, ...]


def source_checks(run_unit_tests: bool = True) -> tuple[Check, ...]:
    checks = [
        Check("profile-mirrors", "Profile mirrors", ("tools/sync_profiles.py",)),
        Check("skill-mirrors", "Skill mirrors", ("tools/sync_skills.py",)),
        Check("behavior-contract", "Behavior Contract", ("tools/behavior_contract.py",)),
        Check("framework-contract", "Framework Contract + invariants", ("tools/framework_contract.py",)),
        Check("tool-adapter-protocol", "Tool Adapter Protocol", ("tools/tool_adapter_protocol.py",)),
        Check("routing-integrity", "Routing Integrity", ("tools/routing_integrity.py",)),
        Check("autoresearch-records", "Autoresearch record integrity", ("tools/autoresearch.py", "validate")),
        Check("duplication-audit", "Duplication audit", ("tools/duplication_audit.py",)),
        Check("source-audit", "Framework Source audit", ("tools/audit.py",)),
        Check(
            "context-report",
            "Context budget report",
            (
                "tools/context_report.py",
                "--profile",
                "personal",
                "--baseline-chars",
                str(BASELINE_CHARS),
            ),
        ),
    ]
    if run_unit_tests:
        checks.append(
            Check(
                "unit-tests",
                "Framework unit/regression tests",
                ("-m", "unittest", "discover", "-s", "tools/tests", "-v"),
            )
        )
    return tuple(checks)


def ensure_framework_source(root: Path) -> list[str]:
    required = (
        root / "docs/contracts/FRAMEWORK_CONTRACT.json",
        root / "profiles/personal/AGENTS.md",
        root / "tools/audit.py",
        root / "tools/framework_contract.py",
    )
    return [str(path.relative_to(root)) for path in required if not path.is_file()]


def run_gate(root: Path, *, run_unit_tests: bool = True) -> int:
    root = root.resolve()
    missing = ensure_framework_source(root)
    if missing:
        print("ERROR: Progressive Gate must run against Framework Source.", flush=True)
        for path in missing:
            print(f"MISSING: {path}", flush=True)
        print(
            "Project Runtime uses .progressive/tools/audit.py and task-relevant validation instead.",
            flush=True,
        )
        print("PROGRESSIVE GATE: FAIL (wrong verification surface)", flush=True)
        return 2

    checks = source_checks(run_unit_tests)
    total = len(checks)
    passed = 0
    for index, check in enumerate(checks, 1):
        print(f"\n[{index}/{total}] {check.label}", flush=True)
        command = [sys.executable, *check.args]
        print("+", " ".join(command), flush=True)
        result = subprocess.run(command, cwd=root)
        if result.returncode:
            print(
                f"PROGRESSIVE GATE: FAIL ({passed}/{total} checks passed; "
                f"failed: {check.id})",
                flush=True,
            )
            return result.returncode
        passed += 1

    print(f"\nPROGRESSIVE GATE: PASS ({passed}/{total} checks)", flush=True)
    print(
        "Scope: Framework Source static/integrity verification only; not empirical model-quality proof.",
        flush=True,
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the canonical Progressive Context Kit Framework Source gate."
    )
    parser.add_argument("--root", default=".", help="Framework Source repository root.")
    parser.add_argument(
        "--skip-unit-tests",
        action="store_true",
        help="Skip unittest discovery. Intended for nested release-builder tests/local iteration only.",
    )
    args = parser.parse_args()
    return run_gate(Path(args.root), run_unit_tests=not args.skip_unit_tests)


if __name__ == "__main__":
    raise SystemExit(main())
