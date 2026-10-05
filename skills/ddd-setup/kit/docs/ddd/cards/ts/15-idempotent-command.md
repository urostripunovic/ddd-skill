# Idempotent command: TypeScript

The rules are in [the card](../15-idempotent-command.md).

Check as: boundary

```ts
export type Result<T, E> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E };

export type CommandId = string & { readonly __brand: "CommandId" };
export type OrderId = string & { readonly __brand: "OrderId" };

export type DraftOrder = { readonly kind: "draft"; readonly id: OrderId };
export type PlacedOrder = { readonly kind: "placed"; readonly id: OrderId; readonly placedAt: Date };

export function place(order: DraftOrder, now: Date): PlacedOrder {
  return { kind: "placed", id: order.id, placedAt: now };
}

export type PlaceOrderDeps = {
  readonly wasHandled: (command: CommandId) => Promise<boolean>;
  readonly loadDraft: (id: OrderId) => Promise<DraftOrder | undefined>;
  // Stores the order and the command ID in one transaction. Resolves to
  // "already-handled" when the unique constraint on the command ID rejects it.
  readonly savePlaced: (order: PlacedOrder, command: CommandId) => Promise<"saved" | "already-handled">;
  readonly now: () => Date;
};

export async function placeOrder(
  deps: PlaceOrderDeps,
  command: CommandId,
  id: OrderId,
): Promise<Result<OrderId, "order-not-found">> {
  if (await deps.wasHandled(command)) return { ok: true, value: id };

  const draft = await deps.loadDraft(id);
  if (draft === undefined) return { ok: false, error: "order-not-found" };

  // "already-handled" means a concurrent copy of this command won the race; its outcome is ours.
  await deps.savePlaced(place(draft, deps.now()), command);
  return { ok: true, value: id };
}
```
