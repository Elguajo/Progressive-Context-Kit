# Tool and Skill Routing

> Human-only explanatory visual. Framework Source only; not packaged into Project Runtime.

```mermaid
flowchart TD
    A[Task arrives] --> B{What kind of work is this?}
    B -->|Implementation| C[implementation-execution]
    B -->|Review| D[code-review]
    B -->|Unknown root cause| E[systematic-debugging]
    B -->|Architecture choice| F[architecture-decision]
    B -->|Security-sensitive| G[security-sensitive-change]
    B -->|End of meaningful session| H[session-handoff]

    C --> I[Load only relevant project context + code/tests]
    D --> I
    E --> I
    F --> I
    G --> I
    H --> I

    J[Installed / available Skills] -. not automatically loaded .-> B
```

**Installed does not mean loaded. Available does not mean active context.** Routing should activate only the workflow support that materially helps the current task.
