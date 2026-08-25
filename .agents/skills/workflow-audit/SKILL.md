---
name: workflow-audit
description: Verify Progressive Context integrity at the appropriate layer without loading framework maintenance evidence into normal product work.
activation: explicit
---

# Workflow Audit

First determine whether the current repository is the **Framework Source** itself or an installed **Project Runtime**.

- In Framework Source, run the full static verification suite: inherited behavior contract, Progressive framework contract, routing integrity audit, duplication audit, source audit, context report, and tests.
- In Project Runtime, run only the local runtime audit and task-relevant project validation. Do not load migration/evaluation/framework-development evidence because it is intentionally absent from Runtime.

Report actual commands and results. Do not claim a gate passed unless it ran and passed.
