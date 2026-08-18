# Framework Update Safety

Human-only explanatory view. Installer behavior and regression tests remain executable sources of truth.

```mermaid
flowchart TD
    U["Update framework"] --> F{"File ownership?"}
    F -- "framework-owned" --> A["May update from new Runtime"]
    F -- "project-owned" --> P["Preserve project state"]

    P --> P1[".progressive/project/"]
    P --> P2[".progressive/phases/"]
    P --> P3[".progressive/completions/"]
    P --> P4[".progressive/decisions/"]
    P --> P5["project-specific agent suffixes"]

    A --> V["audit / verify after update"]
    P --> V
```

Framework updates may refresh framework-owned machinery, but project-owned knowledge and completion history must survive unchanged.
