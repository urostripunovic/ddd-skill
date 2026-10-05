import type { CancelledOrder, DraftOrder, OrderEvent, PlacedOrder, PriceQuote } from "./order.ts";
import type { CancellationReason, CustomerEmail, OrderId, Quantity, Timestamp } from "./primitives.ts";
import type { Result } from "./result.ts";

const MAX_ITEMS = 100;
const MAX_QUOTE_AGE_MILLIS = 5 * 60 * 1000;

export function startOrder(id: OrderId, customer: CustomerEmail): DraftOrder {
  return { kind: "draft", id, customer, items: [] };
}

// The item's product and price both come from the quote, so they cannot disagree.
export function addItem(
  order: DraftOrder,
  quantity: Quantity,
  quote: PriceQuote,
  now: Timestamp,
): Result<DraftOrder, "quote-expired" | "too-many-items"> {
  if (now - quote.quotedAt > MAX_QUOTE_AGE_MILLIS) return { ok: false, error: "quote-expired" };
  if (order.items.length >= MAX_ITEMS) return { ok: false, error: "too-many-items" };
  const items = [...order.items, { sku: quote.sku, quantity, unitPrice: quote.unitPrice }];
  return { ok: true, value: { ...order, items } };
}

export type Placed = { readonly order: PlacedOrder; readonly events: readonly OrderEvent[] };

export function placeOrder(order: DraftOrder, now: Timestamp): Result<Placed, "empty-order"> {
  if (order.items.length === 0) return { ok: false, error: "empty-order" };
  return {
    ok: true,
    value: {
      order: { kind: "placed", id: order.id, customer: order.customer, items: order.items, placedAt: now },
      events: [{ type: "order-placed", orderId: order.id, at: now }],
    },
  };
}

export type Cancelled = { readonly order: CancelledOrder; readonly events: readonly OrderEvent[] };

// Cannot fail: the parameter type is exactly the states the model allows it in.
export function cancelOrder(order: DraftOrder | PlacedOrder, reason: CancellationReason, now: Timestamp): Cancelled {
  return {
    order: { kind: "cancelled", id: order.id, customer: order.customer, reason },
    events: [{ type: "order-cancelled", orderId: order.id, reason, at: now }],
  };
}
