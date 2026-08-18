# Progressive Context Overview

Human-only explanatory view. Canonical behavior remains in the framework protocols and context compiler.

```mermaid
flowchart TB
    K["AVAILABLE KNOWLEDGE"]
    K --> H["ACTIVE / HOT"]
    K --> C["COLD / ON DEMAND"]

    H --> B["PROJECT_BRIEF"]
    B --> A["ARCHITECTURE"]
    A --> R["ROADMAP"]
    R --> N["NEXT_SESSION"]
    N --> P["current Phase"]
    P --> CR["compact Completion Record"]

    C --> C0["completions/00..."]
    C --> C1["completions/01..."]
    C --> C2["completions/02..."]
```

The framework minimizes **active context**, not available project knowledge. Detailed completion reports stay available for investigation without becoming part of normal warm-up.
