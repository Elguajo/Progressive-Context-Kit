import json
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from analyze_agent_eval import (
    ANONYMOUS_ARTIFACTS,
    EvalDataError,
    JUDGE_IDENTIFICATION_FIELDS,
    JUDGE_RECORD_FIELDS,
    QUALITY_KEYS,
    WORKFLOW_EVIDENCE_KEYS,
    pair_records,
    summarize,
    validate_judge_record,
)
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


def judge_record(pair_id, *, a_score=3, b_score=3, a_failures=None, b_failures=None):
    return {
        "schema": 1,
        "experiment_id": "execution-efficiency-test",
        "pair_id": pair_id,
        "judge": {"agent": "reviewer", "model": "fixed-judge", "reasoning": "fixed"},
        "artifacts": ["A", "B"],
        "rubric_ref": "rubrics/v1",
        "scores": {"A": quality(a_score), "B": quality(b_score)},
        "hard_failures": {"A": a_failures or [], "B": b_failures or []},
        "preference": "TIE",
        "confidence": "MEDIUM",
        "notes": "Artifacts were reviewed anonymously.",
    }


def pair_map(pair_id, *, baseline="A", candidate="B"):
    return {
        "schema": 1,
        "pairs": [{
            "experiment_id": "execution-efficiency-test",
            "pair_id": pair_id,
            "mapping": {"baseline": baseline, "candidate": candidate},
        }],
    }


def workflow_evidence():
    return {
        "artifact_refs": ["artifacts/diff.patch"],
        "project_state_refs": ["git/status.txt"],
        "command_result_refs": ["commands/test.txt"],
        "verification_refs": ["verification/summary.txt"],
        "tool_trace_refs": [],
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

    def test_blinded_judge_scores_replace_run_record_quality_for_gate(self):
        records = [record("p1", "baseline"), record("p1", "candidate")]
        mapping = {("execution-efficiency-test", "p1"): {"baseline": "A", "candidate": "B"}}
        summary = summarize(records, judge_records=[judge_record("p1", a_score=3, b_score=2)], anonymous_pair_map=mapping)
        self.assertEqual(summary["quality_evidence"], "blinded_judge_records")
        self.assertEqual(summary["quality_gate"], "FAIL")

    def test_blinded_judge_hard_failure_causes_regression_using_private_map(self):
        records = [record("p1", "baseline"), record("p1", "candidate")]
        mapping = {("execution-efficiency-test", "p1"): {"baseline": "B", "candidate": "A"}}
        summary = summarize(
            records,
            judge_records=[judge_record("p1", a_failures=["unsafe action"])],
            anonymous_pair_map=mapping,
        )
        self.assertEqual(summary["quality_gate"], "FAIL")
        self.assertEqual(summary["hard_regressions"], ["execution-efficiency-test:p1"])

    def test_judge_record_rejects_nonanonymous_artifacts(self):
        item = judge_record("p1")
        item["artifacts"] = ["baseline", "candidate"]
        with self.assertRaises(EvalDataError):
            validate_judge_record(item, 0)

    def test_judge_schema_and_runtime_validator_share_canonical_shape(self):
        schema = json.loads((ROOT / "docs/evals/agent/JUDGE_RECORD.schema.json").read_text())
        self.assertEqual(set(schema["required"]), JUDGE_RECORD_FIELDS)
        self.assertEqual(set(schema["properties"]["judge"]["required"]), JUDGE_IDENTIFICATION_FIELDS)
        self.assertEqual(tuple(schema["properties"]["artifacts"]["const"]), ANONYMOUS_ARTIFACTS)
        self.assertEqual(schema["properties"]["scores"]["properties"]["A"]["$ref"], "#/$defs/quality")
        self.assertEqual(set(schema["$defs"]["quality"]["required"]), set(QUALITY_KEYS))

    def test_workflow_claim_requires_blinding_and_nonself_report_evidence(self):
        records = [record("p1", "baseline"), record("p1", "candidate")]
        mapping = {("execution-efficiency-test", "p1"): {"baseline": "A", "candidate": "B"}}
        with self.assertRaises(EvalDataError):
            summarize(records, require_workflow_evidence=True)
        for item in records:
            item["evidence"] = workflow_evidence()
        summary = summarize(
            records,
            judge_records=[judge_record("p1")],
            anonymous_pair_map=mapping,
            require_workflow_evidence=True,
        )
        self.assertTrue(summary["workflow_evidence_required"])
        records[0]["evidence"]["verification_refs"] = []
        with self.assertRaises(EvalDataError):
            summarize(
                records,
                judge_records=[judge_record("p1")],
                anonymous_pair_map=mapping,
                require_workflow_evidence=True,
            )

    def test_workflow_evidence_schema_fields_match_analyzer(self):
        schema = json.loads((ROOT / "docs/evals/agent/RUN_RECORD.schema.json").read_text())
        self.assertEqual(set(schema["properties"]["evidence"]["required"]), set(WORKFLOW_EVIDENCE_KEYS))

    def test_real_agent_eval_foundation_stays_source_only(self):
        sources = {src.relative_to(ROOT).as_posix() for src, _, _ in runtime_entries(ROOT)}
        self.assertNotIn("tools/analyze_agent_eval.py", sources)
        self.assertNotIn("docs/evals/agent/EXECUTION_EFFICIENCY_PROTOCOL.md", sources)
        self.assertNotIn("docs/evals/agent/RUN_RECORD.schema.json", sources)
        self.assertNotIn("docs/evals/agent/JUDGE_RECORD.schema.json", sources)


if __name__ == "__main__":
    unittest.main()
