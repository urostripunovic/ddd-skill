# States as types: TypeScript

The rules are in [the card](../03-states-as-types.md).

```ts
export type OrderId = string & { readonly __brand: "OrderId" };

export type DraftOrder = { readonly kind: "draft"; readonly id: OrderId };
export type PlacedOrder = { readonly kind: "placed"; readonly id: OrderId; readonly placedAt: Date };
export type CancelledOrder = { readonly kind: "cancelled"; readonly id: OrderId; readonly reason: string };

export type Order = DraftOrder | PlacedOrder | CancelledOrder;

export type CancellableOrder = DraftOrder | PlacedOrder;

export function cancel(order: CancellableOrder, reason: string): CancelledOrder {
  return { kind: "cancelled", id: order.id, reason };
}

export function assertNever(x: never): never {
  // eslint-disable-next-line no-restricted-syntax -- an unhandled variant is a bug, not a business failure
  throw new Error(`unhandled variant: ${JSON.stringify(x)}`);
}

export function canBeEdited(order: Order): boolean {
  switch (order.kind) {
    case "draft":
      return true;
    case "placed":
    case "cancelled":
      return false;
    default:
      return assertNever(order);
  }
}
```
