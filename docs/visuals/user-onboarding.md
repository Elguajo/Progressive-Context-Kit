# User Onboarding Flow

> Human-only explanatory visual. Framework Source only; not packaged into Project Runtime.

```mermaid
flowchart LR
    A[Download Project Runtime] --> B[Extract into project]
    B --> C[Start Claude Code or Codex]
    C --> D[Describe product idea and real constraints]
    D --> E[PROJECT_BRIEF]
    E --> F[ARCHITECTURE]
    F --> G[ROADMAP]
    G --> H[Current Phase]
    H --> I[Implementation + verification]
```

The user provides the desired outcome and real constraints. Progressive maintains the durable project state and routes the agent into the current work.
