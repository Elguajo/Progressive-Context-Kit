---
name: project-bootstrap
description: Initialize Progressive Context Spec Kit for a new/greenfield product.
activation: automatic
requires: ["prompts/START_NEW_PROJECT.md", "docs/system/PLANNING_DEPTH.md"]
may_delegate: ["existing-project-adoption"]
---

# Project Bootstrap

Use `prompts/START_NEW_PROJECT.md` and `docs/system/PLANNING_DEPTH.md`. Select the smallest sufficient `DIRECT`, `FOCUSED`, or `FULL` planning depth before creating durable specifications. Create compact canonical project state at that depth, choose architecture pragmatically, create only necessary phases with exactly one current marker, select/tool-bootstrap a justified tooling profile, and begin implementation unless a user-only blocker exists. Escalate depth when evidence increases uncertainty/risk/reach; never use depth reduction to bypass required engineering or safety work. For an existing product repository, use `existing-project-adoption` instead.
