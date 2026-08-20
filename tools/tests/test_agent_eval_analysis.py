import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from analyze_agent_eval import EvalDataError, QUALITY_KEYS, pair_records, summarize
from runtime_layout import runtime_entries


def quality(score=3):
    return {key: score for key in QUALITY_KEYS}


def record(pair_id, arm, *, tokens=1000, turns=10, hard_pass=True, quality_score=3):
    return {
        "schema": 1,
        "experiment_id": "execution-efficiency-test",
        "pair_id": pair_id,
        "arm": arm,
        "task_id": "task-1",
        "task_class": "directed-implementation",
        "agent": "codex",
        "model": "fixed-model",
        "reasoning": "fixed",
        "workflow_ref": "baseline-ref" if arm == "baseline" else "candidate-ref",
        "controls": {
            "repo_snapshot": "repo-sha",
            "task_sha256": "task-sha",
            "acceptance_sha256": "acceptance-sha",
            "tools_profile": "tools-v1",
            "permissions_profile": "permissions-v1",
            "environment_profile": "environment-v1",
        },
        "outcome": {
            "hard_pass": hard_pass,
            "hard_failures": [] if hard_pass else ["material failure"],
            "quality": quality(quality_score),
        },
        "metrics": {
            "total_tokens": tokens,
            "input_tokens": tokens - 100,
            "output_tokens": 100,
            "cache_read_tokens": 0,
            "cost_usd": None,
            "turns": turns,
            "tool_calls": 8,
            "file_reads": 4,
            "wall_time_seconds": 60,
            "initial_context_tokens": 500,
            "peak_context_tokens": 1500,
            "token_accounting": "input+output",
        },
    }


class AgentEvalAnalysisTests(unittest.TestCase):
    def test_paired_summary_reports_candidate_savings(self):
        records = [
            record("p1", "baseline", tokens=1000, turns=10),
            record("p1", "candidate", tokens=800, turns=8),
            record("p2", "baseline", tokens=2000, turns=20),
            record("p2", "candidate", tokens=1600, turns=16),
        ]
        summary = summarize(records)
        self.assertEqual(summary["quality_gate"], "PASS")
        self.assertEqual(summary["pair_count"], 2)
        self.assertAlmostEqual(summary["median_paired_percent_delta"]["total_tokens"], -20.0)
        self.assertAlmostEqual(summary["median_paired_percent_delta"]["turns"], -20.0)
        self.assertAlmostEqual(summary["median_paired_quality_delta"], 0.0)

    def test_control_mismatch_rejects_pair(self):
        baseline = record("p1", "baseline")
        candidate = record("p1", "candidate")
        candidate["controls"]["repo_snapshot"] = "different-repo-sha"
        with self.assertRaises(EvalDataError):
            pair_records([baseline, candidate])

    def test_baseline_pass_candidate_fail_is_hard_regression(self):
        summary = summarize([
            record("p1", "baseline", hard_pass=True),
            record("p1", "candidate", hard_pass=False),
        ])
        self.assertEqual(summary["quality_gate"], "FAIL")
        self.assertEqual(summary["hard_regressions"], ["execution-efficiency-test:p1"])

    def test_quality_drop_respects_noninferiority_tolerance(self):
        records = [
            record("p1", "baseline", quality_score=3),
            record("p1", "candidate", quality_score=2),
        ]
        self.assertEqual(summarize(records, quality_tolerance=0.5)["quality_gate"], "FAIL")
        self.assertEqual(summarize(records, quality_tolerance=1.0)["quality_gate"], "PASS")

    def test_pair_requires_both_arms(self):
        with self.assertRaises(EvalDataError):
            pair_records([record("p1", "baseline")])

    def test_real_agent_eval_foundation_stays_source_only(self):
        sources = {src.relative_to(ROOT).as_posix() for src, _, _ in runtime_entries(ROOT)}
        self.assertNotIn("tools/analyze_agent_eval.py", sources)
        self.assertNotIn("docs/evals/agent/EXECUTION_EFFICIENCY_PROTOCOL.md", sources)
        self.assertNotIn("docs/evals/agent/RUN_RECORD.schema.json", sources)


if __name__ == "__main__":
    unittest.main()
