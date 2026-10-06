# Read model: TypeScript

The rules are in [the card](../19-read-model.md).

Check as: boundary

```ts
export type Result<T, E> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E };

export type PageSize = number & { readonly __brand: "PageSize" };
export type CustomerId = string & { readonly __brand: "CustomerId" };

const MAX_PAGE_SIZE = 100;

export function parsePageSize(raw: number): Result<PageSize, "invalid-page-size"> {
  if (!Number.isInteger(raw) || raw < 1 || raw > MAX_PAGE_SIZE) {
    return { ok: false, error: "invalid-page-size" };
  }
  // eslint-disable-next-line @typescript-eslint/consistent-type-assertions -- the brand is applied only here, after validation
  return { ok: true, value: raw as PageSize };
}

// Shaped for the "my orders" list. Plain values, because this is output and
// never enters a decision function.
export type OrderSummary = {
  readonly orderId: string;
  readonly status: string;
  readonly itemCount: number;
  // Undefined until the order is placed.
  readonly placedAt: Date | undefined;
};

// Takes the customer whose orders are asked for; the caller has already
// checked that the actor may see them.
export type OrderSummaries = {
  readonly forCustomer: (customer: CustomerId, size: PageSize) => Promise<readonly OrderSummary[]>;
};
```
