# Errors as values: TypeScript

The rules are in [the card](../10-errors-as-values.md).

```ts
export type Result<T, E> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E };

export type Quantity = number & { readonly __brand: "Quantity" };
// A separate type from Quantity so "requested" and "available" cannot be swapped.
export type StockLevel = number & { readonly __brand: "StockLevel" };

export type InsufficientStock = {
  readonly kind: "insufficient-stock";
  readonly requested: Quantity;
  readonly available: StockLevel;
};

export type OrderAlreadyPlaced = { readonly kind: "order-already-placed" };

export type ReserveError = InsufficientStock | OrderAlreadyPlaced;

export function reserve(requested: Quantity, available: StockLevel): Result<undefined, ReserveError> {
  if (requested > available) {
    return { ok: false, error: { kind: "insufficient-stock", requested, available } };
  }
  return { ok: true, value: undefined };
}

function assertNever(x: never): never {
  // eslint-disable-next-line no-restricted-syntax -- an unhandled variant is a bug, not a business failure
  throw new Error(`unhandled variant: ${JSON.stringify(x)}`);
}

export function userMessage(error: ReserveError): string {
  switch (error.kind) {
    case "insufficient-stock":
      return `Only ${String(error.available)} left in stock.`;
    case "order-already-placed":
      return "This order has already been placed.";
    default:
      return assertNever(error);
  }
}
```
