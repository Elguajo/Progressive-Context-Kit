import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import autoresearch
from runtime_layout import runtime_entries

BASELINE = "1" * 40
CANDIDATE = "2" * 40


def summary(gate="PASS"):
    return {
        "pair_count": 5,
        "quality_gate": gate,
        "quality_gate_reason": "test evidence",
        "median_paired_percent_delta": {
            "total_tokens": -10.0,
            "turns": -5.0,
            "tool_calls": -8.0,
            "file_reads": -12.0,
            "wall_time_seconds": -3.0,
        },
        "median_paired_quality_delta": 0.0,
    }


class AutoresearchTests(unittest.TestCase):
    def isolated(self, root: Path):
        ar = root / "docs/evals/agent/autoresearch"
        ar.mkdir(parents=True, exist_ok=True)
        (ar / "REGISTRY.json").write_text(
            json.dumps({"schema": 1, "next_experiment_number": 1, "experiments": []}) + "\n",
            encoding="utf-8",
        )
        return patch.multiple(
            autoresearch,
            ROOT=root,
            AUTORESEARCH_ROOT=ar,
            REGISTRY_PATH=ar / "REGISTRY.json",
            EXPERIMENTS_DIR=ar / "experiments",
            EVIDENCE_DIR=ar / "evidence",
        )

    def new_args(self, **overrides):
        data = dict(
            observation="Trace shows repeated full-file reads after symbol location.",
            hypothesis="Locate-then-slice wording will reduce read volume without quality loss.",
            change="Make bounded inspection operational: locate, slice, widen only if unresolved.",
            baseline_ref=BASELINE,
            candidate_ref=CANDIDATE,
            task_set="execution-efficiency-v1/keyhole-read",
            evidence_ref=["trace://discovery/keyhole-r01"],
            file=["global/AGENTS.codex.md"],
            parent=None,
        )
        data.update(overrides)
        return SimpleNamespace(**data)

    def test_current_registry_and_records_validate(self):
        self.assertEqual(autoresearch.validate_repository(ROOT), [])

    def test_new_requires_observed_evidence_and_changed_surface(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            with self.isolated(root):
                with self.assertRaises(autoresearch.AutoresearchError):
                    autoresearch.create_experiment(self.new_args(evidence_ref=[]))
                with self.assertRaises(autoresearch.AutoresearchError):
                    autoresearch.create_experiment(self.new_args(file=[]))
                registry = autoresearch.load_json(autoresearch.REGISTRY_PATH)
                self.assertEqual(registry["next_experiment_number"], 1)
                self.assertEqual(registry["experiments"], [])

    def test_full_lifecycle_new_evaluate_keep_is_valid(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            with self.isolated(root):
                eid = autoresearch.create_experiment(self.new_args())
                self.assertEqual(eid, "EXP-0001")
                record = autoresearch.load_json(autoresearch.experiment_path(eid))
                self.assertEqual(record["status"], "PLANNED")

                summary_path = root / "summary.json"
                summary_path.write_text(json.dumps(summary()), encoding="utf-8")
                autoresearch.attach_evaluation(eid, summary_path)
                record = autoresearch.load_json(autoresearch.experiment_path(eid))
                self.assertEqual(record["status"], "EVALUATED")
                self.assertEqual(record["evaluation"]["quality_gate"], "PASS")

                autoresearch.decide_experiment(eid, "KEEP", "Measured saving with quality gate PASS")
                record = autoresearch.load_json(autoresearch.experiment_path(eid))
                self.assertEqual(record["status"], "DECIDED")
                self.assertEqual(record["decision"]["outcome"], "KEEP")
                self.assertEqual(autoresearch.validate_repository(root), [])

    def test_keep_is_forbidden_when_quality_gate_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            with self.isolated(root):
                eid = autoresearch.create_experiment(self.new_args())
                summary_path = root / "summary.json"
                summary_path.write_text(json.dumps(summary("FAIL")), encoding="utf-8")
                autoresearch.attach_evaluation(eid, summary_path)
                with self.assertRaises(autoresearch.AutoresearchError):
                    autoresearch.decide_experiment(eid, "KEEP", "Cheaper but regressed")
                self.assertEqual(autoresearch.load_json(autoresearch.experiment_path(eid))["status"], "EVALUATED")

    def test_modify_creates_new_linked_experiment_instead_of_reopening_parent(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            with self.isolated(root):
                parent = autoresearch.create_experiment(self.new_args())
                summary_path = root / "summary.json"
                summary_path.write_text(json.dumps(summary("INCONCLUSIVE")), encoding="utf-8")
                autoresearch.attach_evaluation(parent, summary_path)
                autoresearch.decide_experiment(parent, "MODIFY", "Promising but inconclusive")

                child = autoresearch.create_experiment(
                    self.new_args(
                        parent=parent,
                        baseline_ref=CANDIDATE,
                        candidate_ref="3" * 40,
                        hypothesis="A narrower formulation will produce a stable paired saving.",
                    )
                )
                self.assertEqual(child, "EXP-0002")
                child_record = autoresearch.load_json(autoresearch.experiment_path(child))
                self.assertEqual(child_record["parent_experiment_id"], parent)
                self.assertEqual(
                    autoresearch.load_json(autoresearch.experiment_path(parent))["status"],
                    "DECIDED",
                )
                self.assertEqual(autoresearch.validate_repository(root), [])

    def test_evidence_hash_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            with self.isolated(root):
                eid = autoresearch.create_experiment(self.new_args())
                summary_path = root / "summary.json"
                summary_path.write_text(json.dumps(summary()), encoding="utf-8")
                autoresearch.attach_evaluation(eid, summary_path)
                evidence = root / autoresearch.load_json(autoresearch.experiment_path(eid))["evaluation"]["summary_path"]
                evidence.write_text("{}\n", encoding="utf-8")
                errors = autoresearch.validate_repository(root)
                self.assertTrue(any("SHA-256 mismatch" in error for error in errors))

    def test_autoresearch_infrastructure_stays_out_of_project_runtime(self):
        runtime_sources = {src.resolve() for src, _, _ in runtime_entries(ROOT, "standalone")}
        source_only = {
            path.resolve()
            for path in (ROOT / "docs/evals/agent/autoresearch").rglob("*")
            if path.is_file()
        }
        source_only.add((ROOT / "tools/autoresearch.py").resolve())
        self.assertTrue(source_only.isdisjoint(runtime_sources))

    def test_release_builder_validates_autoresearch_before_runtime_build(self):
        text = (ROOT / "tools/build_release.py").read_text(encoding="utf-8")
        self.assertIn('"tools/autoresearch.py validate"', text)
        self.assertIn('"autoresearch_records": True', text)


if __name__ == "__main__":
    unittest.main()
