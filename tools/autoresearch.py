#!/usr/bin/env python3
"""Manage evidence-driven Progressive Context Autoresearch experiments.

This tool operates only on Framework Source research records. It never changes Project Runtime
or invokes an agent. Real runs are produced externally and analyzed by analyze_agent_eval.py.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
AUTORESEARCH_ROOT = ROOT / "docs/evals/agent/autoresearch"
REGISTRY_PATH = AUTORESEARCH_ROOT / "REGISTRY.json"
EXPERIMENTS_DIR = AUTORESEARCH_ROOT / "experiments"
EVIDENCE_DIR = AUTORESEARCH_ROOT / "evidence"

ID_RE = re.compile(r"^EXP-(\d{4})$")
REF_RE = re.compile(r"^[0-9a-f]{40}$")
DECISIONS = {"KEEP", "MODIFY", "REMOVE"}
STATUSES = {"PLANNED", "EVALUATED", "DECIDED"}
SUMMARY_KEYS = {
    "pair_count",
    "quality_gate",
    "quality_gate_reason",
    "median_paired_percent_delta",
    "median_paired_quality_delta",
}


class AutoresearchError(ValueError):
    pass


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AutoresearchError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise AutoresearchError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise AutoresearchError(f"expected JSON object: {path}")
    return data


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def experiment_path(experiment_id: str) -> Path:
    if not ID_RE.fullmatch(experiment_id):
        raise AutoresearchError("experiment id must match EXP-NNNN")
    return EXPERIMENTS_DIR / f"{experiment_id}.json"


def validate_record(record: dict, *, root: Path | None = None) -> list[str]:
    root = ROOT if root is None else root
    errors: list[str] = []
    rid = record.get("experiment_id")
    if not isinstance(rid, str) or not ID_RE.fullmatch(rid):
        errors.append("experiment_id must match EXP-NNNN")
    if record.get("schema") != 1:
        errors.append(f"{rid or '<unknown>'}: schema must be 1")
    status = record.get("status")
    if status not in STATUSES:
        errors.append(f"{rid}: invalid status {status!r}")
    if not isinstance(record.get("created_at"), str) or not record.get("created_at"):
        errors.append(f"{rid}: created_at must be non-empty")

    parent = record.get("parent_experiment_id")
    if parent is not None and (not isinstance(parent, str) or not ID_RE.fullmatch(parent)):
        errors.append(f"{rid}: invalid parent_experiment_id")
    if parent == rid:
        errors.append(f"{rid}: experiment cannot parent itself")

    observation = record.get("observation")
    if not isinstance(observation, dict):
        errors.append(f"{rid}: observation must be object")
    else:
        if not isinstance(observation.get("text"), str) or not observation.get("text", "").strip():
            errors.append(f"{rid}: observation.text must be non-empty")
        refs = observation.get("evidence_refs")
        if (
            not isinstance(refs, list)
            or not refs
            or not all(isinstance(x, str) and x.strip() for x in refs)
        ):
            errors.append(f"{rid}: observation.evidence_refs must be a non-empty string array")

    if not isinstance(record.get("hypothesis"), str) or not record.get("hypothesis", "").strip():
        errors.append(f"{rid}: hypothesis must be non-empty")

    change = record.get("candidate_change")
    if not isinstance(change, dict):
        errors.append(f"{rid}: candidate_change must be object")
    else:
        if not isinstance(change.get("summary"), str) or not change.get("summary", "").strip():
            errors.append(f"{rid}: candidate_change.summary must be non-empty")
        files = change.get("files")
        if (
            not isinstance(files, list)
            or not files
            or not all(isinstance(x, str) and x.strip() for x in files)
        ):
            errors.append(f"{rid}: candidate_change.files must be a non-empty string array")

    comparison = record.get("comparison")
    if not isinstance(comparison, dict):
        errors.append(f"{rid}: comparison must be object")
    else:
        baseline = comparison.get("baseline_workflow_ref")
        candidate = comparison.get("candidate_workflow_ref")
        if not isinstance(baseline, str) or not REF_RE.fullmatch(baseline):
            errors.append(f"{rid}: baseline_workflow_ref must be immutable 40-char git SHA")
        if not isinstance(candidate, str) or not REF_RE.fullmatch(candidate):
            errors.append(f"{rid}: candidate_workflow_ref must be immutable 40-char git SHA")
        if baseline == candidate:
            errors.append(f"{rid}: baseline and candidate workflow refs must differ")
        if not isinstance(comparison.get("task_set"), str) or not comparison.get("task_set", "").strip():
            errors.append(f"{rid}: comparison.task_set must be non-empty")

    evaluation = record.get("evaluation")
    decision = record.get("decision")
    if status == "PLANNED":
        if evaluation is not None:
            errors.append(f"{rid}: PLANNED experiment cannot have evaluation")
        if decision is not None:
            errors.append(f"{rid}: PLANNED experiment cannot have decision")
    elif status == "EVALUATED":
        if not isinstance(evaluation, dict):
            errors.append(f"{rid}: EVALUATED experiment requires evaluation")
        if decision is not None:
            errors.append(f"{rid}: EVALUATED experiment cannot have decision")
    elif status == "DECIDED":
        if not isinstance(evaluation, dict):
            errors.append(f"{rid}: DECIDED experiment requires evaluation")
        if not isinstance(decision, dict):
            errors.append(f"{rid}: DECIDED experiment requires decision")

    if isinstance(evaluation, dict):
        for key in SUMMARY_KEYS:
            if key not in evaluation:
                errors.append(f"{rid}: evaluation missing {key}")
        if not isinstance(evaluation.get("pair_count"), int) or evaluation.get("pair_count", 0) < 1:
            errors.append(f"{rid}: evaluation.pair_count must be positive integer")
        if evaluation.get("quality_gate") not in {"PASS", "FAIL", "INCONCLUSIVE"}:
            errors.append(f"{rid}: invalid evaluation.quality_gate")
        summary_path = evaluation.get("summary_path")
        summary_hash = evaluation.get("summary_sha256")
        if not isinstance(summary_path, str) or not summary_path:
            errors.append(f"{rid}: evaluation.summary_path must be non-empty")
        else:
            p = root / summary_path
            if not p.is_file():
                errors.append(f"{rid}: evaluation summary missing: {summary_path}")
            elif isinstance(summary_hash, str) and re.fullmatch(r"[0-9a-f]{64}", summary_hash):
                if sha256_file(p) != summary_hash:
                    errors.append(f"{rid}: evaluation summary SHA-256 mismatch")
            else:
                errors.append(f"{rid}: evaluation.summary_sha256 must be 64-char hex")

    if isinstance(decision, dict):
        outcome = decision.get("outcome")
        if outcome not in DECISIONS:
            errors.append(f"{rid}: invalid decision outcome")
        if not isinstance(decision.get("reason"), str) or not decision.get("reason", "").strip():
            errors.append(f"{rid}: decision.reason must be non-empty")
        if not isinstance(decision.get("decided_at"), str) or not decision.get("decided_at"):
            errors.append(f"{rid}: decision.decided_at must be non-empty")
        if outcome == "KEEP" and isinstance(evaluation, dict) and evaluation.get("quality_gate") != "PASS":
            errors.append(f"{rid}: KEEP requires evaluation quality_gate=PASS")

    return errors


def validate_repository(root: Path | None = None) -> list[str]:
    root = ROOT if root is None else root
    registry_path = root / "docs/evals/agent/autoresearch/REGISTRY.json"
    experiments_dir = root / "docs/evals/agent/autoresearch/experiments"
    registry = load_json(registry_path)
    errors: list[str] = []
    if registry.get("schema") != 1:
        errors.append("autoresearch registry schema must be 1")
    entries = registry.get("experiments")
    if not isinstance(entries, list):
        return errors + ["autoresearch registry experiments must be array"]

    ids: set[str] = set()
    paths: set[str] = set()
    records: dict[str, dict] = {}
    max_number = 0
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("autoresearch registry entry must be object")
            continue
        eid = entry.get("experiment_id")
        rel = entry.get("path")
        status = entry.get("status")
        if not isinstance(eid, str) or not ID_RE.fullmatch(eid):
            errors.append(f"invalid registry experiment id: {eid!r}")
            continue
        max_number = max(max_number, int(ID_RE.fullmatch(eid).group(1)))
        if eid in ids:
            errors.append(f"duplicate registry experiment id: {eid}")
        ids.add(eid)
        if not isinstance(rel, str) or not rel:
            errors.append(f"{eid}: registry path must be non-empty")
            continue
        if rel in paths:
            errors.append(f"duplicate registry path: {rel}")
        paths.add(rel)
        p = root / rel
        if not p.is_file():
            errors.append(f"{eid}: registry record missing: {rel}")
            continue
        try:
            record = load_json(p)
        except AutoresearchError as exc:
            errors.append(str(exc))
            continue
        records[eid] = record
        errors.extend(validate_record(record, root=root))
        if record.get("experiment_id") != eid:
            errors.append(f"{eid}: record id does not match registry")
        if record.get("status") != status:
            errors.append(f"{eid}: registry status does not match record")

    next_number = registry.get("next_experiment_number")
    if not isinstance(next_number, int) or next_number < 1:
        errors.append("next_experiment_number must be positive integer")
    elif next_number <= max_number:
        errors.append("next_experiment_number must be greater than every allocated experiment id")

    for eid, record in records.items():
        parent = record.get("parent_experiment_id")
        if parent is not None and parent not in ids:
            errors.append(f"{eid}: parent experiment not present in registry: {parent}")
        if parent is not None:
            parent_record = records.get(parent)
            if parent_record and parent_record.get("status") != "DECIDED":
                errors.append(f"{eid}: parent experiment must already be DECIDED")
            if parent_record and (parent_record.get("decision") or {}).get("outcome") != "MODIFY":
                errors.append(f"{eid}: parent link is only valid from a MODIFY decision")

    existing_files = {
        p.relative_to(root).as_posix()
        for p in experiments_dir.glob("EXP-*.json")
        if p.is_file()
    }
    unregistered = existing_files - paths
    if unregistered:
        errors.append("unregistered experiment records: " + ", ".join(sorted(unregistered)))
    return errors


def create_experiment(args) -> str:
    registry = load_json(REGISTRY_PATH)
    number = registry.get("next_experiment_number")
    if not isinstance(number, int) or number < 1:
        raise AutoresearchError("invalid next_experiment_number in registry")
    eid = f"EXP-{number:04d}"
    path = experiment_path(eid)
    if path.exists():
        raise AutoresearchError(f"experiment record already exists: {path}")
    if args.baseline_ref == args.candidate_ref:
        raise AutoresearchError("baseline and candidate refs must differ")
    for label, ref in (("baseline", args.baseline_ref), ("candidate", args.candidate_ref)):
        if not REF_RE.fullmatch(ref):
            raise AutoresearchError(f"{label} ref must be immutable 40-char git SHA")
    parent = args.parent
    if parent:
        parent_record = load_json(experiment_path(parent))
        if parent_record.get("status") != "DECIDED" or (parent_record.get("decision") or {}).get("outcome") != "MODIFY":
            raise AutoresearchError("--parent must reference a DECIDED experiment with decision MODIFY")

    record = {
        "schema": 1,
        "experiment_id": eid,
        "status": "PLANNED",
        "created_at": now(),
        "parent_experiment_id": parent,
        "observation": {
            "text": args.observation.strip(),
            "evidence_refs": list(dict.fromkeys(args.evidence_ref or [])),
        },
        "hypothesis": args.hypothesis.strip(),
        "candidate_change": {
            "summary": args.change.strip(),
            "files": list(dict.fromkeys(args.file or [])),
        },
        "comparison": {
            "baseline_workflow_ref": args.baseline_ref,
            "candidate_workflow_ref": args.candidate_ref,
            "task_set": args.task_set.strip(),
        },
        "evaluation": None,
        "decision": None,
    }
    errors = validate_record(record)
    if errors:
        raise AutoresearchError("; ".join(errors))
    write_json(path, record)
    registry.setdefault("experiments", []).append(
        {
            "experiment_id": eid,
            "status": "PLANNED",
            "path": path.relative_to(ROOT).as_posix(),
        }
    )
    registry["next_experiment_number"] = number + 1
    write_json(REGISTRY_PATH, registry)
    return eid


def _registry_entry(registry: dict, eid: str) -> dict:
    for entry in registry.get("experiments", []):
        if entry.get("experiment_id") == eid:
            return entry
    raise AutoresearchError(f"experiment is not registered: {eid}")


def attach_evaluation(eid: str, summary_source: Path) -> None:
    path = experiment_path(eid)
    record = load_json(path)
    if record.get("status") != "PLANNED":
        raise AutoresearchError("evaluation may only be attached to a PLANNED experiment")
    summary = load_json(summary_source)
    missing = SUMMARY_KEYS - set(summary)
    if missing:
        raise AutoresearchError("analyzer summary missing: " + ", ".join(sorted(missing)))
    if summary.get("quality_gate") not in {"PASS", "FAIL", "INCONCLUSIVE"}:
        raise AutoresearchError("summary quality_gate must be PASS, FAIL, or INCONCLUSIVE")
    if not isinstance(summary.get("pair_count"), int) or summary["pair_count"] < 1:
        raise AutoresearchError("summary pair_count must be positive integer")

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    evidence_path = EVIDENCE_DIR / f"{eid}-summary.json"
    if evidence_path.exists():
        raise AutoresearchError(f"evaluation evidence already exists: {evidence_path}")
    shutil.copyfile(summary_source, evidence_path)
    record["evaluation"] = {
        "summary_path": evidence_path.relative_to(ROOT).as_posix(),
        "summary_sha256": sha256_file(evidence_path),
        "pair_count": summary["pair_count"],
        "quality_gate": summary["quality_gate"],
        "quality_gate_reason": str(summary["quality_gate_reason"]),
        "median_paired_percent_delta": summary["median_paired_percent_delta"],
        "median_paired_quality_delta": summary["median_paired_quality_delta"],
    }
    record["status"] = "EVALUATED"
    errors = validate_record(record)
    if errors:
        evidence_path.unlink(missing_ok=True)
        raise AutoresearchError("; ".join(errors))
    write_json(path, record)
    registry = load_json(REGISTRY_PATH)
    _registry_entry(registry, eid)["status"] = "EVALUATED"
    write_json(REGISTRY_PATH, registry)


def decide_experiment(eid: str, outcome: str, reason: str) -> None:
    path = experiment_path(eid)
    record = load_json(path)
    if record.get("status") != "EVALUATED":
        raise AutoresearchError("decision may only be recorded for an EVALUATED experiment")
    outcome = outcome.upper()
    if outcome not in DECISIONS:
        raise AutoresearchError("decision must be KEEP, MODIFY, or REMOVE")
    evaluation = record.get("evaluation") or {}
    if outcome == "KEEP" and evaluation.get("quality_gate") != "PASS":
        raise AutoresearchError("KEEP is forbidden unless paired analyzer quality_gate=PASS")
    record["decision"] = {
        "outcome": outcome,
        "reason": reason.strip(),
        "decided_at": now(),
    }
    record["status"] = "DECIDED"
    errors = validate_record(record)
    if errors:
        raise AutoresearchError("; ".join(errors))
    write_json(path, record)
    registry = load_json(REGISTRY_PATH)
    _registry_entry(registry, eid)["status"] = "DECIDED"
    write_json(REGISTRY_PATH, registry)


def list_experiments() -> None:
    registry = load_json(REGISTRY_PATH)
    entries = registry.get("experiments", [])
    if not entries:
        print("No Autoresearch experiments recorded yet.")
        return
    for entry in entries:
        print(f"{entry['experiment_id']}  {entry['status']:<9}  {entry['path']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage Progressive Context Autoresearch experiments.")
    sub = parser.add_subparsers(dest="command", required=True)

    new = sub.add_parser("new", help="Create a PLANNED one-hypothesis experiment")
    new.add_argument("--observation", required=True)
    new.add_argument("--hypothesis", required=True)
    new.add_argument("--change", required=True)
    new.add_argument("--baseline-ref", required=True)
    new.add_argument("--candidate-ref", required=True)
    new.add_argument("--task-set", required=True)
    new.add_argument("--evidence-ref", action="append")
    new.add_argument("--file", action="append")
    new.add_argument("--parent")

    evaluate = sub.add_parser("evaluate", help="Attach paired analyzer summary to a PLANNED experiment")
    evaluate.add_argument("experiment_id")
    evaluate.add_argument("--summary", required=True)

    decide = sub.add_parser("decide", help="Record KEEP/MODIFY/REMOVE on an EVALUATED experiment")
    decide.add_argument("experiment_id")
    decide.add_argument("--decision", required=True, choices=sorted(DECISIONS))
    decide.add_argument("--reason", required=True)

    sub.add_parser("validate", help="Validate registry, records, lifecycle, and evidence hashes")
    sub.add_parser("list", help="List recorded experiments")

    args = parser.parse_args()
    try:
        if args.command == "new":
            eid = create_experiment(args)
            print(f"AUTORESEARCH: CREATED {eid}")
            return 0
        if args.command == "evaluate":
            attach_evaluation(args.experiment_id, Path(args.summary).resolve())
            print(f"AUTORESEARCH: EVALUATED {args.experiment_id}")
            return 0
        if args.command == "decide":
            decide_experiment(args.experiment_id, args.decision, args.reason)
            print(f"AUTORESEARCH: DECIDED {args.experiment_id} -> {args.decision}")
            return 0
        if args.command == "list":
            list_experiments()
            return 0
        if args.command == "validate":
            errors = validate_repository()
            for error in errors:
                print("ERROR:", error)
            if errors:
                print(f"AUTORESEARCH: FAIL ({len(errors)} errors)")
                return 1
            print("AUTORESEARCH: PASS")
            return 0
    except (OSError, AutoresearchError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
