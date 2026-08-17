# Framework Change Control

Framework-owned: root adapters, `global/`, `profiles/`, skills, prompts, templates,
`docs/system/`, `docs/contracts/`, migration/eval docs, integrations, and tools.

Project-owned after initialization: `docs/project/*`, `docs/phases/*`, `docs/decisions/*`,
application code/tests/migrations/configuration.

Framework updates must preserve project-owned state. Run audit/tests after changes.
