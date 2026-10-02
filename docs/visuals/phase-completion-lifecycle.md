# Phase Completion Lifecycle

Human-only explanatory view. Canonical closeout rules remain in `docs/system/HANDOFF_PROTOCOL.md`.

```mermaid
flowchart TD
    W["Work in current Phase"] --> V{"Acceptance / verification passed?"}
    V -- No --> W
    V -- Yes --> C["Update canonical Architecture / ADR if needed"]
    C --> P["Retain Phase task prompts and observed evidence"]
    P --> R["Write one Phase Completion Report with task IDs"]
    R --> B["Write compact Completion Record"]
    B --> M["Mark ROADMAP phase complete"]
    M --> N["Update NEXT_SESSION with hot state and active prompt pointer"]
    N --> X["Next Phase / next session"]
```

The detailed report preserves durable history. The compact Completion Record is the cross-phase bridge used by normal context routing.
