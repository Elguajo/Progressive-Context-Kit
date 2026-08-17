# Context Protocol

Use the smallest evidence set that can preserve correctness.

Normal product work may use `python3 tools/context_compile.py` to deterministically assemble a compact bundle from Brief, Architecture, Roadmap, current Phase, the immediate predecessor's `Completion Record` when present, and optional `CONTEXT_MANIFEST.json` hints. The compiler output is disposable; canonical files remain source of truth.

The previous-phase bridge is deliberately narrow: include only `## Completion Record`, never the full completed phase by default. Older completed phases remain retrievable when current evidence, an ADR, a regression, or an explicit historical dependency requires them.

Do not automatically read full completed phases, every ADR, all system docs, LINEAGE, migration evidence, eval corpora, or every installed Skill/tool adapter. Load a Skill/protocol/integration adapter only when its trigger matches.

Manifest hints are not authority over code reality. If a required path is stale/missing, report it and ground in repository evidence rather than hallucinating.
