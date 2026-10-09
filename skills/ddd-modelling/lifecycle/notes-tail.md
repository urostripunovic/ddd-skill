# The notes tail

A context file ends with three sections, in this order, after every model section. They are written after approval, and writing them does not undo it. A model section after them is an error.

| Section | Holds | Written by | Cleared by |
|---|---|---|---|
| `## Migration` | numbered steps to move existing code to the model; a finished step ends `(done <date>)` | `ddd-modelling` (ADOPTING.md); `ddd-implementation` marks steps done | not cleared; it is the record |
| `## Amendments` | changes to the rest of an approved model at standard effective depth: what implementation learned and settled, or what the user changed | `ddd-implementation`; `ddd-modelling` for a change the user asks for | `ddd-modelling`, folding the rows into the model, then approval again |
| `## Pending` | gaps implementation found and may not settle: the question for the user | `ddd-implementation` | `ddd-modelling`, once the model is approved with the answer |

Amendments are part of the model for every reader: implementation, tickets and reviews read them alongside the rows they amend.
