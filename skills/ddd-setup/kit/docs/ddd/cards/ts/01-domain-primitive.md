# Domain primitive: TypeScript

The rules are in [the card](../01-domain-primitive.md).

```ts
export type Result<T, E> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E };

export type Quantity = number & { readonly __brand: "Quantity" };

const MAX_QUANTITY = 1000;

export function parseQuantity(raw: number): Result<Quantity, "invalid-quantity"> {
  if (!Number.isInteger(raw) || raw < 1 || raw > MAX_QUANTITY) {
    return { ok: false, error: "invalid-quantity" };
  }
  // eslint-disable-next-line @typescript-eslint/consistent-type-assertions -- the brand is applied only here, after validation
  return { ok: true, value: raw as Quantity };
}
```
