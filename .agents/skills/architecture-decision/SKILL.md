---
name: architecture-decision
description: Material architecture/technology fork with genuinely different strategies.
---

# Architecture Decision

Use only for Decision-worthy work after task classification. Silently weigh architecture,
correctness, effort, testing, security, compatibility, reversibility, and maintenance. Do not expose the full internal analysis.

Present exactly:

**Diagnosis:** core problem, key repository constraint, and main risk in 1–3 sentences.

**Options:**
- **A — Pragmatic / Fast:** smallest effective solution; scope, effort, limitation, and when appropriate.
- **B — Architectural / Robust:** structurally complete solution; scope, effort, long-term benefit, added complexity, and when justified.
- **C — Balanced / Hybrid:** solve the immediate problem plus the single most important structural weakness; what changes now, what stays, effort, and main risk.

Options must be materially different; never invent filler. Then give **My Recommendation:** choose exactly one of A/B/C and tie it to repository maturity, risk, and maintenance cost; never call all options equally valid.

Ask: **“Which path should I implement: A, B, or C? Or describe your own direction.”** Then stop. Do not implement before a direction is chosen unless task classification already exempts the task (e.g. Directed/Trivial).

If the user provides a custom direction, turn it into a coherent approach and proceed. Their direction overrides the recommendation unless it creates serious security, integrity, compatibility, or data-loss risk; then name the risk, propose the nearest safe alternative, and confirm.

## Pivot rule

- Core strategy rejected → stop extending it and return to remaining viable strategies.
- Local detail rejected → preserve approved architecture and revise that detail directly.
- Never pile compatibility patches onto a strategy the user fundamentally rejected.

Create an ADR only for a consequential, hard-to-reverse decision that future maintainers need to understand.
