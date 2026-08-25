# Contributing

Keep one canonical behavioral owner per rule/fact. High-frequency universal guarantees may
live in the global layer; long conditional procedures should normally live in Skills/protocols.

If behavior derived from the archived Custom Instructions changes, update the atomic Behavior
Contract and representative scenarios deliberately. Never delete/rename a behavior ID merely
to make the audit green; explain the semantic replacement.

Before submitting changes, run the canonical Framework Source gate:

```bash
python3 tools/gate.py
```

Use individual validators only to diagnose a failed gate or when you are deliberately working
on one validator in isolation. Do not substitute `--skip-unit-tests` for the normal pre-submit
gate.

If `global/AGENTS.codex.md` or the Personal router grows, justify why that behavior must be
always loaded. If it shrinks, prove no Behavior Contract rule or high-frequency guarantee was lost.


## Release artifacts

Framework Source is the only editable source of truth. Do not patch Project Runtime or Starter archives manually. Build the user-facing artifact with `python3 tools/build_release.py`; the release builder invokes the same canonical Source gate before generating and auditing Runtime.
