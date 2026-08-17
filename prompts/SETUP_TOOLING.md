# Setup Preferred Tooling

Use only when tooling setup materially improves the project or the selected profile requires it.

1. Read `integrations/TOOL_REGISTRY.json`, `integrations/PROFILES.md`, and `docs/project/TOOLING_STATUS.json`.
2. Determine Tier/Risk from Project Brief/Architecture/current phase; choose Minimal, Recommended, or Advanced Spec profile.
3. Probe what can be safely detected locally and inspect active agent capabilities/configuration without exposing secrets.
4. For each materially useful preferred tool that is absent/unconfigured, consult its **current official source** before proposing installation. Do not trust stale commands embedded in old docs.
5. Group compatible installation/configuration changes into one concise approval request. Explain user/global files, hooks, credentials/API keys, downloads, or external services involved. RTK global hooks always require explicit confirmation.
6. After approval, install/configure only the approved tools, verify them, and persist status/evidence/version when available.
7. If declined/unavailable, record `declined`/`degraded` and use the documented fallback. Do not repeatedly ask in every session.
8. Never block a tiny local task merely because optional tooling is absent.
