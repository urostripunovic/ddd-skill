# Anti-corruption layer

**Use when:** the domain depends on another system's model: a payment provider, a legacy database, another team's API, another bounded context.

**Never:** let the other system's types, field names or status strings appear in domain code.

When to choose this over conforming to the other model is a modelling decision: see the strategic card, [anti-corruption layer](../../strategic/06-anti-corruption-layer.md).

## Rules

- A translator at the edge maps the external model to domain types and back. Nothing else knows the external model.
- Translation is a parse: unknown or unexpected values are errors, not defaults.
- The domain's states are chosen by the domain. Several external statuses may map to one domain state, and some may map to none.
- The external model's names stay in the adapter. The domain uses the ubiquitous language.

## Enforced by

- Go: the external DTO lives in the adapter package; the domain package does not import it.
- TypeScript: the adapter takes `unknown` and returns a domain union.

## Anti-pattern

```ts
if (order.stripeStatus === "requires_capture") { /* domain logic */ }
```

## Example

One file per language: [Go](go/09-anti-corruption-layer.md), [TypeScript](ts/09-anti-corruption-layer.md). Read only the one for the language you are writing.

## Corrections

<!-- Add a dated line each time an agent gets this pattern wrong. -->
