import assert from "node:assert/strict";
import { addItem, startOrder } from "../src/ordering/decisions.ts";
import type { DraftOrder, PriceQuote } from "../src/ordering/order.ts";
import {
  parseCancellationReason,
  parseCustomerEmail,
  parseOrderId,
  parsePrice,
  parseQuantity,
  parseSku,
  parseTimestamp,
  type CancellationReason,
  type CustomerEmail,
  type OrderId,
  type Quantity,
  type Timestamp,
} from "../src/ordering/primitives.ts";
import type { Result } from "../src/ordering/result.ts";

export function must<T, E>(result: Result<T, E>): T {
  if (!result.ok) throw new Error(`test setup: ${String(result.error)}`);
  return result.value;
}

export const SECOND = 1000;
export const MINUTE = 60 * SECOND;

export function at(base: Timestamp, offsetMillis: number): Timestamp {
  return must(parseTimestamp(base + offsetMillis));
}

export const tenOClock: Timestamp = must(parseTimestamp(Date.UTC(2026, 2, 1, 10, 0, 0)));
export const orderId: OrderId = must(parseOrderId("123e4567-e89b-12d3-a456-426614174000"));

export const email = (raw: string): CustomerEmail => must(parseCustomerEmail(raw));
export const quantity = (raw: number): Quantity => must(parseQuantity(raw));
export const reason = (raw: string): CancellationReason => must(parseCancellationReason(raw));

export function quoteAbc1(quotedAt: Timestamp): PriceQuote {
  return { sku: must(parseSku("ABC-1")), unitPrice: must(parsePrice(999)), quotedAt };
}

export function testDraft(): DraftOrder {
  return startOrder(orderId, email("a@example.com"));
}

export function draftWithItems(count: number): DraftOrder {
  let order = testDraft();
  for (let i = 0; i < count; i++) {
    order = must(addItem(order, quantity(1), quoteAbc1(tenOClock), tenOClock));
  }
  assert.equal(order.items.length, count);
  return order;
}
