# Errors as values

**Use when:** a domain operation can fail for a business reason: out of stock, already placed, limit exceeded.

**Never:** throw or panic for an expected business outcome. Never return a bare string, or one generic error for every case.

## Rules

- Each business failure has a name in the ubiquitous language and its own error value or variant.
- A failure carries the data needed to explain it, as domain types.
- Domain errors and infrastructure errors (timeout, connection lost) are kept apart. The domain never returns the second kind.
- Error text shown to users is chosen at the boundary. Domain errors must not leak internals; an error is also output and can expose data.
- Exceptions and panics are for bugs only.

## Enforced by

- Go: sentinel errors and error types, matched with `errors.Is` and `errors.As`. Never by comparing strings.
- TypeScript: a discriminated union in the `Result` error position, handled with `assertNever` so a new failure does not compile until it is handled.

## Anti-pattern

```ts
throw new Error("Not enough stock for " + sku);
```

Examples: [Go](go/10-errors-as-values.md) · [TypeScript](ts/10-errors-as-values.md). Read only the one for your language.

## Corrections

<!-- Add a dated line each time an agent gets this pattern wrong. -->
