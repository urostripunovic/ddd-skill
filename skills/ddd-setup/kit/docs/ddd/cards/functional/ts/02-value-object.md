# Value object: TypeScript

The rules are in [the card](../02-value-object.md).

```ts
export type Result<T, E> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E };

export type Currency = "SEK" | "EUR";

export type Money = {
  readonly minor: bigint;
  readonly currency: Currency;
  readonly __brand: "Money";
};

export function money(minor: bigint, currency: Currency): Result<Money, "negative-amount"> {
  if (minor < 0n) return { ok: false, error: "negative-amount" };
  return { ok: true, value: { minor, currency, __brand: "Money" } };
}

export function add(a: Money, b: Money): Result<Money, "currency-mismatch"> {
  if (a.currency !== b.currency) return { ok: false, error: "currency-mismatch" };
  return { ok: true, value: { minor: a.minor + b.minor, currency: a.currency, __brand: "Money" } };
}
```
