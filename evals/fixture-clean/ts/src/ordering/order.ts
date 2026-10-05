import type { CancellationReason, CustomerEmail, OrderId, Price, Quantity, Sku, Timestamp } from "./primitives.ts";

export type Item = {
  readonly sku: Sku;
  readonly quantity: Quantity;
  readonly unitPrice: Price;
};

export type DraftOrder = {
  readonly kind: "draft";
  readonly id: OrderId;
  readonly customer: CustomerEmail;
  readonly items: readonly Item[];
};

export type PlacedOrder = {
  readonly kind: "placed";
  readonly id: OrderId;
  readonly customer: CustomerEmail;
  // "At least one" is held by the decision function placeOrder, as the model says, not by this type.
  readonly items: readonly Item[];
  readonly placedAt: Timestamp;
};

export type CancelledOrder = {
  readonly kind: "cancelled";
  readonly id: OrderId;
  readonly customer: CustomerEmail;
  readonly reason: CancellationReason;
};

export type Order = DraftOrder | PlacedOrder | CancelledOrder;

export type OrderPlaced = {
  readonly type: "order-placed";
  readonly orderId: OrderId;
  readonly at: Timestamp;
};

export type OrderCancelled = {
  readonly type: "order-cancelled";
  readonly orderId: OrderId;
  readonly reason: CancellationReason;
  readonly at: Timestamp;
};

export type OrderEvent = OrderPlaced | OrderCancelled;

// A fact from the Pricing service: what one product cost, and when that was said.
export type PriceQuote = {
  readonly sku: Sku;
  readonly unitPrice: Price;
  readonly quotedAt: Timestamp;
};
