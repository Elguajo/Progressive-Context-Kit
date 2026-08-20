#!/usr/bin/env python3
"""Prepare paired real-agent benchmark repos from immutable workflow refs.

The script builds disposable task repos only; it never invokes Codex or Claude.
Benchmark/eval infrastructure stays Framework Source-only.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile

from agent_benchmark_fixtures import fixture_digest, materialize_fixture

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_ROOT = ROOT / "docs/evals/agent/benchmark"
OPTIONAL_FRAMEWORK_TOOLS = (
    "semble",
    "serena",
    "rtk",
    "superpowers",
    "gstack",
    "context7",
    "github_spec_kit",
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def export_git_ref(repo: Path, ref: str, destination: Path) -> None:
    result = subprocess.run(
        ["git", "archive", "--format=tar", ref],
        cwd=repo,
        capture_output=True,
    )
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(
            f"cannot export workflow ref {ref}: {detail or 'git archive failed'}. "
            "Fetch the full repository history and retry."
        )

    destination.mkdir(parents=True, exist_ok=True)
    resolved_root = destination.resolve()
    with tarfile.open(fileobj=io.BytesIO(result.stdout), mode="r:") as archive:
        for member in archive.getmembers():
            target = (destination / member.name).resolve()
            if target != resolved_root and resolved_root not in target.parents:
                raise RuntimeError(f"unsafe archive path: {member.name}")
        archive.extractall(destination)


def build_runtime_from_ref(repo: Path, ref: str, agent_target: str, destination: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="pc-benchmark-workflow-") as tmp:
        exported = Path(tmp) / "source"
        export_git_ref(repo, ref, exported)
        result = subprocess.run(
            [
                sys.executable,
                str(exported / "tools/build_runtime.py"),
                "--profile",
                "standalone",
                "--agent",
                agent_target,
            ],
            cwd=exported,
            capture_output=True,
            text=True,
        )
        if result.returncode:
            raise RuntimeError(
                f"runtime build failed for {ref}:\n{result.stdout}\n{result.stderr}".strip()
            )

        artifacts = sorted((exported / "dist").glob("Progressive-Context-Project-Runtime-v*.zip"))
        if len(artifacts) != 1:
            raise RuntimeError(
                f"expected one standalone runtime artifact for {ref}, found {len(artifacts)}"
            )

        with zipfile.ZipFile(artifacts[0]) as archive:
            names = archive.namelist()
            top = {name.split("/", 1)[0] for name in names if name}
            if len(top) != 1:
                raise RuntimeError(f"runtime artifact for {ref} must have one top-level directory")
            prefix = next(iter(top)).rstrip("/") + "/"
            for name in names:
                if name == prefix or not name.startswith(prefix):
                    continue
                rel = name[len(prefix):]
                if not rel:
                    continue
                target = destination / rel
                if name.endswith("/"):
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(archive.read(name))


def init_clean_git_repo(root: Path) -> str:
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": "Progressive Benchmark",
            "GIT_AUTHOR_EMAIL": "benchmark@example.invalid",
            "GIT_COMMITTER_NAME": "Progressive Benchmark",
            "GIT_COMMITTER_EMAIL": "benchmark@example.invalid",
            "GIT_AUTHOR_DATE": "2026-08-20T00:00:00+00:00",
            "GIT_COMMITTER_DATE": "2026-08-20T00:00:00+00:00",
        }
    )
    for command in (
        ["git", "init", "-q"],
        ["git", "add", "-A"],
        ["git", "commit", "-q", "-m", "benchmark fixture"],
    ):
        result = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(f"{' '.join(command)} failed: {result.stderr.strip()}")
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def copy_runtime(source: Path, repo: Path) -> None:
    for path in source.rglob("*"):
        rel = path.relative_to(source)
        target = repo / rel
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def benchmark_tooling_state() -> dict:
    return {
        "schema": 1,
        "profile": "minimal",
        "last_bootstrap": None,
        "tools": {
            key: {
                "status": "not_applicable",
                "checked_at": None,
                "version": None,
                "evidence": "optional framework tool intentionally excluded from controlled benchmark",
                "notes": None,
            }
            for key in OPTIONAL_FRAMEWORK_TOOLS
        },
    }


def initialize_benchmark_project(repo: Path, task_id: str) -> None:
    """Replace uninitialized Runtime seeds with identical minimal active state in both arms."""
    project = repo / ".progressive/project"
    phases = repo / ".progressive/phases"
    project.mkdir(parents=True, exist_ok=True)
    phases.mkdir(parents=True, exist_ok=True)

    (project / "PROJECT_BRIEF.md").write_text(
        "# Project Brief\n\n"
        "Status: ACTIVE\n\n"
        "Project: Real-agent benchmark fixture\n\n"
        "Goal: Complete the current user-provided local coding task correctly and with the "
        "smallest complete change.\n\n"
        "Scope: The current repository and current task only. Do not expand product scope.\n",
        encoding="utf-8",
    )
    (project / "ARCHITECTURE.md").write_text(
        "# Architecture\n\n"
        "Status: ACTIVE\n\n"
        "Runtime: Python 3.11+ standard library.\n\n"
        "Layout: application code under `src/`, unittest-based tests under `tests/`, and local "
        "helper commands under `tools/` when present.\n\n"
        "Constraint: Preserve repository-local conventions; add no third-party dependency unless "
        "the user task explicitly requires one.\n",
        encoding="utf-8",
    )
    (project / "ROADMAP.md").write_text(
        "# Roadmap — Benchmark Fixture\n\n"
        "Legend: `[ ] PLANNED` · `[>] IN PROGRESS` · `[x] COMPLETE`\n\n"
        "- [>] Phase 00 — Current coding task — `.progressive/phases/00-benchmark-task.md`\n\n"
        "Project complete when the current user task and its supplied acceptance criteria are "
        "verified.\n",
        encoding="utf-8",
    )
    (project / "NEXT_SESSION.md").write_text(
        "# Next Session\n\n"
        "> Volatile hot context for this disposable benchmark fixture.\n\n"
        "Status: READY\n\n"
        f"Current focus: Execute benchmark task `{task_id}` exactly as supplied by the user.\n\n"
        "Next action: Ground in the repository, implement the task, and produce required "
        "validation evidence.\n",
        encoding="utf-8",
    )
    (phases / "00-benchmark-task.md").write_text(
        "# Phase 00 — Current Coding Task\n\n"
        "Status: IN PROGRESS\n\n"
        "## Goal\n\n"
        "Complete the exact current user-provided task without unrelated scope.\n\n"
        "## Acceptance\n\n"
        "Use the acceptance criteria supplied with the user task and the repository's required "
        "validation evidence.\n",
        encoding="utf-8",
    )

    tooling_json = project / "TOOLING_STATUS.json"
    if tooling_json.exists():
        tooling_json.write_text(
            json.dumps(benchmark_tooling_state(), indent=2) + "\n",
            encoding="utf-8",
        )
    tooling_md = project / "TOOLING_STATUS.md"
    if tooling_md.exists():
        tooling_md.write_text(
            "# Tooling Status\n\n"
            "Profile: minimal\n\n"
            "Status: READY\n\n"
            "Optional framework tooling is intentionally not applicable to this controlled "
            "benchmark. Use repository-native tools only.\n",
            encoding="utf-8",
        )


def write_task_material(task_dir: Path, task: dict) -> tuple[Path, Path]:
    prompt = task_dir / "prompt.md"
    acceptance = task_dir / "acceptance.md"
    task_dir.mkdir(parents=True, exist_ok=True)
    prompt.write_text(task["prompt"].strip() + "\n", encoding="utf-8")
    acceptance.write_text(
        "# Acceptance criteria\n\n"
        + "\n".join(f"- {item}" for item in task["acceptance"])
        + "\n",
        encoding="utf-8",
    )
    return prompt, acceptance


def prepare_pack(
    output: Path,
    repetitions: int,
    selected_tasks: set[str] | None = None,
) -> dict:
    experiment = load_json(BENCHMARK_ROOT / "EXPERIMENT.json")
    tasks = load_json(BENCHMARK_ROOT / "TASKS.json")["tasks"]

    if selected_tasks:
        known = {task["id"] for task in tasks}
        unknown = selected_tasks - known
        if unknown:
            raise ValueError("unknown task id(s): " + ", ".join(sorted(unknown)))
        tasks = [task for task in tasks if task["id"] in selected_tasks]

    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    plan = {
        "schema": 1,
        "experiment_id": experiment["experiment_id"],
        "baseline_workflow_ref": experiment["baseline_workflow_ref"],
        "candidate_workflow_ref": experiment["candidate_workflow_ref"],
        "repetitions": repetitions,
        "pairs": [],
    }

    with tempfile.TemporaryDirectory(prefix="pc-benchmark-runtime-") as runtime_tmp:
        runtime_cache: dict[str, Path] = {}
        for arm in ("baseline", "candidate"):
            runtime_dir = Path(runtime_tmp) / arm
            runtime_dir.mkdir(parents=True)
            build_runtime_from_ref(
                ROOT,
                experiment[f"{arm}_workflow_ref"],
                experiment.get("agent_target", "both"),
                runtime_dir,
            )
            runtime_cache[arm] = runtime_dir

        for task in tasks:
            with tempfile.TemporaryDirectory(prefix=f"pc-fixture-{task['id']}-") as fixture_tmp:
                raw = Path(fixture_tmp) / "repo"
                materialize_fixture(task["fixture"], raw)
                fixture_snapshot = fixture_digest(raw)

                task_dir = output / "tasks" / task["id"]
                prompt_path, acceptance_path = write_task_material(task_dir, task)
                task_sha256 = sha256_file(prompt_path)
                acceptance_sha256 = sha256_file(acceptance_path)

                for repetition in range(1, repetitions + 1):
                    pair_id = f"{task['id']}-r{repetition:02d}"
                    pair = {
                        "pair_id": pair_id,
                        "task_id": task["id"],
                        "task_class": task["task_class"],
                        "mechanism": task["mechanism"],
                        "fixture_snapshot": fixture_snapshot,
                        "task_sha256": task_sha256,
                        "acceptance_sha256": acceptance_sha256,
                        "prompt": str(prompt_path.relative_to(output)),
                        "acceptance": str(acceptance_path.relative_to(output)),
                        "arms": {},
                    }
                    for arm in ("baseline", "candidate"):
                        repo_dir = task_dir / f"r{repetition:02d}" / arm / "repo"
                        shutil.copytree(raw, repo_dir)
                        copy_runtime(runtime_cache[arm], repo_dir)
                        initialize_benchmark_project(repo_dir, task["id"])
                        pair["arms"][arm] = {
                            "workflow_ref": experiment[f"{arm}_workflow_ref"],
                            "repo": str(repo_dir.relative_to(output)),
                            "local_git_commit": init_clean_git_repo(repo_dir),
                        }
                    plan["pairs"].append(pair)

    (output / "RUN_PLAN.json").write_text(
        json.dumps(plan, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return plan


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare paired Progressive Context real-agent benchmark repositories."
    )
    parser.add_argument(
        "--output",
        default=str(ROOT / "dist/agent-benchmark/execution-efficiency-v1"),
        help="Disposable benchmark-pack destination.",
    )
    parser.add_argument("--repetitions", type=int, default=None)
    parser.add_argument(
        "--task",
        action="append",
        dest="tasks",
        help="Prepare only this task id; repeatable.",
    )
    args = parser.parse_args()

    experiment = load_json(BENCHMARK_ROOT / "EXPERIMENT.json")
    repetitions = args.repetitions or int(experiment.get("default_repetitions", 1))
    if repetitions < 1:
        print("ERROR: --repetitions must be >= 1", file=sys.stderr)
        return 2

    try:
        plan = prepare_pack(
            Path(args.output).resolve(),
            repetitions,
            set(args.tasks or []) or None,
        )
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print("AGENT BENCHMARK PACK: READY")
    print(f"Output: {Path(args.output).resolve()}")
    print(f"Pairs: {len(plan['pairs'])}")
    print(f"Baseline: {plan['baseline_workflow_ref']}")
    print(f"Candidate: {plan['candidate_workflow_ref']}")
    print("Next: run identical agent/model/settings on each baseline/candidate pair.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
