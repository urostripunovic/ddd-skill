# The notes tail

A context file ends with three sections, in this order, after every model section. The hash leaves them out, so writing them does not undo an approval. A model section after them is an error.

| Section | Holds | Written by | Cleared by |
|---|---|---|---|
| `## Migration` | numbered steps to move existing code to the model; a finished step ends `(done <date>)` | `ddd-modelling` (ADOPTING.md); `ddd-implementation` marks steps done | not cleared; it is the record |
| `## Amendments` | what implementation learned and settled itself, at standard effective depth | `ddd-implementation` | `ddd-modelling`, folding the rows into the model, then approval again |
| `## Pending` | gaps implementation found and may not settle: the question for the user | `ddd-implementation` | `ddd-modelling`, once the model is approved with the answer |

Amendments are part of the model for every reader: implementation, tickets and reviews read them alongside the rows they amend.
