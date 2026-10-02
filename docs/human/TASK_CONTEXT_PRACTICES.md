# Task Continuity and Context Economy

Human-only research and implementation evidence; Framework Source only, not a Runtime dependency.
Reviewed public upstream sources on 2026-10-03. Links follow upstream main and may change.

## Comparable practices

| Project | Observed practice | Useful here | Limitation |
| --- | --- | --- | --- |
| [GitHub Spec Kit](https://github.com/github/spec-kit/blob/main/templates/commands/implement.md) | Implementation starts with prerequisite/checklist checks and reads feature-local tasks, plan and applicable supporting artifacts. | Durable task IDs, acceptance and prerequisite reconciliation. | Its implementation read set is broader than a single task; copying it wholesale would increase our context. |
| [GSD state template](https://github.com/gsd-build/get-shit-done/blob/main/get-shit-done/templates/state.md), [execution workflow](https://github.com/gsd-build/get-shit-done/blob/main/get-shit-done/workflows/execute-plan.md) | STATE is a digest limited to 100 lines. Phase PLAN is executed and paired with SUMMARY; execution initialization requests paths to reduce orchestrator context. | Keep navigation small; preserve phase-local intent and observed result separately from hot state. | Full workflow/model/commit policies are unnecessary for our portable continuity layer. |
| [GSD resume workflow](https://github.com/gsd-build/get-shit-done/blob/main/get-shit-done/workflows/resume-project.md), [summary template](https://github.com/gsd-build/get-shit-done/blob/main/get-shit-done/templates/summary.md) | Resume checks interrupted work, plans without summaries and handoff divergence against Git. Summary metadata supports selecting relevant dependencies without reading every full summary. | Reconcile saved navigation with live evidence; use references and small cross-phase summaries. | A missing summary is a signal to investigate, not proof that no implementation exists. |
| [OpenSpec concepts](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md), [commands](https://github.com/Fission-AI/OpenSpec/blob/main/docs/commands.md) | Current specs are distinct from change-local proposal/design/tasks/deltas. Archived changes preserve intent/history. Apply resumes incomplete tasks; verify compares implementation with artifacts. | Preserve task intent/history without making it current project truth. | Verification and artifact coherence do not automatically establish that an old prompt remains authorized/applicable today. |
| [Superpowers task execution](https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md) | One task brief supplies exact requirements; dispatch contains pointers and essential interfaces, not the whole plan or accumulated prior-task history. Reports are files with compact return messages. | Read one task, pass references, avoid duplicating instruction/evidence bodies. | Fresh task contexts/reviews have an orchestration cost; they are not an automatic token-saving policy for tiny work. |

These are observed mechanisms, not evidence that one framework is universally cheaper or more reliable.
The per-execution semantic freshness check and preservation of executed prompt revisions below
are our adaptation to this user's requirement, not a claim that all upstream projects implement it.

## Applied design

- Phase plan owns current tasks/acceptance and points to one adjacent `<phase-name>.prompts.md`
  archive. The archive retains original requests, executed prompt revisions and observed evidence.
- NEXT_SESSION contains current navigation plus `<phase-name>.prompts.md#task-id`; it does not
  carry another editable copy of the task instructions. Unchanged instructions retain their ID.
- The compiled execution view contains task/status/revision metadata, full Prompt, latest
  Freshness check and Current checkpoint. Original Request and accumulated Outcome / evidence
  stay retrievable as cold history. Changed instructions create linked replacement revisions.
- Default context stays bounded as task history grows. Oversized instructions become explicit
  pointers rather than truncated requirements; compact checkpoints point to detailed evidence.
- `context_compile.py --task-only` emits a task delta within an already-grounded session.
  Cold start/context loss still requires the normal read set; affected canonical constraints
  must be reread when changed. No token saving may bypass acceptance, authorization or validation.
- Manifest paths already included are deduplicated. Prompt archives remain pointers even when
  listed in the manifest. Mechanical substeps do not get individual records or files.

Lifecycle and freshness owners: [Handoff Protocol](../system/HANDOFF_PROTOCOL.md) and
[Context Protocol](../system/CONTEXT_PROTOCOL.md). This research report is not another policy owner.

## Observed context-size evidence

Reproducible synthetic fixture: `tools/tests/test_task_prompts.py`,
`test_adjacent_archive_keeps_context_constant_as_history_grows`. Same plan, target and acceptance;
add 100 completed records, a long original request and old evidence to the archive.

| Character count | Initial archive | After adding cold history |
| --- | ---: | ---: |
| Saved archive | 269 | 184,786 |
| Full compiled fixture context | 792 | 792 |
| Task-only fixture context | 414 | 414 |

The regression asserts identical compiled output before/after, and verifies Runtime packaging,
archive preservation on framework update, pointer ownership and exclusion of historical bodies.
This measures selection/isolation on a synthetic fixture. Character counts are not tokenizer
counts, billable-token measurements, representative production workloads or empirical agent
accuracy results. No fixed percentage of monetary savings is claimed.

## Further economy without speculative machinery

Prefer bounded code/search output, task-specific source/test slices and pointers to long logs.
Avoid rereading unchanged context within a session and repeating a full review after a narrow fix
without a new risk. Cache routing/navigation only as a hint; evidence of task freshness must still
be checked. Do not add vector retrieval, an extra state ledger, a tokenizer dependency, automatic
subagent dispatch or global configuration merely to shrink these small Markdown bundles.
