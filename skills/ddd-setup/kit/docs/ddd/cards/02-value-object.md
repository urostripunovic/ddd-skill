# Value object

**Use when:** several values only make sense together and have rules as a group (money = amount + currency, a date range, an address).

**Never:** pass the parts separately (`amount int64, currency string`), or do arithmetic on the parts outside the type.

## Rules

- Built only through a constructor that checks the combination.
- Immutable. Operations return a new value.
- Operations that can break a rule return an error; they do not silently coerce.
- Money is stored in minor units as an integer. Never a float.

## Enforced by

- Go: unexported fields; `exhaustive` on the currency switch.
- TypeScript: `readonly` fields plus a brand, so an object literal with the right shape is not accepted as `Money`.

## Anti-pattern

```ts
const total = a.amount + b.amount; // currencies never compared
```

## Example

One file per language: [Go](go/02-value-object.md), [TypeScript](ts/02-value-object.md). Read only the one for the language you are writing.

## Corrections

<!-- Add a dated line each time an agent gets this pattern wrong. -->
