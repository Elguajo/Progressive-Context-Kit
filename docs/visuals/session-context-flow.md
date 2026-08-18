# Session Context Flow

> Human-only explanatory visual. Framework Source only; not packaged into Project Runtime.

```mermaid
flowchart TD
    A[Fresh session] --> B[Repository behavior / router]
    B --> C[Project Brief]
    C --> D[Architecture]
    D --> E[Roadmap]
    E --> F[Current Phase]
    F --> G[Relevant code + tests + matching Skill]
    G --> H{Need older implementation detail?}
    H -- No --> I[Work]
    H -- Yes --> J[Read specific cold history on demand]
    J --> I
    I --> K[Verification]
    K --> L[Handoff]
    L --> M[Overwrite NEXT_SESSION]
```

Normal startup stays bounded. Detailed historical material is pulled only when evidence requires it.
