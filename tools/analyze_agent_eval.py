#!/usr/bin/env python3
"""Validate and compare paired real-agent evaluation records."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

QUALITY_KEYS = (
    "task_correctness",
    "repository_grounding",
    "instruction_adherence",
    "validation_truthfulness",
    "regression_safety",
    "security_approval",
    "decision_quality",
    "question_efficiency",
    "rework_avoidance",
    "context_tool_efficiency",
)

EFFICIENCY_METRICS = (
    "total_tokens",
    "input_tokens",
    "output_tokens",
    "cache_read_tokens",
    "cost_usd",
    "turns",
    "tool_calls",
    "file_reads",
    "wall_time_seconds",
    "initial_context_tokens",
    "peak_context_tokens",
)

CONTROL_FIELDS = ("task_id", "task_class", "agent", "model", "reasoning")
CONTROL_KEYS = (
    "repo_snapshot",
    "task_sha256",
    "acceptance_sha256",
    "tools_profile",
    "permissions_profile",
    "environment_profile",
)


class EvalDataError(ValueError):
    pass


def load_records(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise EvalDataError("evaluation input is empty")
    if text.startswith("["):
        data = json.loads(text)
        if not isinstance(data, list):
            raise EvalDataError("top-level JSON must be an array")
        return data
    records = []
    for line_no, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise EvalDataError(f"invalid JSONL at line {line_no}: {exc}") from exc
    return records


def _number(value, label: str, *, integer: bool = False, nullable: bool = False):
    if value is None and nullable:
        return
    good = (
        isinstance(value, int) and not isinstance(value, bool)
        if integer
        else isinstance(value, (int, float)) and not isinstance(value, bool)
    )
    if not good or value < 0:
        kind = "non-negative integer" if integer else "non-negative number"
        raise EvalDataError(f"{label} must be a {kind}")


def validate_record(record: dict, index: int) -> None:
    label = f"record[{index}]"
    required = (
        "schema", "experiment_id", "pair_id", "arm", "task_id", "task_class",
        "agent", "model", "reasoning", "workflow_ref", "controls", "outcome", "metrics",
    )
    for key in required:
        if key not in record:
            raise EvalDataError(f"{label} missing {key}")
    if record["schema"] != 1:
        raise EvalDataError(f"{label} schema must be 1")
    if record["arm"] not in ("baseline", "candidate"):
        raise EvalDataError(f"{label} arm must be baseline or candidate")
    for key in (
        "experiment_id", "pair_id", "task_id", "task_class", "agent", "model",
        "reasoning", "workflow_ref",
    ):
        if not isinstance(record[key], str) or not record[key]:
            raise EvalDataError(f"{label}.{key} must be a non-empty string")

    controls = record["controls"]
    if not isinstance(controls, dict):
        raise EvalDataError(f"{label}.controls must be an object")
    for key in CONTROL_KEYS:
        if not isinstance(controls.get(key), str) or not controls[key]:
            raise EvalDataError(f"{label}.controls.{key} must be a non-empty string")

    outcome = record["outcome"]
    if not isinstance(outcome, dict) or not isinstance(outcome.get("hard_pass"), bool):
        raise EvalDataError(f"{label}.outcome.hard_pass must be boolean")
    failures = outcome.get("hard_failures")
    if not isinstance(failures, list) or not all(isinstance(x, str) for x in failures):
        raise EvalDataError(f"{label}.outcome.hard_failures must be a string array")
    if outcome["hard_pass"] and failures:
        raise EvalDataError(f"{label} cannot have hard_failures when hard_pass=true")

    quality = outcome.get("quality")
    if not isinstance(quality, dict):
        raise EvalDataError(f"{label}.outcome.quality must be an object")
    for key in QUALITY_KEYS:
        value = quality.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 3:
            raise EvalDataError(f"{label}.outcome.quality.{key} must be integer 0..3")

    metrics = record["metrics"]
    if not isinstance(metrics, dict):
        raise EvalDataError(f"{label}.metrics must be an object")
    for key in ("total_tokens", "wall_time_seconds"):
        _number(metrics.get(key), f"{label}.metrics.{key}")
    for key in ("turns", "tool_calls", "file_reads"):
        _number(metrics.get(key), f"{label}.metrics.{key}", integer=True)
    for key in (
        "input_tokens", "output_tokens", "cache_read_tokens", "cost_usd",
        "initial_context_tokens", "peak_context_tokens",
    ):
        _number(metrics.get(key), f"{label}.metrics.{key}", nullable=True)
    if not isinstance(metrics.get("token_accounting"), str) or not metrics["token_accounting"]:
        raise EvalDataError(f"{label}.metrics.token_accounting must be a non-empty string")


def pair_records(records: list[dict]) -> list[tuple[dict, dict]]:
    grouped: dict[tuple[str, str], dict[str, dict]] = {}
    for index, record in enumerate(records):
        validate_record(record, index)
        key = (record["experiment_id"], record["pair_id"])
        arms = grouped.setdefault(key, {})
        if record["arm"] in arms:
            raise EvalDataError(f"duplicate {record['arm']} for experiment/pair {key}")
        arms[record["arm"]] = record

    pairs = []
    for key, arms in grouped.items():
        if set(arms) != {"baseline", "candidate"}:
            raise EvalDataError(f"pair {key} must contain exactly baseline and candidate")
        baseline, candidate = arms["baseline"], arms["candidate"]
        for field in CONTROL_FIELDS:
            if baseline[field] != candidate[field]:
                raise EvalDataError(f"pair {key} control mismatch: {field}")
        for field in CONTROL_KEYS:
            if baseline["controls"][field] != candidate["controls"][field]:
                raise EvalDataError(f"pair {key} control mismatch: controls.{field}")
        if baseline["metrics"]["token_accounting"] != candidate["metrics"]["token_accounting"]:
            raise EvalDataError(f"pair {key} control mismatch: metrics.token_accounting")
        pairs.append((baseline, candidate))
    return pairs


def quality_mean(record: dict) -> float:
    q = record["outcome"]["quality"]
    return sum(q[key] for key in QUALITY_KEYS) / len(QUALITY_KEYS)


def median(values):
    return statistics.median(values) if values else None


def arm_medians(pairs, arm_index: int) -> dict:
    out = {}
    for metric in EFFICIENCY_METRICS:
        values = [pair[arm_index]["metrics"].get(metric) for pair in pairs]
        values = [float(v) for v in values if v is not None]
        if values:
            out[metric] = median(values)
    out["quality_mean"] = median([quality_mean(pair[arm_index]) for pair in pairs])
    return out


def paired_percent_deltas(pairs) -> dict:
    out = {}
    for metric in EFFICIENCY_METRICS:
        deltas = []
        for baseline, candidate in pairs:
            b = baseline["metrics"].get(metric)
            c = candidate["metrics"].get(metric)
            if b is None or c is None or b == 0:
                continue
            deltas.append((float(c) - float(b)) / float(b) * 100.0)
        if deltas:
            out[metric] = median(deltas)
    return out


def summarize(records: list[dict], quality_tolerance: float = 0.0) -> dict:
    pairs = pair_records(records)
    if not pairs:
        raise EvalDataError("no complete pairs")

    hard_regressions = []
    candidate_hard_failures = []
    quality_deltas = []
    for baseline, candidate in pairs:
        pair_name = f"{baseline['experiment_id']}:{baseline['pair_id']}"
        if baseline["outcome"]["hard_pass"] and not candidate["outcome"]["hard_pass"]:
            hard_regressions.append(pair_name)
        if not candidate["outcome"]["hard_pass"]:
            candidate_hard_failures.append(pair_name)
        if baseline["outcome"]["hard_pass"] and candidate["outcome"]["hard_pass"]:
            quality_deltas.append(quality_mean(candidate) - quality_mean(baseline))

    median_quality_delta = median(quality_deltas)
    if hard_regressions:
        gate = "FAIL"
        reason = "hard regression"
    elif median_quality_delta is not None and median_quality_delta < -quality_tolerance:
        gate = "FAIL"
        reason = "quality non-inferiority threshold exceeded"
    elif candidate_hard_failures:
        gate = "INCONCLUSIVE"
        reason = "candidate has hard failures without a baseline-pass regression"
    elif median_quality_delta is None:
        gate = "INCONCLUSIVE"
        reason = "no both-pass pairs for quality comparison"
    else:
        gate = "PASS"
        reason = "no hard regression and quality threshold satisfied"

    return {
        "pair_count": len(pairs),
        "quality_gate": gate,
        "quality_gate_reason": reason,
        "quality_tolerance": quality_tolerance,
        "hard_regressions": hard_regressions,
        "candidate_hard_failures": candidate_hard_failures,
        "baseline_medians": arm_medians(pairs, 0),
        "candidate_medians": arm_medians(pairs, 1),
        "median_paired_percent_delta": paired_percent_deltas(pairs),
        "median_paired_quality_delta": median_quality_delta,
    }


def print_human(summary: dict) -> None:
    print(f"PAIRED EVAL: {summary['quality_gate']} ({summary['pair_count']} pairs)")
    print(f"Quality gate: {summary['quality_gate_reason']}")
    q = summary["median_paired_quality_delta"]
    print("Median paired quality delta:", "n/a" if q is None else f"{q:+.3f} / 3.000")
    if summary["hard_regressions"]:
        print("Hard regressions:", ", ".join(summary["hard_regressions"]))
    print("\nMedian paired efficiency deltas (candidate vs baseline; lower is better):")
    for key, value in summary["median_paired_percent_delta"].items():
        print(f"  {key}: {value:+.2f}%")
    print("\nArm medians:")
    for arm in ("baseline", "candidate"):
        print(f"  {arm}:")
        for key, value in summary[f"{arm}_medians"].items():
            print(f"    {key}: {value:.3f}")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Analyze paired Progressive Context real-agent eval records."
    )
    ap.add_argument("input", help="JSONL or JSON array of run records")
    ap.add_argument(
        "--quality-tolerance",
        type=float,
        default=0.0,
        help="Allowed median quality drop on the 0..3 mean scale",
    )
    ap.add_argument("--format", choices=("human", "json"), default="human")
    ap.add_argument("--require-pass", action="store_true", help="Return exit 1 unless quality_gate=PASS")
    args = ap.parse_args()
    if args.quality_tolerance < 0:
        print("ERROR: --quality-tolerance must be >= 0", file=sys.stderr)
        return 2
    try:
        summary = summarize(load_records(Path(args.input)), args.quality_tolerance)
    except (OSError, json.JSONDecodeError, EvalDataError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print_human(summary)
    if args.require_pass and summary["quality_gate"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
