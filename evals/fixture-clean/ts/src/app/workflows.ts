// One function per use case: load, authorise, narrow, decide, save. The rules are in src/ordering.
import { mayChangeOrder, ownerOfNewOrder, type Actor } from "../ordering/actor.ts";
import { addItem, cancelOrder, placeOrder, startOrder } from "../ordering/decisions.ts";
import type { DraftOrder, Order, OrderEvent, PlacedOrder, PriceQuote } from "../ordering/order.ts";
import type { CancellationReason, OrderId, Quantity, Sku, Timestamp } from "../ordering/primitives.ts";
import type { Orders } from "../ordering/repository.ts";
import type { Result } from "../ordering/result.ts";

const MAX_ATTEMPTS = 3;

// A function here rejects (throws) only when the infrastructure fails. Every business outcome is a Result.
export type Deps = {
  readonly orders: Orders;
  readonly quotePrice: (sku: Sku) => Promise<PriceQuote>;
  readonly newOrderId: () => OrderId;
  readonly now: () => Timestamp;
};

type Changed = { readonly order: Order; readonly events: readonly OrderEvent[] };
type ChangeError = "order-not-found" | "not-allowed" | "conflict";

// On a conflict the order is loaded and decided again, so the command that was
// saved second is judged against what the first one left behind.
async function change<E>(
  deps: Deps,
  actor: Actor,
  id: OrderId,
  decide: (order: Order) => Promise<Result<Changed, E>>,
): Promise<Result<undefined, E | ChangeError>> {
  for (let attempt = 0; attempt < MAX_ATTEMPTS; attempt++) {
    const loaded = await deps.orders.load(id);
    if (!loaded.ok) return loaded;
    // Before narrowing, so someone who does not own the order learns nothing about its state.
    if (!mayChangeOrder(actor, loaded.value.order)) return { ok: false, error: "not-allowed" };

    const decided = await decide(loaded.value.order);
    if (!decided.ok) return decided;

    const saved = await deps.orders.save(decided.value.order, decided.value.events, loaded.value.version);
    if (saved.ok) return saved;
  }
  return { ok: false, error: "conflict" };
}

function asDraft(order: Order): Result<DraftOrder, "order-not-draft"> {
  switch (order.kind) {
    case "draft":
      return { ok: true, value: order };
    case "placed":
    case "cancelled":
      return { ok: false, error: "order-not-draft" };
  }
}

function asCancellable(order: Order): Result<DraftOrder | PlacedOrder, "order-already-cancelled"> {
  switch (order.kind) {
    case "draft":
    case "placed":
      return { ok: true, value: order };
    case "cancelled":
      return { ok: false, error: "order-already-cancelled" };
  }
}

export async function startOrderFor(deps: Deps, actor: Actor): Promise<OrderId> {
  const id = deps.newOrderId();
  await deps.orders.create(startOrder(id, ownerOfNewOrder(actor)));
  return id;
}

export type AddItemError = ChangeError | "order-not-draft" | "quote-expired" | "too-many-items";

export function addItemTo(
  deps: Deps,
  actor: Actor,
  id: OrderId,
  sku: Sku,
  quantity: Quantity,
): Promise<Result<undefined, AddItemError>> {
  return change(deps, actor, id, async (order) => {
    const draft = asDraft(order);
    if (!draft.ok) return draft;
    // Fetched after the checks above, so a price is only requested for an order this caller may change.
    const quote = await deps.quotePrice(sku);
    // The item takes its product from the quote, so an answer for another product would be stored unnoticed.
    // A throw, because this is the pricing adapter failing and not a business outcome.
    if (quote.sku !== sku) throw new Error("quote price: the answer is for another product");
    const added = addItem(draft.value, quantity, quote, deps.now());
    if (!added.ok) return added;
    return { ok: true, value: { order: added.value, events: [] } };
  });
}

export type PlaceOrderError = ChangeError | "order-not-draft" | "empty-order";

export function placeOrderWith(deps: Deps, actor: Actor, id: OrderId): Promise<Result<undefined, PlaceOrderError>> {
  return change(deps, actor, id, (order) => {
    const draft = asDraft(order);
    if (!draft.ok) return Promise.resolve(draft);
    return Promise.resolve(placeOrder(draft.value, deps.now()));
  });
}

export type CancelOrderError = ChangeError | "order-already-cancelled";

export function cancelOrderWith(
  deps: Deps,
  actor: Actor,
  id: OrderId,
  reason: CancellationReason,
): Promise<Result<undefined, CancelOrderError>> {
  return change(deps, actor, id, (order) => {
    const cancellable = asCancellable(order);
    if (!cancellable.ok) return Promise.resolve(cancellable);
    return Promise.resolve({ ok: true, value: cancelOrder(cancellable.value, reason, deps.now()) });
  });
}
