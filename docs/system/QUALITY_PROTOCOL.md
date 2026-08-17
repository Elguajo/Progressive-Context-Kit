# Quality Protocol

Use after implementation and whenever completion claims depend on verification.

## Validation order

Validate from narrowest to broadest, skipping only checks irrelevant to the change:
1. targeted tests / focused reproduction;
2. type check or equivalent static checks;
3. lint and formatting checks;
4. build / compile / package;
5. broader suites when shared code or public interfaces changed;
6. e2e/manual/runtime verification when required by the behavior.

## On failure

Classify each relevant failure as **caused by the change**, **pre-existing**, or
**environmental**. Fix what the change broke, re-run the relevant checks, and do not stop at
the first failure when a safe diagnosable fix is in scope. Do not silently "fix" unrelated
pre-existing failures.

## If validation cannot run

State all four explicitly:
- the exact reason it could not run;
- what was inspected or verified instead;
- the exact command/check the user should run;
- the remaining uncertainty.

A validation claim is supported only by evidence actually observed in the current work.
Never report a check as passed unless it actually ran and passed.
