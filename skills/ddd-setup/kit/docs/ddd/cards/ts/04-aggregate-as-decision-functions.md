# Aggregate as data plus decision functions: TypeScript

The rules are in [the card](../04-aggregate-as-decision-functions.md).

```ts
export type Result<T, E> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E };

export type OrderId = string & { readonly __brand: "OrderId" };
export type Sku = string & { readonly __brand: "Sku" };
export type Quantity = number & { readonly __brand: "Quantity" };

export type Item = { readonly sku: Sku; readonly quantity: Quantity };

export type DraftOrder = {
  readonly kind: "draft";
  readonly id: OrderId;
  readonly items: readonly Item[];
};

export type PlacedOrder = {
  readonly kind: "placed";
  readonly id: OrderId;
  readonly items: readonly Item[];
  readonly placedAt: Date;
};

export type OrderPlaced = {
  readonly type: "order-placed";
  readonly orderId: OrderId;
  readonly at: Date;
};

export type OrderEvent = OrderPlaced;

export type Placed = {
  readonly order: PlacedOrder;
  readonly events: readonly OrderEvent[];
};

// now is a parameter so the decision stays pure and can be tested without a clock.
export function place(order: DraftOrder, now: Date): Result<Placed, "empty-order"> {
  if (order.items.length === 0) return { ok: false, error: "empty-order" };
  return {
    ok: true,
    value: {
      order: { kind: "placed", id: order.id, items: order.items, placedAt: now },
      events: [{ type: "order-placed", orderId: order.id, at: now }],
    },
  };
}
```
