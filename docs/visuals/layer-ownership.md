# Layer Ownership Map

Human-only explanatory view. Canonical ownership rules remain in `docs/system/LAYER_OWNERSHIP.md`.

```mermaid
flowchart LR
    B["PROJECT_BRIEF\nproduct / scope"]
    A["ARCHITECTURE\ncurrent system truth"]
    R["ROADMAP\nphase order + status"]
    P["CURRENT PHASE\nexecution + acceptance"]
    C["COMPLETION RECORD\ncompact cross-phase bridge"]
    H["COMPLETION REPORT\ndetailed historical result"]
    D["ADR\ndecision rationale"]
    N["NEXT_SESSION\nvolatile hot navigation"]

    B --> A --> R --> P
    P --> C
    P --> H
    A -. consequential decision .-> D
    C --> N
```

One durable fact should have one canonical owner. Completion reports preserve what happened; they do not replace current Architecture, Brief, Roadmap, or ADR truth.
