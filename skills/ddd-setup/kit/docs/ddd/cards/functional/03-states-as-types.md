# States as types

**Use when:** something has a lifecycle and different states carry different data or allow different operations.

**Never:** one struct/object with a `status` field and optional fields that are "only set when status is X".

## Rules

- One type per state. Each type holds exactly the data that exists in that state.
- A closed set of states forms a sum type.
- Every switch over the sum type lists every variant. No `default` that swallows new variants.
- Go: put every switch over a sum type in the package that declares it. Under golangci-lint, `gochecksumtype` does not report a missing variant in a switch that lives in another package. Code elsewhere calls a function exported by the declaring package, such as `AsDraft(order)`.
- A function that only makes sense in one state takes that state's type, not the sum type.
- A function that is legal in several states takes exactly those states: a narrower sum type, never the whole one.

## Enforced by

- Go: sealed interface marked `//sumtype:decl`, checked by `gochecksumtype` with `default-signifies-exhaustive: false`. A nil interface value is still possible and no linter catches it.
- Go: state fields are unexported and read through accessors, so only the domain package can build a state with contents. Another package can still write the zero value (`PlacedOrder{}`); Go cannot prevent that, so code that receives a state from outside the package checks for it.
- TypeScript: discriminated union on `kind`; `assertNever` makes a missing case a compile error.

## Anti-pattern

```go
type Order struct {
	Status   string     // "draft" | "placed" | "cancelled"
	PlacedAt *time.Time // nil unless placed
	Reason   string     // empty unless cancelled
}
```

Examples: [Go](go/03-states-as-types.md) · [TypeScript](ts/03-states-as-types.md). Read only the one for your language.

## Corrections

<!-- Add a dated line each time an agent gets this pattern wrong. -->
