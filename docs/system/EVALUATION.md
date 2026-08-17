# Evaluation

Context/tooling optimization is accepted only when inherited engineering behavior **and** Progressive framework behavior remain intact and real-task quality is non-inferior.

## Static inherited-behavior gate

`tools/behavior_contract.py` validates the 147-rule migration from the original comprehensive Custom Instructions against `docs/evals/static/BEHAVIOR_SCENARIOS.json`.

## Static framework gate

`tools/framework_contract.py` protects Progressive-specific invariants: branded preferred tooling, install-if-useful policy, existing-project adoption, context compiler/manifest, canonical ownership, lineage, and static-vs-agent eval separation.

`tools/duplication_audit.py` guards against copying long canonical policies back into multiple owners.

These gates do **not** execute an LLM.

## Real-agent gate

Use `docs/evals/agent/MODEL_EVAL_PROTOCOL.md`. Compare the same model/reasoning/repository snapshot/tool permissions/task wording/acceptance criteria. Track correctness, grounding, regressions, security, validation truthfulness, unnecessary questions, rework, context size, repeated reads, tool calls, and unsupported success claims.

Never claim an “N× quality improvement” from static prompt structure alone.
