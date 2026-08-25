#!/usr/bin/env python3
"""Validate cold-start transfer run records against the hidden scenario oracle."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCENARIOS = ROOT / "docs/evals/agent/cold-start/SCENARIOS.json"
SUITE_ID = "cold-start-runtime-transfer-v1"


class ColdStartDataError(ValueError):
    pass


def load_records(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ColdStartDataError("cold-start input is empty")
    if text.startswith("["):
        data = json.loads(text)
        if not isinstance(data, list):
            raise ColdStartDataError("top-level JSON must be an array")
        return data
    records = []
    for line_no, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ColdStartDataError(f"invalid JSONL at line {line_no}: {exc}") from exc
    return records


def load_oracles(path: Path = DEFAULT_SCENARIOS) -> dict[str, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != 1 or data.get("suite_id") != SUITE_ID:
        raise ColdStartDataError("invalid cold-start scenario suite")
    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise ColdStartDataError("cold-start suite has no scenarios")
    out = {}
    for scenario in scenarios:
        sid = scenario.get("id")
        if not isinstance(sid, str) or not sid or sid in out:
            raise ColdStartDataError("scenario ids must be unique non-empty strings")
        if not isinstance(scenario.get("oracle"), dict):
            raise ColdStartDataError(f"scenario {sid} missing oracle")
        out[sid] = scenario["oracle"]
    return out


def _nonempty_string(value, label: str) -> None:
    if not isinstance(value, str) or not value:
        raise ColdStartDataError(f"{label} must be a non-empty string")


def validate_record(record: dict, index: int) -> None:
    label = f"record[{index}]"
    required = (
        "schema", "suite_id", "suite_run_id", "scenario_id", "agent", "model",
        "reasoning", "workflow_ref", "controls", "observation",
    )
    for key in required:
        if key not in record:
            raise ColdStartDataError(f"{label} missing {key}")
    if record["schema"] != 1 or record["suite_id"] != SUITE_ID:
        raise ColdStartDataError(f"{label} has invalid schema/suite_id")
    for key in ("suite_run_id", "scenario_id", "agent", "model", "reasoning", "workflow_ref"):
        _nonempty_string(record[key], f"{label}.{key}")

    controls = record["controls"]
    if not isinstance(controls, dict):
        raise ColdStartDataError(f"{label}.controls must be an object")
    for key in ("repo_snapshot", "prompt_sha256", "tools_profile", "permissions_profile", "environment_profile"):
        _nonempty_string(controls.get(key), f"{label}.controls.{key}")
    if not isinstance(controls.get("fresh_session"), bool):
        raise ColdStartDataError(f"{label}.controls.fresh_session must be boolean")

    observation = record["observation"]
    if not isinstance(observation, dict):
        raise ColdStartDataError(f"{label}.observation must be an object")
    rescue = observation.get("rescue_turns")
    if not isinstance(rescue, int) or isinstance(rescue, bool) or rescue < 0:
        raise ColdStartDataError(f"{label}.observation.rescue_turns must be a non-negative integer")
    skills = observation.get("routed_skills")
    if not isinstance(skills, list) or not all(isinstance(x, str) and x for x in skills):
        raise ColdStartDataError(f"{label}.observation.routed_skills must be a string array")
    if len(skills) != len(set(skills)):
        raise ColdStartDataError(f"{label}.observation.routed_skills must be unique")
    if observation.get("planning_depth") not in {None, "DIRECT", "FOCUSED", "FULL"}:
        raise ColdStartDataError(f"{label}.observation.planning_depth is invalid")
    if not isinstance(observation.get("stopped_for_user_direction"), bool):
        raise ColdStartDataError(f"{label}.observation.stopped_for_user_direction must be boolean")
    checks = observation.get("state_checks")
    if not isinstance(checks, dict) or not all(isinstance(k, str) and isinstance(v, bool) for k, v in checks.items()):
        raise ColdStartDataError(f"{label}.observation.state_checks must map strings to booleans")
    failures = observation.get("hard_failures")
    if not isinstance(failures, list) or not all(isinstance(x, str) and x for x in failures):
        raise ColdStartDataError(f"{label}.observation.hard_failures must be a string array")


def evaluate_record(record: dict, oracle: dict) -> list[str]:
    failures = []
    controls = record["controls"]
    observation = record["observation"]
    skills = set(observation["routed_skills"])

    if not controls["fresh_session"]:
        failures.append("session was not fresh")
    if observation["rescue_turns"] != 0:
        failures.append(f"required {observation['rescue_turns']} rescue turn(s)")

    for skill in oracle.get("required_skills", []):
        if skill not in skills:
            failures.append("required Skill not observed: " + skill)
    for skill in oracle.get("forbidden_skills", []):
        if skill in skills:
            failures.append("forbidden Skill observed: " + skill)

    depths = oracle.get("acceptable_planning_depths", [])
    if depths and observation["planning_depth"] not in depths:
        failures.append(
            "planning depth mismatch: expected " + "/".join(depths) +
            f", got {observation['planning_depth'] or '<none>'}"
        )

    expected_stop = oracle.get("stopped_for_user_direction")
    if isinstance(expected_stop, bool) and observation["stopped_for_user_direction"] != expected_stop:
        failures.append(f"deliberate-stop mismatch: expected {expected_stop}")

    checks = observation["state_checks"]
    for name in oracle.get("required_checks", []):
        if checks.get(name) is not True:
            failures.append("required check failed/missing: " + name)

    failures.extend("hard failure: " + item for item in observation["hard_failures"])
    return failures


def summarize(records: list[dict], scenarios_path: Path = DEFAULT_SCENARIOS) -> dict:
    oracles = load_oracles(scenarios_path)
    grouped: dict[str, list[dict]] = {}
    for index, record in enumerate(records):
        validate_record(record, index)
        if record["scenario_id"] not in oracles:
            raise ColdStartDataError("unknown scenario_id: " + record["scenario_id"])
        grouped.setdefault(record["suite_run_id"], []).append(record)
    if not grouped:
        raise ColdStartDataError("no cold-start records")

    run_summaries = []
    for run_id, run_records in sorted(grouped.items()):
        by_scenario = {}
        for record in run_records:
            sid = record["scenario_id"]
            if sid in by_scenario:
                raise ColdStartDataError(f"suite run {run_id} has duplicate scenario {sid}")
            by_scenario[sid] = record

        first = run_records[0]
        for record in run_records[1:]:
            for field in ("agent", "model", "reasoning", "workflow_ref"):
                if record[field] != first[field]:
                    raise ColdStartDataError(f"suite run {run_id} control mismatch: {field}")
            for key in ("tools_profile", "permissions_profile", "environment_profile"):
                if record["controls"][key] != first["controls"][key]:
                    raise ColdStartDataError(f"suite run {run_id} control mismatch: controls.{key}")

        missing = sorted(set(oracles) - set(by_scenario))
        extra = sorted(set(by_scenario) - set(oracles))
        scenarios = []
        for sid in sorted(oracles):
            if sid not in by_scenario:
                continue
            failures = evaluate_record(by_scenario[sid], oracles[sid])
            scenarios.append(
                {
                    "scenario_id": sid,
                    "gate": "PASS" if not failures else "FAIL",
                    "failures": failures,
                    "rescue_turns": by_scenario[sid]["observation"]["rescue_turns"],
                }
            )
        failed = [x["scenario_id"] for x in scenarios if x["gate"] == "FAIL"]
        gate = "PASS" if not missing and not extra and not failed and len(by_scenario) == len(oracles) else "FAIL"
        run_summaries.append(
            {
                "suite_run_id": run_id,
                "transfer_gate": gate,
                "agent": first["agent"],
                "model": first["model"],
                "reasoning": first["reasoning"],
                "workflow_ref": first["workflow_ref"],
                "expected_scenarios": len(oracles),
                "recorded_scenarios": len(by_scenario),
                "missing_scenarios": missing,
                "extra_scenarios": extra,
                "failed_scenarios": failed,
                "total_rescue_turns": sum(r["observation"]["rescue_turns"] for r in run_records),
                "scenarios": scenarios,
            }
        )

    overall = "PASS" if all(run["transfer_gate"] == "PASS" for run in run_summaries) else "FAIL"
    return {"suite_id": SUITE_ID, "transfer_gate": overall, "runs": run_summaries}


def print_human(summary: dict) -> None:
    print(f"COLD-START TRANSFER: {summary['transfer_gate']} ({len(summary['runs'])} suite run(s))")
    for run in summary["runs"]:
        print(
            f"- {run['suite_run_id']}: {run['transfer_gate']} "
            f"({run['recorded_scenarios']}/{run['expected_scenarios']} scenarios, "
            f"rescue_turns={run['total_rescue_turns']})"
        )
        for scenario in run["scenarios"]:
            if scenario["gate"] == "FAIL":
                print(f"  - {scenario['scenario_id']}: FAIL — {'; '.join(scenario['failures'])}")
        if run["missing_scenarios"]:
            print("  - missing: " + ", ".join(run["missing_scenarios"]))


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze Progressive cold-start transfer records.")
    parser.add_argument("records")
    parser.add_argument("--scenarios", default=str(DEFAULT_SCENARIOS))
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args()
    try:
        summary = summarize(load_records(Path(args.records)), Path(args.scenarios))
    except (OSError, json.JSONDecodeError, ColdStartDataError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.as_json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print_human(summary)
    if args.require_pass and summary["transfer_gate"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
