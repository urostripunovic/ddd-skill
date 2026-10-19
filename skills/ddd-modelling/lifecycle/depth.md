# Depth

Each context file has a `Depth:` line. A missing one means strict. Depth follows what it costs to be wrong, not the kind of project.

| Depth | For | Settled before code |
|---|---|---|
| none | a spike: code that may be thrown away | nothing; recorded under `## Prototypes` |
| `light` | an area where a wrong rule is cheap to find and fix: nothing on the strict list, and no other context reacts to its facts | who may make each request, confirmed; then each rule as a numbered example, asked when a change raises it and written with its test |
| `standard` | most work | the core, confirmed by the user; the rest is a best guess marked `(assumed)` |
| `strict` | money, credentials, authorisation, personal data, anything that cannot be undone, or when the user asks | everything, confirmed and reviewed |

The **core** is what is expensive to change once code exists: the states, the commands and who may issue each, what makes each caller and each fact from outside trusted, the invariants, the aggregate boundaries, and the glossary. The **rest** is everything else: bounds, what a failure or event carries, races, edge cases, examples at the limits. The core is never `(assumed)` and never a placeholder such as "TBD"; `tools/check-model.sh` rejects an "Issued by" cell, an invariant or a "Believed when" cell that is.

A **light** context is a Requests table and an Examples table (`contexts/_light-template.md`), with no approval step. It moves to standard, or strict for the part that needs it, when any of these holds: a request touches something on the strict list, another context reacts to its facts, it gains a second lifecycle, it outgrows about a dozen rows, or the user asks. Moving up is a new core, so it is approved like one.

`Strict commands: A, B` under `Depth:` makes part of a standard context strict. The **strict scope** of each is the command, its failures, the rows that name it (examples, invariants, races, facts from outside, policies) and the primitives of the data it touches; `tools/check-model.sh` prints it. Work inside a strict scope uses strict depth, everything else the context's depth: together, the **effective depth**. A light context has no strict commands.
