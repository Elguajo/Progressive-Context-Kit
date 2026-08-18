# Project Memory Model

> Human-only explanatory visual. Framework Source only; not packaged into Project Runtime.

```mermaid
flowchart TB
    subgraph T[Current truth]
        B[PROJECT_BRIEF\nwhat are we building?]
        A[ARCHITECTURE\nhow does it work now?]
        R[ROADMAP\nwhat comes next?]
    end

    subgraph E[Execution]
        P[Current Phase\nwhat are we doing now?]
    end

    subgraph H[History and continuity]
        CR[Completion Record\ncompact cross-phase bridge]
        CP[Completion Report\ndetailed phase history]
        ADR[ADR\nwhy a consequential decision was made]
        NS[NEXT_SESSION\nvolatile next action]
    end

    B --> A --> R --> P
    P --> CR
    P --> CP
    P --> NS
    A -. consequential rationale .-> ADR
    CR --> R
```

Each durable fact should have one canonical owner. Completion reports explain what happened; they do not replace current truth in Brief, Architecture, Roadmap, or ADRs.
