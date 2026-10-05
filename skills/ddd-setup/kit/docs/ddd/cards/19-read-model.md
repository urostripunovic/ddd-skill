# Read model

**Use when:** a screen, report, list or search needs data. Nothing is being decided.

**Never:** load aggregates to answer a query, add `FindAllWhere` methods to a [repository](08-repository.md), or pass a read model into a decision function.

## Rules

- A read model is shaped for one question, and lives outside the domain package. It may join, flatten and denormalise freely.
- It is output, so plain display values and optional fields are fine here. That is also why it must never flow back into the domain: it has been through no constructor.
- If a decision needs the data, it is a fact, not a read model. See [facts from outside the aggregate](13-facts-from-outside.md).
- The query's input is still untrusted. Filters, page sizes and sort keys are parsed into types with bounds. An unbounded page size is a way to exhaust the service.
- A query takes the actor and returns only what that actor may see. See [authorisation](14-authorisation.md).
- A read model may be slightly behind the write side. The model says how far behind is acceptable for each one.
- It is fed either by a query over the same tables the repository writes, or by a projection of events. Choose the first until it stops being enough.

## Enforced by

- Go: import direction. The domain package does not import the read-model package.
- TypeScript: the read-model type has no brand, so it is not assignable to a domain type.

## Anti-pattern

```go
orders, _ := repo.All(ctx) // every aggregate loaded and rebuilt
for _, o := range orders { // to count items for a list page
	// ...
}
```

## Example

One file per language: [Go](go/19-read-model.md), [TypeScript](ts/19-read-model.md). Read only the one for the language you are writing.

## Corrections

<!-- Add a dated line each time an agent gets this pattern wrong. -->
