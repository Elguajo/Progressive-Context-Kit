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
instructions after it for simpler upgrades. Inline edits are also preserved through three-way
merging: pristine installed instructions + your current file + the new standard. Independent
line edits are combined, including your additions, replacements and deletions; identical edits
are applied once. Overlapping incompatible edits stop the update before any file is written.
The boundary alone does not authorize replacement.

New installs, successful updates and generated Runtime ZIPs save the pristine framework prefixes
in `.progressive/INSTRUCTION_BASE.json`. This is cold updater metadata and is not loaded into
normal agent context. It never records your custom merged prefix as the new standard, so future
updates continue to preserve your rules.

For an older project with inline edits and no saved original, provide the directory from the
**exact pristine Runtime you originally installed** (extract the old ZIP separately):

```bash
python3 tools/init_project.py /path/to/project --update-framework --instruction-base /path/to/original-runtime --dry-run
python3 tools/init_project.py /path/to/project --update-framework --instruction-base /path/to/original-runtime
```

That directory must contain original `AGENTS.md` and `CLAUDE.md`, without local suffixes.
Do not use the modified project or a guessed/latest Runtime as the original. Without a reliable
base, modified unknown prefixes still require manual reconciliation. Standard legacy profiles
and their appended rules continue to update without this option.

Update checks both instruction files before writing; `--dry-run` uses the same merge and displays
the proposed instruction diff without saving it. Conflicts display a diff against the new standard,
which may include framework version differences. Resolve overlapping rules deliberately; do not
copy the whole older framework prefix into the project-specific section.

Before an update replaces either instruction file, it saves both existing entrypoints, byte for
byte, together with the existing instruction base, in a new
`.progressive/update-backup/instructions-<unique-id>/` directory and prints its path. Earlier
backups are preserved. If creating the backup fails, instruction replacement does
not start. Dry runs, rejected updates, and updates with unchanged instruction files create no
backup. These copies protect root instructions; they are not full-project rollback snapshots.

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
