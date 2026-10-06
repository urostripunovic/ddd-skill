# When code learns what the model did not say

The core, the rest and effective depth are defined in [depth.md](depth.md); the `## Pending` and `## Amendments` sections in [notes-tail.md](notes-tail.md).

Decide by what the gap is and the effective depth.

- **A gap in the core** (a missing state, command or invariant, who may issue a command, an aggregate boundary, two rules that contradict each other), at any depth: stop. Add a `## Pending` row, propose the change, and wait. The change goes through `ddd-modelling` and approval.
- **A gap in the rest at strict effective depth**: the same.
- **A gap in the rest at standard effective depth**: decide the least surprising behaviour consistent with the stated rules, implement it with a test, and add an `## Amendments` row: the section, what the model said (or "nothing"), what was learned, what the code now does. Do not edit the model above the tail.
- **Unless** a wrong guess could lose money or data, expose something, or be hard to undo, or a confirmed example (one not marked `(assumed)`) does not hold: then stop and ask, as for the core.

Something marked `(assumed)` is implemented as written. If it cannot hold, that is a gap in the rest.
