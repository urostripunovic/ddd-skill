# Repository

**Use when:** an aggregate needs to be loaded or stored.

**Never:** return rows, ORM entities or DTOs from a repository. Never add query methods for screens and reports; those are read models and belong outside the domain.

## Rules

- The interface is declared in the domain, in domain types. The implementation lives in infrastructure and depends on the domain, never the other way.
- One repository per aggregate. It loads and saves the whole aggregate.
- Loading rebuilds the aggregate through the same constructors as any other input. See [parse at the boundary](07-parse-at-the-boundary.md).
- "Not found" is an expected outcome with its own error value, not a nil or a generic failure.
- Keep it small: usually `byID` and `save`. Add a method only when a workflow needs it.
- Two requests can load the same aggregate and both save. Give the stored aggregate a version, and make `save` fail when the version has changed since loading. For event-sourced aggregates see [event stream repository](12-event-stream-repository.md).

## Enforced by

- Go: import direction. The domain package must not import the database package.
- TypeScript: the domain module exports only the type; `undefined` in the return type forces callers to handle "not found".

## Anti-pattern

```go
func (r *OrderRepo) FindAllWhere(sql string, args ...any) ([]map[string]any, error)
```

Examples: [Go](go/08-repository.md) · [TypeScript](ts/08-repository.md). Read only the one for your language.

## Corrections

<!-- Add a dated line each time an agent gets this pattern wrong. -->
