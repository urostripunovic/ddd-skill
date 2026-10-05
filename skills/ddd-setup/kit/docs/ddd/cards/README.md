# Pattern cards

Typed DDD patterns. A card has the rule, what enforces it, an anti-pattern, and the corrections this team has recorded. It has no example code. The examples are in one directory per language, in a file with the card's name:

| Directory | Holds |
|---|---|
| [go/](go/README.md) | Go idioms and check commands, and one example per card |
| [ts/](ts/README.md) | the same for TypeScript |

Every example compiles and passes the applicable reference lint rules in `tools/lint/`. The checker extracts examples into domain directories by default. Examples of workflows, adapters and other boundary code declare `Check as: boundary` and receive the general rules instead of the no-I/O domain rules. Read the cards the task needs, and the examples only for the language being written.

| Card | Load it when |
|---|---|
| [01 Domain primitive](01-domain-primitive.md) | a single value has rules or must not be confused with another |
| [02 Value object](02-value-object.md) | several values only make sense together |
| [03 States as types](03-states-as-types.md) | something has a lifecycle |
| [04 Aggregate as decision functions](04-aggregate-as-decision-functions.md) | implementing a command or business rule |
| [05 Domain event](05-domain-event.md) | recording or publishing that something happened |
| [06 Workflow as function](06-workflow-as-function.md) | wiring a use case: load, decide, persist, publish |
| [07 Parse at the boundary](07-parse-at-the-boundary.md) | data enters from HTTP, a queue, a database or config |
| [08 Repository](08-repository.md) | loading or storing an aggregate |
| [09 Anti-corruption layer](09-anti-corruption-layer.md) | talking to another system or bounded context |
| [10 Errors as values](10-errors-as-values.md) | an operation can fail for a business reason |
| [11 Decider](11-decider.md) | the aggregate is event-sourced, or all its commands should go through one `decide` function |
| [12 Event stream repository](12-event-stream-repository.md) | storing and loading an event-sourced aggregate |
| [13 Facts from outside the aggregate](13-facts-from-outside.md) | a decision needs data the aggregate does not hold: a price, a stock level, whether an email is taken |
| [14 Authorisation](14-authorisation.md) | the model restricts who may issue a command, or on whose data |
| [15 Idempotent command](15-idempotent-command.md) | a command can arrive twice: retries, redelivery, double-clicks |
| [16 Policy](16-policy.md) | an event in one aggregate or context must cause a command in another |
| [17 Read-once secret](17-read-once-secret.md) | handling a password, API key or one-time token |
| [18 Non-empty collection](18-non-empty-collection.md) | the model says "at least one" and the type should carry it |
| [19 Read model](19-read-model.md) | a screen, list, report or search needs data and nothing is decided |
| [20 Event versioning](20-event-versioning.md) | a stored event has to change shape |

## Maintaining the cards

- When an agent gets a pattern wrong, add a dated line under **Corrections** in that card. This is where the cards gain most of their value.
- Replace the generic examples with approved code from your own projects over time.
- After editing an example, run `tools/check-cards.sh` so the cards never teach code that does not compile.

## When no card fits

A card is added when a project has needed the pattern, not before. A card written ahead of a real case teaches a guess.

1. The agent says that no card covers the pattern, names it, and adds a row under **Wanted** below.
2. It implements the code from the core rules in the `ddd-implementation` skill, and the reviews run as usual.
3. Once that code is reviewed and merged, it becomes the card: copy an existing card's headings, put the merged code in the language directory as the example, and run `tools/check-cards.sh`. The check fails while an installed language has no example for a card.
4. Remove the row from **Wanted**.

### Wanted

| Pattern | First needed in | Date |
|---|---|---|
| <!-- Saga with compensation --> | <!-- billing/refund.go --> | <!-- 2026-01-15 --> |
| Property test over command sequences (asked for by `ddd-implementation`) | the first aggregate implemented with the kit | 2026-10-03 |

## Adding a language

A language is a directory here: a `README.md` with the same three headings as the existing ones (idioms, checks, never), and one example per card. Add its extraction and its compile and lint commands to `tools/extract_cards.py` and `tools/check-cards.sh`, and a reference lint config to `tools/lint/`. The cards do not change. `ddd-setup` needs a line for detecting the language and merging its lint config.
