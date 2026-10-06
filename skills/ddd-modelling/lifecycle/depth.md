# Depth

Each context file has a `Depth:` line. A missing one means strict.

| Depth | For | Settled before code |
|---|---|---|
| none | a spike: code that may be thrown away | nothing; recorded under `## Prototypes` |
| `standard` | most work | the core, confirmed by the user; the rest is a best guess marked `(assumed)` |
| `strict` | money, credentials, authorisation, personal data, anything that cannot be undone, or when the user asks | everything, confirmed and reviewed |

The **core** is what is expensive to change once code exists: the states, the commands and who may issue each, the invariants, the aggregate boundaries, and the glossary. The **rest** is everything else: bounds, what a failure or event carries, races, edge cases, examples at the limits. The core is never `(assumed)` and never a placeholder such as "TBD"; `tools/check-model.sh` rejects an "Issued by" cell or invariant that is.

`Strict commands: A, B` under `Depth:` makes part of a standard context strict. The **strict scope** of each is the command, its failures, the rows that name it (examples, invariants, races, facts from outside, policies) and the primitives of the data it touches; `tools/check-model.sh` prints it. Work inside a strict scope uses strict depth, everything else the context's depth: together, the **effective depth**.
