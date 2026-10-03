# Updating Project Runtime Safely

> **Human-only documentation.** Framework Source only; excluded from Project Runtime.
>
> Russian: [`UPDATING_RUNTIME.ru.md`](UPDATING_RUNTIME.ru.md)

Project Runtime updates must preserve project-owned state while replacing only framework-owned runtime material.

Visual boundary: [`../visuals/framework-update-safety.md`](../visuals/framework-update-safety.md)

## The rule

```text
framework-owned → may be updated
project-owned   → must be preserved
```

Project-owned state includes, among other project data:

- `.progressive/project/` durable project state;
- `.progressive/phases/`;
- `.progressive/completions/`;
- `.progressive/decisions/`;
- project-specific instruction suffixes preserved by the installer;
- application/source files.

Do not update a real project by blindly extracting a new Runtime ZIP over the project and hoping file collisions are harmless.

## Preferred update path

From a trusted Framework Source checkout, use the installer/update mechanism rather than manual replacement:

```bash
python3 tools/init_project.py /path/to/project --update-framework --dry-run
python3 tools/init_project.py /path/to/project --update-framework
```

Use `--dry-run` first when the project matters or when moving across a meaningful framework change.

## Older instruction compatibility

The installer recognizes historical standard Personal/Standalone profiles by exact fingerprints
in `tools/legacy_agent_profiles.json`, shipped with Framework Source. Recognition needs no Git
or network. User text appended after a verified standard prefix is preserved under the
`PROJECT-SPECIFIC-INSTRUCTIONS` boundary.

New installations and generated Runtime entrypoints already contain that boundary. Put local
instructions after it. Inline edits to an unmarked framework prefix require manual reconciliation
and are never automatically overwritten. Update checks both AGENTS.md and CLAUDE.md before
writing any files. `--dry-run` performs the same checks and fails for unknown instruction formats.

The catalog is source-only compatibility evidence, not agent warm-up context. When extending
compatibility, record the exact runtime-rendered standard prefix fingerprint (universal newlines,
`rstrip()`), character length and source commit. Do not add user-specific variants or recognize
ownership only by a heading or declared version.

## What to verify after an update

Run:

```bash
python3 .progressive/tools/audit.py --root .
python3 .progressive/tools/context_compile.py --root .
```

Then confirm:

- current project state still matches reality;
- phases, completion reports, decisions, and source files were preserved;
- root agent instructions still include any project-specific preserved suffix;
- normal context remains bounded;
- historical completion reports remain on-demand rather than entering warm-up.

## When to stop

If an update produces a collision in project-owned state, an unrecognized root instruction file, or another ambiguity that could destroy project intent, stop instead of forcing the overwrite.

A safe update is one that can explain exactly which framework-owned files changed and can show that project-owned state remained intact.
