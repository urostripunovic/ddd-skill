# Aggregate as data plus decision functions

**Use when:** a group of data must stay consistent together and changes to it follow business rules.

**Never:** a class or struct with mutating methods and setters, or business rules in an HTTP handler or a "service" that pokes at fields.

## Rules

- The aggregate is immutable data. See [states as types](03-states-as-types.md).
- A decision function takes the current state and the command's data, and returns the new state, the events, or an error.
- Decision functions are pure: no I/O, no clock, no randomness. Time and generated IDs come in as parameters.
- When a decision needs data the aggregate does not hold, the workflow fetches it first and passes it in as a value. See [facts from outside the aggregate](13-facts-from-outside.md).
- The function takes the specific state type it applies to. `Place(DraftOrder)` cannot be called with a placed order.
- A command that is legal in several states takes exactly those states, as a narrower sum type. See [states as types](03-states-as-types.md).
- "Wrong state" is therefore not a failure a decision function can return. It is handled in the workflow, where the loaded aggregate is narrowed. See [workflow as function](06-workflow-as-function.md).
- Other aggregates are referenced by ID, never embedded.
- One transaction changes one aggregate.
- For an event-sourced aggregate, wrap these functions in a [decider](11-decider.md).

## Enforced by

- Both: the parameter type. An illegal transition does not compile.
- Go: defensive copy of slices, since Go cannot enforce immutability.
- TypeScript: `readonly` on every field and array.

## Anti-pattern

```go
func (o *Order) SetStatus(s string) { o.Status = s }
```

Examples: [Go](go/04-aggregate-as-decision-functions.md) · [TypeScript](ts/04-aggregate-as-decision-functions.md). Read only the one for your language.

## Corrections

<!-- Add a dated line each time an agent gets this pattern wrong. -->
