# Phase Completion Lifecycle

Human-only explanatory view. Canonical closeout rules remain in `docs/system/HANDOFF_PROTOCOL.md`.

```mermaid
flowchart TD
    W["Work in current Phase"] --> V{"Acceptance / verification passed?"}
    V -- No --> W
    V -- Yes --> C["Update canonical Architecture / ADR if needed"]
    C --> R["Write one Phase Completion Report"]
    R --> B["Write compact Completion Record"]
    B --> M["Mark ROADMAP phase complete"]
    M --> N["Overwrite NEXT_SESSION with hot continuation state"]
    N --> X["Next Phase / next session"]
```

The detailed report preserves durable history. The compact Completion Record is the cross-phase bridge used by normal context routing.
