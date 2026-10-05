# Workflow as function: TypeScript

The rules are in [the card](../06-workflow-as-function.md).

Check as: boundary

```ts
export type Result<T, E> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E };

export type OrderId = string & { readonly __brand: "OrderId" };
export type DraftOrder = { readonly kind: "draft"; readonly id: OrderId; readonly itemCount: number };
export type PlacedOrder = { readonly kind: "placed"; readonly id: OrderId; readonly placedAt: Date };
export type Order = DraftOrder | PlacedOrder;
export type OrderEvent = { readonly type: "order-placed"; readonly orderId: OrderId };

type Placed = { readonly order: PlacedOrder; readonly events: readonly OrderEvent[] };

function place(order: DraftOrder, now: Date): Result<Placed, "empty-order"> {
  if (order.itemCount === 0) return { ok: false, error: "empty-order" };
  return {
    ok: true,
    value: {
      order: { kind: "placed", id: order.id, placedAt: now },
      events: [{ type: "order-placed", orderId: order.id }],
    },
  };
}

export type PlaceOrderDeps = {
  readonly loadOrder: (id: OrderId) => Promise<Order | undefined>;
  // Takes state and events together so the implementation can commit both in one transaction.
  readonly savePlaced: (order: PlacedOrder, events: readonly OrderEvent[]) => Promise<void>;
  readonly now: () => Date;
};

export type PlaceOrderError = "order-not-found" | "order-not-draft" | "empty-order";

export async function placeOrder(
  deps: PlaceOrderDeps,
  id: OrderId,
): Promise<Result<PlacedOrder, PlaceOrderError>> {
  const order = await deps.loadOrder(id);
  if (order === undefined) return { ok: false, error: "order-not-found" };
  if (order.kind !== "draft") return { ok: false, error: "order-not-draft" };

  const decided = place(order, deps.now());
  if (!decided.ok) return decided;

  await deps.savePlaced(decided.value.order, decided.value.events);
  return { ok: true, value: decided.value.order };
}
```
