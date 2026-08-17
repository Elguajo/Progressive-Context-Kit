# Contributing

Keep one canonical behavioral owner per rule/fact. High-frequency universal guarantees may
live in the global layer; long conditional procedures should normally live in Skills/protocols.

If behavior derived from the archived Custom Instructions changes, update the atomic Behavior
Contract and representative scenarios deliberately. Never delete/rename a behavior ID merely
to make the audit green; explain the semantic replacement.

Before submitting changes:

```bash
python3 tools/behavior_contract.py
python3 tools/audit.py
python3 tools/context_report.py --profile personal
python3 tools/sync_profiles.py
python3 tools/sync_skills.py
python3 -m unittest discover -s tools/tests -v
python3 tools/build_starter.py
```

If `global/AGENTS.codex.md` or the Personal router grows, justify why that behavior must be
always loaded. If it shrinks, prove no Behavior Contract rule or high-frequency guarantee was lost.


## Release artifacts

Framework Source is the only editable source of truth. Do not patch Project Runtime or Starter archives manually. Build the user-facing artifact with `python3 tools/build_release.py`; the release workflow uses the same command.
