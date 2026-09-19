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

WORKFLOW_EVIDENCE_KEYS = (
    "artifact_refs",
    "project_state_refs",
    "command_result_refs",
    "verification_refs",
    "tool_trace_refs",
)

JUDGE_RECORD_FIELDS = frozenset({
    "schema", "experiment_id", "pair_id", "judge", "artifacts", "rubric_ref", "scores",
    "hard_failures", "preference", "confidence", "notes",
})
JUDGE_IDENTIFICATION_FIELDS = frozenset({"agent", "model", "reasoning"})
ANONYMOUS_ARTIFACTS = ("A", "B")

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


def load_anonymous_pair_map(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    """Load the control-only arm map; it is never part of judge-visible input."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvalDataError(f"invalid anonymous pair map: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema") != 1 or not isinstance(data.get("pairs"), list):
        raise EvalDataError("anonymous pair map must be an object with schema=1 and pairs")
    result: dict[tuple[str, str], dict[str, str]] = {}
    for index, item in enumerate(data["pairs"]):
        if not isinstance(item, dict):
            raise EvalDataError(f"anonymous pair map pair[{index}] must be an object")
        experiment_id, pair_id, mapping = item.get("experiment_id"), item.get("pair_id"), item.get("mapping")
        if not isinstance(experiment_id, str) or not experiment_id or not isinstance(pair_id, str) or not pair_id:
            raise EvalDataError(f"anonymous pair map pair[{index}] needs experiment_id and pair_id")
        if not isinstance(mapping, dict) or set(mapping) != {"baseline", "candidate"}:
            raise EvalDataError(f"anonymous pair map pair[{index}] mapping must contain baseline and candidate")
        if {mapping["baseline"], mapping["candidate"]} != {"A", "B"}:
            raise EvalDataError(f"anonymous pair map pair[{index}] must map baseline/candidate to A/B")
        key = (experiment_id, pair_id)
        if key in result:
            raise EvalDataError(f"duplicate anonymous pair map entry for {key}")
        result[key] = mapping
    return result


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

    evidence = record.get("evidence")
    if evidence is not None:
        validate_workflow_evidence(evidence, f"{label}.evidence")


def validate_workflow_evidence(evidence: object, label: str) -> None:
    if not isinstance(evidence, dict) or set(evidence) != set(WORKFLOW_EVIDENCE_KEYS):
        raise EvalDataError(f"{label} must contain exactly the canonical evidence references")
    for key in WORKFLOW_EVIDENCE_KEYS:
        refs = evidence[key]
        if not isinstance(refs, list) or not all(isinstance(ref, str) and ref for ref in refs):
            raise EvalDataError(f"{label}.{key} must be a string array")
        if key != "tool_trace_refs" and not refs:
            raise EvalDataError(f"{label}.{key} must contain at least one reference")


def has_workflow_evidence(record: dict) -> bool:
    try:
        validate_workflow_evidence(record.get("evidence"), "evidence")
    except EvalDataError:
        return False
    return True


def _validate_quality(quality: object, label: str) -> None:
    if not isinstance(quality, dict) or set(quality) != set(QUALITY_KEYS):
        raise EvalDataError(f"{label} must contain exactly the canonical quality dimensions")
    for key in QUALITY_KEYS:
        value = quality[key]
        if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 3:
            raise EvalDataError(f"{label}.{key} must be integer 0..3")


def validate_judge_record(record: dict, index: int) -> None:
    label = f"judge_record[{index}]"
    if not isinstance(record, dict) or set(record) != JUDGE_RECORD_FIELDS:
        raise EvalDataError(f"{label} must contain exactly the blinded judge record fields")
    if record["schema"] != 1:
        raise EvalDataError(f"{label}.schema must be 1")
    for key in ("experiment_id", "pair_id", "rubric_ref", "notes"):
        if not isinstance(record[key], str) or not record[key]:
            raise EvalDataError(f"{label}.{key} must be a non-empty string")
    judge = record["judge"]
    if not isinstance(judge, dict) or set(judge) != JUDGE_IDENTIFICATION_FIELDS:
        raise EvalDataError(f"{label}.judge must identify agent, model, and reasoning")
    if not all(isinstance(judge[key], str) and judge[key] for key in judge):
        raise EvalDataError(f"{label}.judge values must be non-empty strings")
    if record["artifacts"] != list(ANONYMOUS_ARTIFACTS):
        raise EvalDataError(f"{label}.artifacts must be ordered anonymous labels A, B")
    scores, failures = record["scores"], record["hard_failures"]
    if not isinstance(scores, dict) or set(scores) != set(ANONYMOUS_ARTIFACTS):
        raise EvalDataError(f"{label}.scores must contain A and B")
    if not isinstance(failures, dict) or set(failures) != set(ANONYMOUS_ARTIFACTS):
        raise EvalDataError(f"{label}.hard_failures must contain A and B")
    for artifact in ANONYMOUS_ARTIFACTS:
        _validate_quality(scores[artifact], f"{label}.scores.{artifact}")
        if not isinstance(failures[artifact], list) or not all(isinstance(item, str) and item for item in failures[artifact]):
            raise EvalDataError(f"{label}.hard_failures.{artifact} must be a string array")
    if record["preference"] not in {"A", "B", "TIE", "INCONCLUSIVE"}:
        raise EvalDataError(f"{label}.preference is invalid")
    if record["confidence"] not in {"LOW", "MEDIUM", "HIGH"}:
        raise EvalDataError(f"{label}.confidence is invalid")


def blinded_judgments(
    pairs: list[tuple[dict, dict]], judge_records: list[dict], anonymous_pair_map: dict[tuple[str, str], dict[str, str]]
) -> dict[tuple[str, str], dict]:
    judgments: dict[tuple[str, str], dict] = {}
    expected = {(baseline["experiment_id"], baseline["pair_id"]) for baseline, _ in pairs}
    for index, record in enumerate(judge_records):
        validate_judge_record(record, index)
        key = (record["experiment_id"], record["pair_id"])
        if key in judgments:
            raise EvalDataError(f"duplicate blinded judge record for {key}")
        judgments[key] = record
    if set(judgments) != expected:
        raise EvalDataError("blinded judge records must cover exactly the analyzed pairs")
    if set(anonymous_pair_map) != expected:
        raise EvalDataError("anonymous pair map must cover exactly the analyzed pairs")
    return judgments


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


def quality_mean_scores(scores: dict) -> float:
    return sum(scores[key] for key in QUALITY_KEYS) / len(QUALITY_KEYS)


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


def summarize(
    records: list[dict],
    quality_tolerance: float = 0.0,
    *,
    judge_records: list[dict] | None = None,
    anonymous_pair_map: dict[tuple[str, str], dict[str, str]] | None = None,
    require_workflow_evidence: bool = False,
) -> dict:
    pairs = pair_records(records)
    if not pairs:
        raise EvalDataError("no complete pairs")

    if (judge_records is None) != (anonymous_pair_map is None):
        raise EvalDataError("blinded judging requires both judge records and anonymous pair map")
    if require_workflow_evidence:
        if judge_records is None:
            raise EvalDataError("workflow claims require blinded judge records and anonymous pair map")
        missing_evidence = [
            f"{record['experiment_id']}:{record['pair_id']}:{record['arm']}"
            for record in records
            if not has_workflow_evidence(record)
        ]
        if missing_evidence:
            raise EvalDataError("workflow claims require non-self-report evidence for every run: "+", ".join(missing_evidence))
    judgments = (
        blinded_judgments(pairs, judge_records, anonymous_pair_map)
        if judge_records is not None and anonymous_pair_map is not None
        else None
    )

    hard_regressions = []
    candidate_hard_failures = []
    quality_deltas = []
    judged_preferences: dict[str, int] = {}
    for baseline, candidate in pairs:
        pair_name = f"{baseline['experiment_id']}:{baseline['pair_id']}"
        if judgments is None:
            baseline_pass = baseline["outcome"]["hard_pass"]
            candidate_pass = candidate["outcome"]["hard_pass"]
            baseline_quality = quality_mean(baseline)
            candidate_quality = quality_mean(candidate)
        else:
            key = (baseline["experiment_id"], baseline["pair_id"])
            judgment = judgments[key]
            mapping = anonymous_pair_map[key]
            baseline_artifact, candidate_artifact = mapping["baseline"], mapping["candidate"]
            baseline_pass = not judgment["hard_failures"][baseline_artifact]
            candidate_pass = not judgment["hard_failures"][candidate_artifact]
            baseline_quality = quality_mean_scores(judgment["scores"][baseline_artifact])
            candidate_quality = quality_mean_scores(judgment["scores"][candidate_artifact])
            preference = judgment["preference"]
            judged_preferences[preference] = judged_preferences.get(preference, 0) + 1
        if baseline_pass and not candidate_pass:
            hard_regressions.append(pair_name)
        if not candidate_pass:
            candidate_hard_failures.append(pair_name)
        if baseline_pass and candidate_pass:
            quality_deltas.append(candidate_quality - baseline_quality)

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
        "quality_evidence": "blinded_judge_records" if judgments is not None else "run_record_outcomes",
        "judge_preferences": judged_preferences,
        "workflow_evidence_required": require_workflow_evidence,
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
    ap.add_argument("--judge-records", help="JSONL or JSON blinded judge records for the same pairs")
    ap.add_argument("--anonymous-pair-map", help="Control-only JSON map from arms to anonymous A/B artifacts")
    ap.add_argument("--require-judge", action="store_true", help="Fail unless blinded judge evidence is supplied")
    ap.add_argument(
        "--require-workflow-evidence",
        action="store_true",
        help="Require blinded judge evidence plus artifact/project-state/command/verification references for every run",
    )
    args = ap.parse_args()
    if args.quality_tolerance < 0:
        print("ERROR: --quality-tolerance must be >= 0", file=sys.stderr)
        return 2
    if bool(args.judge_records) != bool(args.anonymous_pair_map):
        print("ERROR: --judge-records and --anonymous-pair-map must be supplied together", file=sys.stderr)
        return 2
    if args.require_judge and not args.judge_records:
        print("ERROR: --require-judge needs blinded judge records and anonymous pair map", file=sys.stderr)
        return 2
    if args.require_workflow_evidence and not args.require_judge:
        print("ERROR: --require-workflow-evidence requires --require-judge", file=sys.stderr)
        return 2
    try:
        judges = load_records(Path(args.judge_records)) if args.judge_records else None
        pair_map = load_anonymous_pair_map(Path(args.anonymous_pair_map)) if args.anonymous_pair_map else None
        summary = summarize(
            load_records(Path(args.input)),
            args.quality_tolerance,
            judge_records=judges,
            anonymous_pair_map=pair_map,
            require_workflow_evidence=args.require_workflow_evidence,
        )
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
