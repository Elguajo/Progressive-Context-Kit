#!/usr/bin/env python3
"""Prepare paired real-agent benchmark repositories from immutable workflow refs.

The benchmark pack is Framework Source-only. It creates disposable repos under dist/
with the same task fixture in each arm and only the Progressive workflow differing.
It does not invoke Codex or Claude; real agent runs remain an explicit external step.
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
import textwrap
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_ROOT = ROOT / "docs/evals/agent/benchmark"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_file(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip("\n"), encoding="utf-8")


def python_test_prelude(package: str) -> str:
    return textwrap.dedent(
        f"""
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
        """
    ).lstrip("\n")


def build_recon_batch(root: Path) -> None:
    write_file(root, "pyproject.toml", """
        [project]
        name = "harbor-service"
        version = "2.4.1"
        requires-python = ">=3.11"
    """)
    write_file(root, "README.md", """
        # Harbor Service

        Commands are registered in `harbor.dispatcher`. Keep command implementations small and
        follow existing command modules. Run `python3 -m unittest discover -v` for validation.
    """)
    write_file(root, "src/harbor/__init__.py", "")
    write_file(root, "src/harbor/config.py", "MODE = \"safe\"\n")
    write_file(root, "src/harbor/meta.py", """
        from pathlib import Path
        import tomllib

        def project_metadata():
            root = Path(__file__).resolve().parents[2]
            return tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    """)
    write_file(root, "src/harbor/commands/__init__.py", "")
    write_file(root, "src/harbor/commands/ping.py", """
        def run():
            return {"ok": True}
    """)
    write_file(root, "src/harbor/commands/info.py", """
        from harbor.config import MODE
        from harbor.meta import project_metadata

        def run():
            meta = project_metadata()
            return {"service": meta["name"], "mode": MODE}
    """)
    write_file(root, "src/harbor/dispatcher.py", """
        from harbor.commands import info, ping

        COMMANDS = {
            "ping": ping.run,
            "info": info.run,
        }

        def dispatch(name):
            return COMMANDS[name]()
    """)
    prelude = python_test_prelude("harbor")
    write_file(root, "tests/test_existing.py", prelude + """
        import unittest
        from harbor.dispatcher import dispatch

        class ExistingCommandTests(unittest.TestCase):
            def test_ping(self):
                self.assertEqual(dispatch("ping"), {"ok": True})

            def test_info(self):
                self.assertEqual(dispatch("info"), {"service": "harbor-service", "mode": "safe"})
    """)
    write_file(root, "tests/test_status.py", prelude + """
        import unittest
        from harbor.dispatcher import dispatch

        class StatusCommandTests(unittest.TestCase):
            def test_status_uses_canonical_metadata(self):
                self.assertEqual(
                    dispatch("status"),
                    {"service": "harbor-service", "version": "2.4.1", "mode": "safe"},
                )
    """)


def build_keyhole_read(root: Path) -> None:
    write_file(root, "pyproject.toml", """
        [project]
        name = "catalog-core"
        version = "1.0.0"
        requires-python = ">=3.11"
    """)
    write_file(root, "README.md", """
        # Catalog Core

        The catalog data module is generated in large sections. Avoid unrelated edits.
        Validation: `python3 -m unittest discover -v`.
    """)
    write_file(root, "src/catalog/__init__.py", "")
    lines = ["# Generated catalog constants. Do not reformat unrelated entries.\n"]
    for i in range(1, 1301):
        lines.append(f'ITEM_{i:04d} = "catalog-item-{i:04d}"\n')
    lines.extend([
        "\n",
        "def normalize_sku(value: str) -> str:\n",
        "    return value.strip().upper()\n",
        "\n",
        "def catalog_size() -> int:\n",
        "    return 1300\n",
    ])
    write_file(root, "src/catalog/data.py", "".join(lines))
    prelude = python_test_prelude("catalog")
    write_file(root, "tests/test_catalog.py", prelude + """
        import unittest
        from catalog.data import catalog_size, normalize_sku

        class CatalogTests(unittest.TestCase):
            def test_normalize_sku_collapses_whitespace(self):
                self.assertEqual(normalize_sku("  ab  12 cd "), "AB-12-CD")

            def test_existing_compact_sku(self):
                self.assertEqual(normalize_sku("ab-12"), "AB-12")

            def test_generated_catalog_is_intact(self):
                self.assertEqual(catalog_size(), 1300)
    """)


def build_environment_probe(root: Path) -> None:
    write_file(root, "pyproject.toml", """
        [project]
        name = "slug-service"
        version = "0.3.0"
        requires-python = ">=3.11"
    """)
    write_file(root, "README.md", """
        # Slug Service

        Read `ENVIRONMENT.md` before implementation. No third-party packages are required.
    """)
    write_file(root, "ENVIRONMENT.md", """
        # Local toolchain

        Required prerequisites are all knowable before the first execution step:
        - Python 3.11+ (`python3 --version`)
        - Git (`git --version`)
        - local schema helper (`python3 tools/schema_probe.py --version`)

        Normal validation: `python3 -m unittest discover -v`.
    """)
    write_file(root, "tools/schema_probe.py", """
        import sys

        if "--version" in sys.argv:
            print("schema-probe 1.2.0")
            raise SystemExit(0)
        print("usage: schema_probe.py --version", file=sys.stderr)
        raise SystemExit(2)
    """)
    write_file(root, "src/slug_service/__init__.py", "")
    write_file(root, "src/slug_service/render.py", """
        import re

        def render_slug(value: str) -> str:
            # TODO: complete punctuation/whitespace normalization.
            return value.strip().lower()
    """)
    prelude = python_test_prelude("slug_service")
    write_file(root, "tests/test_render.py", prelude + """
        import unittest
        from slug_service.render import render_slug

        class RenderSlugTests(unittest.TestCase):
            def test_render_slug(self):
                self.assertEqual(
                    render_slug("  Hello, Progressive Context!  "),
                    "hello-progressive-context",
                )
    """)


def build_validation_convergence(root: Path) -> None:
    write_file(root, "pyproject.toml", """
        [project]
        name = "pricing-core"
        version = "1.1.0"
        requires-python = ">=3.11"
    """)
    write_file(root, "README.md", """
        # Pricing Core

        Focused and full unittest commands are the supported validation path. `tools/` also
        contains maintainer convenience wrappers; they are not additional release gates.
    """)
    write_file(root, "src/pricing/__init__.py", "")
    write_file(root, "src/pricing/core.py", """
        from decimal import Decimal, ROUND_HALF_UP

        CENT = Decimal("0.01")

        def tax_total(subtotal: Decimal, tax_percent: Decimal) -> Decimal:
            factor = Decimal("1") + (tax_percent / Decimal("100"))
            return (subtotal * factor).quantize(CENT, rounding=ROUND_HALF_UP)

        def net_total(subtotal: Decimal, discount_percent: Decimal) -> Decimal:
            raise NotImplementedError
    """)
    prelude = python_test_prelude("pricing")
    write_file(root, "tests/__init__.py", "")
    write_file(root, "tests/test_pricing.py", prelude + """
        import unittest
        from decimal import Decimal
        from pricing.core import net_total, tax_total

        class PricingTests(unittest.TestCase):
            def test_net_total(self):
                self.assertEqual(
                    net_total(Decimal("100.00"), Decimal("12.5")),
                    Decimal("87.50"),
                )

            def test_tax_total_regression(self):
                self.assertEqual(
                    tax_total(Decimal("100.00"), Decimal("5")),
                    Decimal("105.00"),
                )
    """)
    write_file(root, "tools/smoke.py", """
        import subprocess, sys
        raise SystemExit(subprocess.call([sys.executable, "-m", "unittest", "tests.test_pricing", "-v"]))
    """)
    write_file(root, "tools/deep_recheck.py", """
        import subprocess, sys
        raise SystemExit(subprocess.call([sys.executable, "-m", "unittest", "discover", "-v"]))
    """)


def build_failure_pivot(root: Path) -> None:
    write_file(root, "pyproject.toml", """
        [project]
        name = "checkout-core"
        version = "0.9.0"
        requires-python = ">=3.11"
    """)
    write_file(root, "README.md", """
        # Checkout Core

        Discount configuration is documented in `CONFIGURATION.md`.
        Validation: `python3 -m unittest discover -v`.
    """)
    write_file(root, "CONFIGURATION.md", """
        # Checkout configuration

        `discount` is a percentage string such as `10%`, `7.5%`, or `0%`.
    """)
    write_file(root, "src/checkout/__init__.py", "")
    write_file(root, "src/checkout/config.py", """
        from decimal import Decimal

        def parse_discount(value: str) -> Decimal:
            # Returns a fraction suitable for multiplication.
            return Decimal(value) / Decimal("100")
    """)
    write_file(root, "src/checkout/core.py", """
        from decimal import Decimal, InvalidOperation
        from checkout.config import parse_discount

        CENT = Decimal("0.01")

        def checkout_total(subtotal: Decimal, settings: dict[str, str]) -> Decimal:
            try:
                discount = parse_discount(settings.get("discount", "0%"))
            except (InvalidOperation, ValueError):
                # Existing fallback masks malformed documented configuration.
                discount = Decimal("0")
            return (subtotal * (Decimal("1") - discount)).quantize(CENT)
    """)
    prelude = python_test_prelude("checkout")
    write_file(root, "tests/test_checkout.py", prelude + """
        import unittest
        from decimal import Decimal
        from checkout.core import checkout_total

        class CheckoutIntegrationTests(unittest.TestCase):
            def test_documented_discount_format(self):
                self.assertEqual(
                    checkout_total(Decimal("100.00"), {"discount": "10%"}),
                    Decimal("90.00"),
                )

            def test_zero_discount(self):
                self.assertEqual(
                    checkout_total(Decimal("100.00"), {"discount": "0%"}),
                    Decimal("100.00"),
                )
    """)


def build_polling_discipline(root: Path) -> None:
    write_file(root, "pyproject.toml", """
        [project]
        name = "build-label"
        version = "1.8.0"
        requires-python = ">=3.11"
    """)
    write_file(root, "README.md", """
        # Build Label

        The task-specific prompt names the required validation command.
    """)
    write_file(root, "src/build_label/__init__.py", "")
    write_file(root, "src/build_label/core.py", """
        def build_label(name: str, version: str) -> str:
            return f"{name}:{version}"
    """)
    write_file(root, "tools/slow_validation.py", """
        import sys
        import time
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
        from build_label.core import build_label

        print("slow validation started", flush=True)
        time.sleep(35)
        actual = build_label("progressive", "1.8.0")
        if actual != "progressive@1.8.0":
            print(f"expected progressive@1.8.0, got {actual}", file=sys.stderr)
            raise SystemExit(1)
        print("slow validation passed", flush=True)
    """)


FIXTURE_BUILDERS = {
    "recon_batch": build_recon_batch,
    "keyhole_read": build_keyhole_read,
    "environment_probe": build_environment_probe,
    "validation_convergence": build_validation_convergence,
    "failure_pivot": build_failure_pivot,
    "polling_discipline": build_polling_discipline,
}


def materialize_fixture(fixture: str, destination: Path) -> None:
    if fixture not in FIXTURE_BUILDERS:
        raise ValueError(f"unknown fixture: {fixture}")
    destination.mkdir(parents=True, exist_ok=True)
    FIXTURE_BUILDERS[fixture](destination)


def fixture_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts):
        rel = path.relative_to(root).as_posix()
        digest.update(rel.encode("utf-8") + b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


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
    with tarfile.open(fileobj=io.BytesIO(result.stdout), mode="r:") as tf:
        for member in tf.getmembers():
            target = (destination / member.name).resolve()
            if destination.resolve() not in target.parents and target != destination.resolve():
                raise RuntimeError(f"unsafe archive path: {member.name}")
        tf.extractall(destination)


def build_runtime_from_ref(repo: Path, ref: str, agent_target: str, destination: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="pc-benchmark-workflow-") as tmp:
        exported = Path(tmp) / "source"
        export_git_ref(repo, ref, exported)
        command = [
            sys.executable,
            str(exported / "tools/build_runtime.py"),
            "--profile",
            "standalone",
            "--agent",
            agent_target,
        ]
        result = subprocess.run(command, cwd=exported, capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(
                f"runtime build failed for {ref}:\n{result.stdout}\n{result.stderr}".strip()
            )
        artifacts = sorted((exported / "dist").glob("Progressive-Context-Project-Runtime-v*.zip"))
        if len(artifacts) != 1:
            raise RuntimeError(f"expected one standalone runtime artifact for {ref}, found {len(artifacts)}")
        with zipfile.ZipFile(artifacts[0]) as zf:
            names = zf.namelist()
            top = {name.split("/", 1)[0] for name in names if name}
            if len(top) != 1:
                raise RuntimeError(f"runtime artifact for {ref} must have one top-level directory")
            prefix = next(iter(top)).rstrip("/") + "/"
            for name in names:
                if not name.startswith(prefix) or name == prefix:
                    continue
                rel = name[len(prefix):]
                if not rel:
                    continue
                target = destination / rel
                if name.endswith("/"):
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(zf.read(name))


def init_clean_git_repo(root: Path) -> str:
    env = os.environ.copy()
    env.update({
        "GIT_AUTHOR_NAME": "Progressive Benchmark",
        "GIT_AUTHOR_EMAIL": "benchmark@example.invalid",
        "GIT_COMMITTER_NAME": "Progressive Benchmark",
        "GIT_COMMITTER_EMAIL": "benchmark@example.invalid",
        "GIT_AUTHOR_DATE": "2026-08-20T00:00:00+00:00",
        "GIT_COMMITTER_DATE": "2026-08-20T00:00:00+00:00",
    })
    commands = [
        ["git", "init", "-q"],
        ["git", "add", "-A"],
        ["git", "commit", "-q", "-m", "benchmark fixture"],
    ]
    for command in commands:
        result = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(f"{' '.join(command)} failed: {result.stderr.strip()}")
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def write_task_material(task_dir: Path, task: dict) -> None:
    write_file(task_dir, "prompt.md", task["prompt"] + "\n")
    acceptance = "# Acceptance criteria\n\n" + "\n".join(f"- {item}" for item in task["acceptance"]) + "\n"
    write_file(task_dir, "acceptance.md", acceptance)


def prepare_pack(output: Path, repetitions: int, selected_tasks: set[str] | None = None) -> dict:
    experiment = load_json(BENCHMARK_ROOT / "EXPERIMENT.json")
    tasks = load_json(BENCHMARK_ROOT / "TASKS.json")["tasks"]
    if selected_tasks:
        unknown = selected_tasks - {task["id"] for task in tasks}
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

    runtime_cache: dict[str, Path] = {}
    with tempfile.TemporaryDirectory(prefix="pc-benchmark-runtime-") as runtime_tmp:
        for arm, ref in (
            ("baseline", experiment["baseline_workflow_ref"]),
            ("candidate", experiment["candidate_workflow_ref"]),
        ):
            runtime_dir = Path(runtime_tmp) / arm
            runtime_dir.mkdir(parents=True)
            build_runtime_from_ref(ROOT, ref, experiment.get("agent_target", "both"), runtime_dir)
            runtime_cache[arm] = runtime_dir

        for task in tasks:
            with tempfile.TemporaryDirectory(prefix=f"pc-fixture-{task['id']}-") as fixture_tmp:
                raw = Path(fixture_tmp) / "repo"
                materialize_fixture(task["fixture"], raw)
                snapshot = fixture_digest(raw)

                task_dir = output / "tasks" / task["id"]
                write_task_material(task_dir, task)
                for repetition in range(1, repetitions + 1):
                    pair_id = f"{task['id']}-r{repetition:02d}"
                    pair = {
                        "pair_id": pair_id,
                        "task_id": task["id"],
                        "task_class": task["task_class"],
                        "mechanism": task["mechanism"],
                        "fixture_snapshot": snapshot,
                        "prompt": str((task_dir / "prompt.md").relative_to(output)),
                        "acceptance": str((task_dir / "acceptance.md").relative_to(output)),
                        "arms": {},
                    }
                    for arm in ("baseline", "candidate"):
                        repo_dir = task_dir / f"r{repetition:02d}" / arm / "repo"
                        shutil.copytree(raw, repo_dir)
                        for source in runtime_cache[arm].rglob("*"):
                            rel = source.relative_to(runtime_cache[arm])
                            target = repo_dir / rel
                            if source.is_dir():
                                target.mkdir(parents=True, exist_ok=True)
                            elif source.is_file():
                                target.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(source, target)
                        commit = init_clean_git_repo(repo_dir)
                        pair["arms"][arm] = {
                            "workflow_ref": experiment[f"{arm}_workflow_ref"],
                            "repo": str(repo_dir.relative_to(output)),
                            "local_git_commit": commit,
                        }
                    plan["pairs"].append(pair)

    (output / "RUN_PLAN.json").write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    return plan


def main() -> int:
    ap = argparse.ArgumentParser(description="Prepare paired Progressive Context agent benchmark repos.")
    ap.add_argument(
        "--output",
        default=str(ROOT / "dist/agent-benchmark/execution-efficiency-v1"),
        help="Disposable benchmark-pack destination.",
    )
    ap.add_argument("--repetitions", type=int, default=None)
    ap.add_argument("--task", action="append", dest="tasks", help="Prepare only this task id; repeatable.")
    args = ap.parse_args()

    experiment = load_json(BENCHMARK_ROOT / "EXPERIMENT.json")
    repetitions = args.repetitions or int(experiment.get("default_repetitions", 1))
    if repetitions < 1:
        print("ERROR: --repetitions must be >= 1", file=sys.stderr)
        return 2
    try:
        plan = prepare_pack(Path(args.output).resolve(), repetitions, set(args.tasks or []) or None)
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print("AGENT BENCHMARK PACK: READY")
    print(f"Output: {Path(args.output).resolve()}")
    print(f"Pairs: {len(plan['pairs'])}")
    print(f"Baseline: {plan['baseline_workflow_ref']}")
    print(f"Candidate: {plan['candidate_workflow_ref']}")
    print("Next: run the same agent/model/settings on each baseline/candidate pair using its prompt.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
