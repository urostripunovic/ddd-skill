# Domain event

**Use when:** something happened in the domain that other parts of the system, or other bounded contexts, react to.

**Never:** name an event after a technical action (`OrderUpdated`, `RowChanged`) or an intention (`PlaceOrder` is a command, not an event).

## Rules

- Named in the past tense, in the ubiquitous language: `OrderPlaced`, `PaymentDeclined`.
- Immutable. Carries the data consumers need, as domain types, and when it happened.
- The timestamp is passed in by the decision function; the event does not read a clock.
- Events of one aggregate form a closed sum type.
- Never carries secrets or more personal data than consumers need. Events are logged and stored for a long time.

## Enforced by

- Go: `//sumtype:decl` on the event interface.
- TypeScript: discriminated union on `type`, handled with `assertNever`.

## Anti-pattern

```ts
type OrderEvent = { name: string; payload: any };
```

Examples: [Go](go/05-domain-event.md) · [TypeScript](ts/05-domain-event.md). Read only the one for your language.

## Corrections

<!-- Add a dated line each time an agent gets this pattern wrong. -->
