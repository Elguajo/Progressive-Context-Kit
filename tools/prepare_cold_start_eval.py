#!/usr/bin/env python3
"""Prepare fresh Project Runtime repositories for cold-start transfer evaluation.

The script builds disposable eval repos only. It never invokes Codex or Claude and never
packages cold-start oracle/eval infrastructure into Project Runtime.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from agent_benchmark_fixtures import materialize_fixture
from runtime_layout import write_runtime

ROOT = Path(__file__).resolve().parents[1]
COLD_START_ROOT = ROOT / "docs/evals/agent/cold-start"
DEFAULT_OUTPUT = ROOT / "dist/agent-eval/cold-start-runtime-transfer-v1"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts):
        rel = path.relative_to(root).as_posix()
        digest.update(rel.encode("utf-8") + b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def current_git_ref(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True
    )
    if result.returncode:
        raise RuntimeError("cold-start preparation requires a Git checkout")
    return result.stdout.strip()


def working_tree_clean(root: Path) -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True
    )
    if result.returncode:
        raise RuntimeError("cannot inspect Git working tree")
    return not result.stdout.strip()


def init_clean_git_repo(root: Path) -> str:
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": "Progressive Cold Start Eval",
            "GIT_AUTHOR_EMAIL": "cold-start@example.invalid",
            "GIT_COMMITTER_NAME": "Progressive Cold Start Eval",
            "GIT_COMMITTER_EMAIL": "cold-start@example.invalid",
            "GIT_AUTHOR_DATE": "2026-08-25T00:00:00+00:00",
            "GIT_COMMITTER_DATE": "2026-08-25T00:00:00+00:00",
        }
    )
    for command in (
        ["git", "init", "-q"],
        ["git", "add", "-A"],
        ["git", "commit", "-q", "-m", "cold-start eval fixture"],
    ):
        result = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(f"{' '.join(command)} failed: {result.stderr.strip()}")
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def set_minimal_tooling(repo: Path) -> None:
    project = repo / ".progressive/project"
    status_path = project / "TOOLING_STATUS.json"
    if status_path.is_file():
        data = load_json(status_path)
        data["profile"] = "minimal"
        data["last_bootstrap"] = None
        for entry in data.get("tools", {}).values():
            entry["status"] = "not_applicable"
            entry["checked_at"] = None
            entry["version"] = None
            entry["evidence"] = "optional framework tool intentionally excluded from cold-start eval"
            entry["notes"] = None
        status_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    md = project / "TOOLING_STATUS.md"
    if md.is_file():
        md.write_text(
            "# Tooling Status\n\n"
            "Profile: minimal\n\n"
            "Status: READY\n\n"
            "Optional framework tooling is intentionally not applicable to this controlled "
            "cold-start evaluation. Use repository-native tools only.\n",
            encoding="utf-8",
        )


def write_active_state(repo: Path, scenario: dict, *, continuation: bool = False) -> None:
    project = repo / ".progressive/project"
    phases = repo / ".progressive/phases"
    project.mkdir(parents=True, exist_ok=True)
    phases.mkdir(parents=True, exist_ok=True)
    focus = scenario.get("continuation_focus") if continuation else None

    (project / "PROJECT_BRIEF.md").write_text(
        "# Project Brief\n\n"
        "Status: ACTIVE\n\n"
        "Project: Cold-start transfer fixture\n\n"
        "Goal: Preserve the current Python service and complete approved repository work "
        "without unrelated scope.\n",
        encoding="utf-8",
    )
    (project / "ARCHITECTURE.md").write_text(
        "# Architecture\n\n"
        "Status: ACTIVE\n\n"
        "Runtime: Python 3.11+ standard library.\n\n"
        "Layout: application code under `src/`, tests under `tests/`, repository-local tools "
        "under `tools/` when present. Preserve existing public behavior unless the user task "
        "explicitly changes it.\n",
        encoding="utf-8",
    )
    (project / "ROADMAP.md").write_text(
        "# Roadmap — Cold-Start Fixture\n\n"
        "Legend: `[ ] PLANNED` · `[>] IN PROGRESS` · `[x] COMPLETE`\n\n"
        "- [>] Phase 00 — Current work — `.progressive/phases/00-current.md`\n",
        encoding="utf-8",
    )
    phase_goal = focus or "Complete the current user-requested repository task correctly and narrowly."
    (phases / "00-current.md").write_text(
        "# Phase 00 — Current Work\n\n"
        "Status: IN PROGRESS\n\n"
        "## Goal\n\n"
        f"{phase_goal}\n\n"
        "## Acceptance\n\n"
        "- Preserve unrelated behavior.\n"
        "- Use repository-supported validation and report evidence truthfully.\n",
        encoding="utf-8",
    )
    if continuation:
        (project / "NEXT_SESSION.md").write_text(
            "# Next Session\n\n"
            "> Volatile hot context for the current unresolved target.\n\n"
            "Status: READY\n\n"
            f"Current focus: {focus}\n\n"
            f"Next action: {focus}\n",
            encoding="utf-8",
        )
    else:
        (project / "NEXT_SESSION.md").write_text(
            "# Next Session\n\n"
            "> Volatile hot context.\n\n"
            "Status: READY\n\n"
            "Current focus: Continue the active phase from repository evidence and the current "
            "user request.\n",
            encoding="utf-8",
        )
    (repo / ".progressive/ADOPTION_STATE").write_text("ready\n", encoding="utf-8")


def write_completed_state(repo: Path) -> None:
    project = repo / ".progressive/project"
    phases = repo / ".progressive/phases"
    project.mkdir(parents=True, exist_ok=True)
    phases.mkdir(parents=True, exist_ok=True)
    (project / "PROJECT_BRIEF.md").write_text(
        "# Project Brief\n\nStatus: ACTIVE\n\nProject: Cold-start completed-roadmap fixture.\n",
        encoding="utf-8",
    )
    (project / "ARCHITECTURE.md").write_text(
        "# Architecture\n\nStatus: ACTIVE\n\nRuntime: Python 3.11+ standard library.\n",
        encoding="utf-8",
    )
    (project / "ROADMAP.md").write_text(
        "# Roadmap — Completed Fixture\n\n"
        "Legend: `[ ] PLANNED` · `[>] IN PROGRESS` · `[x] COMPLETE`\n\n"
        "- [x] Phase 00 — Initial service — `.progressive/phases/00-complete.md`\n",
        encoding="utf-8",
    )
    (phases / "00-complete.md").write_text(
        "# Phase 00 — Initial Service\n\n"
        "Status: COMPLETE\n\n"
        "## Completion Record\n\n"
        "Result: Existing service baseline completed and validated.\n\n"
        "Evidence: Existing repository tests passed at completion.\n",
        encoding="utf-8",
    )
    (project / "NEXT_SESSION.md").write_text(
        "# Next Session\n\nStatus: COMPLETE\n\nCurrent focus: No unresolved work.\n",
        encoding="utf-8",
    )
    (repo / ".progressive/ADOPTION_STATE").write_text("ready\n", encoding="utf-8")


def configure_state(repo: Path, scenario: dict) -> None:
    setup = scenario["setup"]
    set_minimal_tooling(repo)
    if setup == "greenfield":
        return
    if setup == "adoption-pending":
        (repo / ".progressive/ADOPTION_STATE").write_text("pending\n", encoding="utf-8")
        return
    if setup == "active":
        write_active_state(repo, scenario)
        return
    if setup == "active-continuation":
        write_active_state(repo, scenario, continuation=True)
        return
    if setup == "completed":
        write_completed_state(repo)
        return
    raise ValueError(f"unknown cold-start setup: {setup}")


def materialize_scenario_repo(source_root: Path, scenario: dict, destination: Path, agent: str = "both") -> None:
    fixture = scenario.get("fixture")
    if fixture:
        materialize_fixture(fixture, destination)
    else:
        destination.mkdir(parents=True, exist_ok=True)
    write_runtime(source_root, destination, profile="standalone", agent=agent)
    configure_state(destination, scenario)


def prepare_pack(
    output: Path,
    workflow_ref: str,
    agent: str = "both",
    selected: set[str] | None = None,
) -> dict:
    data = load_json(COLD_START_ROOT / "SCENARIOS.json")
    scenarios = data["scenarios"]
    known = {scenario["id"] for scenario in scenarios}
    if selected:
        unknown = selected - known
        if unknown:
            raise ValueError("unknown scenario id(s): " + ", ".join(sorted(unknown)))
        scenarios = [scenario for scenario in scenarios if scenario["id"] in selected]

    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    plan = {
        "schema": 1,
        "suite_id": data["suite_id"],
        "workflow_ref": workflow_ref,
        "profile": "standalone",
        "agent_target": agent,
        "cases": [],
    }

    for scenario in scenarios:
        case_dir = output / "scenarios" / scenario["id"]
        repo = case_dir / "repo"
        materialize_scenario_repo(ROOT, scenario, repo, agent=agent)
        prompt = case_dir / "prompt.md"
        prompt.parent.mkdir(parents=True, exist_ok=True)
        prompt.write_text(scenario["prompt"].strip() + "\n", encoding="utf-8")
        oracle = case_dir / "oracle.json"
        oracle.write_text(
            json.dumps(
                {
                    "schema": 1,
                    "suite_id": data["suite_id"],
                    "scenario_id": scenario["id"],
                    "oracle": scenario["oracle"],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        snapshot = tree_digest(repo)
        local_commit = init_clean_git_repo(repo)
        plan["cases"].append(
            {
                "scenario_id": scenario["id"],
                "prompt": str(prompt.relative_to(output)),
                "oracle": str(oracle.relative_to(output)),
                "repo": str(repo.relative_to(output)),
                "prompt_sha256": sha256_file(prompt),
                "repo_snapshot": snapshot,
                "local_git_commit": local_commit,
            }
        )

    (output / "RUN_PLAN.json").write_text(
        json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return plan


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare Progressive cold-start transfer eval repos.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--agent", choices=["codex", "claude", "both"], default="both")
    parser.add_argument("--scenario", action="append", dest="scenarios")
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Allow preparing from a dirty working tree. The recorded workflow ref then does not fully identify the source contents.",
    )
    args = parser.parse_args()
    try:
        ref = current_git_ref(ROOT)
        if not args.allow_dirty and not working_tree_clean(ROOT):
            raise RuntimeError("working tree is dirty; commit changes first or use --allow-dirty for exploratory runs")
        plan = prepare_pack(
            Path(args.output).resolve(),
            ref,
            agent=args.agent,
            selected=set(args.scenarios or []) or None,
        )
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print("COLD-START EVAL PACK: READY")
    print(f"Output: {Path(args.output).resolve()}")
    print(f"Workflow ref: {plan['workflow_ref']}")
    print(f"Scenarios: {len(plan['cases'])}")
    print("Next: start one fresh agent session per case and send only prompt.md as the initial user message.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
