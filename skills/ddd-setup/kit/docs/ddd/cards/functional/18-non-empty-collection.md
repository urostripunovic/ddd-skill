# Non-empty collection

**Use when:** the model says "at least one": a placed order has items, a shipment has parcels. The invariant's "enforced by" column can then say **type**.

**Never:** keep a plain slice or array and re-check its length in every function that uses it.

## Rules

- A collection that must not be empty gets its own type, built by a constructor that rejects an empty input.
- The state that requires it holds that type. The state before it (a draft) keeps the ordinary collection.
- The check moves to the one transition between the two states. Every function after it relies on the type and checks nothing.
- An upper bound still applies and is checked in the same constructor.
- The same idea covers "exactly one" and "at most N": name the collection and give it a constructor.

## Enforced by

- Go: the first element is a field of its own, so a value built by the constructor always has one. The zero value still exists; `IsZero` detects it.
- TypeScript: the tuple type `readonly [T, ...T[]]`. An empty array is not assignable to it, and the first element is not `undefined` under `noUncheckedIndexedAccess`.

## Anti-pattern

```go
func Total(o PlacedOrder) Price {
	if len(o.items) == 0 { // cannot happen, and yet every function checks
		return Price{}
	}
	// ...
}
```

## Example

One file per language: [Go](go/18-non-empty-collection.md), [TypeScript](ts/18-non-empty-collection.md). Read only the one for the language you are writing.

## Corrections

<!-- Add a dated line each time an agent gets this pattern wrong. -->
