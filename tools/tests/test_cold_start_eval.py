import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from analyze_cold_start_eval import load_oracles, summarize
from prepare_cold_start_eval import COLD_START_ROOT, materialize_scenario_repo, prepare_pack
from runtime_layout import runtime_entries


def scenarios():
    return json.loads((COLD_START_ROOT / "SCENARIOS.json").read_text(encoding="utf-8"))["scenarios"]


def record_for(scenario, run_id="run-1", *, rescue_turns=0, planning_depth=None):
    oracle = scenario["oracle"]
    depths = oracle.get("acceptable_planning_depths", [])
    return {
        "schema": 1,
        "suite_id": "cold-start-runtime-transfer-v1",
        "suite_run_id": run_id,
        "scenario_id": scenario["id"],
        "agent": "codex",
        "model": "fixed-model",
        "reasoning": "fixed",
        "workflow_ref": "f" * 40,
        "controls": {
            "repo_snapshot": "repo-" + scenario["id"],
            "prompt_sha256": "prompt-" + scenario["id"],
            "tools_profile": "native-only",
            "permissions_profile": "sandbox",
            "environment_profile": "python-3.12",
            "fresh_session": True,
        },
        "observation": {
            "rescue_turns": rescue_turns,
            "routed_skills": list(oracle.get("required_skills", [])),
            "planning_depth": planning_depth if planning_depth is not None else (depths[0] if depths else None),
            "stopped_for_user_direction": oracle["stopped_for_user_direction"],
            "state_checks": {name: True for name in oracle.get("required_checks", [])},
            "hard_failures": [],
        },
        "metrics": {
            "total_tokens": None,
            "turns": None,
            "tool_calls": None,
            "file_reads": None,
            "wall_time_seconds": None,
            "token_accounting": None,
        },
    }


class ColdStartEvalTests(unittest.TestCase):
    def test_suite_has_eight_distinct_transfer_scenarios(self):
        data = json.loads((COLD_START_ROOT / "SCENARIOS.json").read_text(encoding="utf-8"))
        items = data["scenarios"]
        self.assertEqual(data["suite_id"], "cold-start-runtime-transfer-v1")
        self.assertEqual(len(items), 8)
        self.assertEqual(len({item["id"] for item in items}), 8)
        self.assertEqual(
            {item["id"] for item in items},
            {
                "greenfield-direct",
                "greenfield-focused",
                "existing-project-adoption",
                "unclear-root-cause-bug",
                "architecture-fork-stop",
                "session-continuation",
                "completed-roadmap-change-request",
                "high-risk-full",
            },
        )
        for item in items:
            self.assertTrue(item["prompt"].strip())
            self.assertNotIn("required_skills", item["prompt"])
            self.assertNotIn("acceptable_planning_depths", item["prompt"])
            self.assertGreaterEqual(len(item["oracle"]["required_checks"]), 3)

    def test_greenfield_and_adoption_pending_states_are_distinct(self):
        by_id = {item["id"]: item for item in scenarios()}
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            greenfield = root / "greenfield"
            adoption = root / "adoption"
            materialize_scenario_repo(ROOT, by_id["greenfield-direct"], greenfield)
            materialize_scenario_repo(ROOT, by_id["existing-project-adoption"], adoption)
            self.assertIn(
                "Status: UNINITIALIZED",
                (greenfield / ".progressive/project/PROJECT_BRIEF.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                (adoption / ".progressive/ADOPTION_STATE").read_text(encoding="utf-8").strip(),
                "pending",
            )
            self.assertTrue((adoption / "src/harbor/dispatcher.py").is_file())

    def test_continuation_and_completed_roadmap_states_are_prepared(self):
        by_id = {item["id"]: item for item in scenarios()}
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            continuation = root / "continuation"
            completed = root / "completed"
            materialize_scenario_repo(ROOT, by_id["session-continuation"], continuation)
            materialize_scenario_repo(ROOT, by_id["completed-roadmap-change-request"], completed)
            next_session = (continuation / ".progressive/project/NEXT_SESSION.md").read_text(encoding="utf-8")
            self.assertIn("net_total", next_session)
            self.assertIn("[>] Phase 00", (continuation / ".progressive/project/ROADMAP.md").read_text(encoding="utf-8"))
            roadmap = (completed / ".progressive/project/ROADMAP.md").read_text(encoding="utf-8")
            self.assertIn("[x] Phase 00", roadmap)
            self.assertNotRegex(roadmap, r"(?m)^- \[>\]")
            self.assertIn(
                "## Completion Record",
                (completed / ".progressive/phases/00-complete.md").read_text(encoding="utf-8"),
            )

    def test_prepared_case_keeps_prompt_and_oracle_outside_agent_repo(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "pack"
            plan = prepare_pack(output, "f" * 40, selected={"greenfield-direct"})
            self.assertEqual(len(plan["cases"]), 1)
            case = plan["cases"][0]
            repo = output / case["repo"]
            prompt = output / case["prompt"]
            oracle = output / case["oracle"]
            self.assertTrue(prompt.is_file())
            self.assertTrue(oracle.is_file())
            self.assertFalse((repo / "prompt.md").exists())
            self.assertFalse((repo / "oracle.json").exists())
            self.assertTrue((repo / ".git").is_dir())
            self.assertEqual(len(plan["workflow_ref"]), 40)

    def test_complete_clean_suite_passes(self):
        items = scenarios()
        summary = summarize([record_for(item) for item in items])
        self.assertEqual(summary["transfer_gate"], "PASS")
        self.assertEqual(summary["runs"][0]["recorded_scenarios"], 8)
        self.assertEqual(summary["runs"][0]["total_rescue_turns"], 0)

    def test_rescue_turn_causes_transfer_failure(self):
        items = scenarios()
        records = [record_for(item) for item in items]
        records[0]["observation"]["rescue_turns"] = 1
        summary = summarize(records)
        self.assertEqual(summary["transfer_gate"], "FAIL")
        self.assertIn("greenfield-direct", summary["runs"][0]["failed_scenarios"])

    def test_wrong_planning_depth_causes_transfer_failure(self):
        items = scenarios()
        records = [record_for(item) for item in items]
        target = next(record for record in records if record["scenario_id"] == "high-risk-full")
        target["observation"]["planning_depth"] = "DIRECT"
        summary = summarize(records)
        self.assertEqual(summary["transfer_gate"], "FAIL")
        self.assertIn("high-risk-full", summary["runs"][0]["failed_scenarios"])

    def test_partial_suite_is_not_a_transfer_pass(self):
        items = scenarios()
        summary = summarize([record_for(item) for item in items[:-1]])
        self.assertEqual(summary["transfer_gate"], "FAIL")
        self.assertEqual(summary["runs"][0]["missing_scenarios"], ["high-risk-full"])

    def test_cold_start_infrastructure_stays_source_only(self):
        runtime_sources = {src.resolve() for src, _, _ in runtime_entries(ROOT, "standalone")}
        cold_sources = {
            path.resolve()
            for path in COLD_START_ROOT.rglob("*")
            if path.is_file()
        }
        cold_sources.update(
            {
                (ROOT / "tools/prepare_cold_start_eval.py").resolve(),
                (ROOT / "tools/analyze_cold_start_eval.py").resolve(),
            }
        )
        self.assertTrue(cold_sources.isdisjoint(runtime_sources))
        self.assertEqual(len(load_oracles()), 8)


if __name__ == "__main__":
    unittest.main()
