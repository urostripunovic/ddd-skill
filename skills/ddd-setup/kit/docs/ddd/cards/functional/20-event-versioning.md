# Event versioning

**Use when:** a stored event has to change shape: a field is added, renamed or split. Applies to event-sourced aggregates and to events other contexts consume.

**Never:** edit stored events, or make a new field optional in the domain event so that old ones still load. That brings "only set in some cases" back into the domain.

## Rules

- A stored event carries its type name and a schema version. Both are written at append time.
- The domain has one shape per event: the current one. Old shapes exist only in the storage adapter.
- An upcaster turns an old stored shape into the current domain event when loading. It is pure, and it runs before the event reaches `evolve`.
- A value the old shape lacks is filled with one the business chose, recorded under the model's decisions. It is never a guess made in code.
- An unknown type or version is an error. Skipping it would rebuild a state that never existed.
- Stored data is untrusted input and is parsed through the same constructors as anything else. See [parse at the boundary](07-parse-at-the-boundary.md).
- A change of meaning is a new event with a new name, not a new version of the old one.

## Enforced by

- Both: the decoder is the only way from stored bytes to a domain event, and it returns the current shape or an error.
- Both: a test per stored version with a recorded sample, so an old shape cannot stop loading unnoticed.

## Anti-pattern

```ts
type OrderPlaced = {
  orderId: OrderId;
  channel?: Channel; // optional only because old events lack it; every consumer now has to guess
};
```

Examples: [Go](go/20-event-versioning.md) · [TypeScript](ts/20-event-versioning.md). Read only the one for your language.

## Corrections

<!-- Add a dated line each time an agent gets this pattern wrong. -->
