import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prepare_agent_benchmark import (
    BENCHMARK_ROOT,
    OPTIONAL_FRAMEWORK_TOOLS,
    fixture_digest,
    initialize_benchmark_project,
    materialize_fixture,
)
from runtime_layout import runtime_entries


class AgentBenchmarkPackTests(unittest.TestCase):
    def test_experiment_pins_immutable_distinct_workflow_refs(self):
        experiment = json.loads((BENCHMARK_ROOT / "EXPERIMENT.json").read_text(encoding="utf-8"))
        baseline = experiment["baseline_workflow_ref"]
        candidate = experiment["candidate_workflow_ref"]
        self.assertRegex(baseline, r"^[0-9a-f]{40}$")
        self.assertRegex(candidate, r"^[0-9a-f]{40}$")
        self.assertNotEqual(baseline, candidate)
        self.assertEqual(experiment["profile"], "standalone")
        self.assertGreaterEqual(experiment["claim_repetitions_minimum"], 5)

    def test_task_set_covers_each_execution_efficiency_mechanism_once(self):
        data = json.loads((BENCHMARK_ROOT / "TASKS.json").read_text(encoding="utf-8"))
        tasks = data["tasks"]
        expected = {
            "batch-reconnaissance",
            "bounded-keyhole-reads",
            "single-pass-environment-probing",
            "convergent-validation",
            "repeated-failure-pivot",
            "bounded-polling",
        }
        self.assertEqual(len(tasks), 6)
        self.assertEqual({task["mechanism"] for task in tasks}, expected)
        self.assertEqual(len({task["id"] for task in tasks}), 6)
        for task in tasks:
            self.assertTrue(task["prompt"].strip())
            self.assertGreaterEqual(len(task["acceptance"]), 3)
            self.assertNotIn(task["mechanism"], task["prompt"])

    def test_all_raw_fixtures_materialize_deterministically_and_compile(self):
        tasks = json.loads((BENCHMARK_ROOT / "TASKS.json").read_text(encoding="utf-8"))["tasks"]
        for task in tasks:
            with self.subTest(task=task["id"]), tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
                first = Path(a) / "repo"
                second = Path(b) / "repo"
                materialize_fixture(task["fixture"], first)
                materialize_fixture(task["fixture"], second)
                self.assertEqual(fixture_digest(first), fixture_digest(second))
                self.assertFalse((first / "AGENTS.md").exists())
                self.assertFalse((first / "CLAUDE.md").exists())
                self.assertFalse((first / ".progressive").exists())
                for source in first.rglob("*.py"):
                    compile(source.read_text(encoding="utf-8"), str(source), "exec")

    def test_injected_runtime_seeds_are_replaced_with_active_identical_project_state(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d) / "repo"
            materialize_fixture("recon_batch", repo)
            project = repo / ".progressive/project"
            project.mkdir(parents=True)
            for name in ["PROJECT_BRIEF.md", "ARCHITECTURE.md", "ROADMAP.md", "NEXT_SESSION.md"]:
                (project / name).write_text("Status: UNINITIALIZED\n", encoding="utf-8")
            (project / "TOOLING_STATUS.json").write_text("{}\n", encoding="utf-8")
            (project / "TOOLING_STATUS.md").write_text("Status: UNINITIALIZED\n", encoding="utf-8")

            initialize_benchmark_project(repo, "recon-batch")

            for name in ["PROJECT_BRIEF.md", "ARCHITECTURE.md", "ROADMAP.md", "NEXT_SESSION.md"]:
                text = (project / name).read_text(encoding="utf-8")
                self.assertNotIn("UNINITIALIZED", text)
            self.assertIn("Status: ACTIVE", (project / "PROJECT_BRIEF.md").read_text(encoding="utf-8"))
            self.assertIn("[>] Phase 00", (project / "ROADMAP.md").read_text(encoding="utf-8"))
            self.assertTrue((repo / ".progressive/phases/00-benchmark-task.md").is_file())

            tooling = json.loads((project / "TOOLING_STATUS.json").read_text(encoding="utf-8"))
            self.assertEqual(tooling["profile"], "minimal")
            self.assertEqual(set(tooling["tools"]), set(OPTIONAL_FRAMEWORK_TOOLS))
            self.assertTrue(
                all(entry["status"] == "not_applicable" for entry in tooling["tools"].values())
            )
            tooling_md = (project / "TOOLING_STATUS.md").read_text(encoding="utf-8")
            self.assertIn("Profile: minimal", tooling_md)
            self.assertIn("repository-native tools only", tooling_md)

    def test_keyhole_fixture_is_materially_large_and_polling_fixture_is_long_running(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            keyhole = root / "keyhole"
            polling = root / "polling"
            materialize_fixture("keyhole_read", keyhole)
            materialize_fixture("polling_discipline", polling)
            lines = (keyhole / "src/catalog/data.py").read_text(encoding="utf-8").splitlines()
            self.assertGreater(len(lines), 1300)
            slow = (polling / "tools/slow_validation.py").read_text(encoding="utf-8")
            self.assertIn("time.sleep(35)", slow)

    def test_environment_fixture_exposes_groupable_prerequisites(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "repo"
            materialize_fixture("environment_probe", root)
            text = (root / "ENVIRONMENT.md").read_text(encoding="utf-8")
            for anchor in ["python3 --version", "git --version", "schema_probe.py --version"]:
                self.assertIn(anchor, text)

    def test_benchmark_research_files_stay_out_of_project_runtime(self):
        runtime_sources = {src.resolve() for src, _, _ in runtime_entries(ROOT, "standalone")}
        benchmark_sources = {
            path.resolve()
            for path in (ROOT / "docs/evals/agent/benchmark").rglob("*")
            if path.is_file()
        }
        benchmark_sources.update(
            {
                (ROOT / "tools/prepare_agent_benchmark.py").resolve(),
                (ROOT / "tools/agent_benchmark_fixtures.py").resolve(),
            }
        )
        self.assertTrue(benchmark_sources.isdisjoint(runtime_sources))


if __name__ == "__main__":
    unittest.main()
