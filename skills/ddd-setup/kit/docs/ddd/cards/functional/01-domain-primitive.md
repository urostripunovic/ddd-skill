# Domain primitive

**Use when:** a value has rules (format, range, length) or two values of the same underlying type must not be mixed up (`OrderID` vs `CustomerID`).

**Never:** pass a raw `string`, `int` or `number` across a domain function boundary.

## Rules

- The only way to get an instance is a constructor/parser that validates.
- Immutable. Compared by value.
- No setter, no "update" method. A new value is a new instance.
- Upper bounds are part of the rules, not only lower bounds. An unbounded string is an attack surface.

## Enforced by

- Go: unexported field, so other packages cannot build one with a literal. The zero value still exists; make it detectably invalid.
- TypeScript: branded type. ESLint bans `as`, so the one cast inside the parser needs a visible disable comment.

## Anti-pattern

```go
func Transfer(amount int, account string) error
```

## Example

One file per language: [Go](go/01-domain-primitive.md), [TypeScript](ts/01-domain-primitive.md). Read only the one for the language you are writing.

## Corrections

<!-- Add a dated line each time an agent gets this pattern wrong. -->
