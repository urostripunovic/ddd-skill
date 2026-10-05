// The Examples table of docs/domain/contexts/ordering.md, row by row.
// Example 6 (the bounds of Quantity) is in primitives.test.ts.
import assert from "node:assert/strict";
import { test } from "node:test";
import { addItem, cancelOrder, placeOrder } from "../src/ordering/decisions.ts";
import { MINUTE, SECOND, at, draftWithItems, must, orderId, quantity, quoteAbc1, reason, tenOClock, testDraft } from "./support.ts";

await test("example 1: StartOrder gives a draft with no items for that customer", () => {
  const order = testDraft();
  assert.equal(order.kind, "draft");
  assert.equal(order.items.length, 0);
  assert.equal(order.customer.reveal(), "a@example.com");
});

await test("example 2: AddItem 2 × ABC-1 at 10:01 with a quote of 999 from 10:00", () => {
  const order = must(addItem(testDraft(), quantity(2), quoteAbc1(tenOClock), at(tenOClock, MINUTE)));
  assert.deepEqual(order.items, [{ sku: "ABC-1", quantity: 2, unitPrice: 999 }]);
});

await test("example 3: the same product twice is two items", () => {
  const order = draftWithItems(2);
  assert.deepEqual(order.items, [
    { sku: "ABC-1", quantity: 1, unitPrice: 999 },
    { sku: "ABC-1", quantity: 1, unitPrice: 999 },
  ]);
});

await test("example 4: a quote is accepted at 10:05:00 and expired at 10:05:01", () => {
  const quote = quoteAbc1(tenOClock);
  assert.ok(addItem(testDraft(), quantity(2), quote, at(tenOClock, 5 * MINUTE)).ok);
  assert.deepEqual(addItem(testDraft(), quantity(2), quote, at(tenOClock, 5 * MINUTE + SECOND)), {
    ok: false,
    error: "quote-expired",
  });
});

await test("example 5: accepted with 99 items, giving 100; TooManyItems with 100", () => {
  const full = must(addItem(draftWithItems(99), quantity(1), quoteAbc1(tenOClock), tenOClock));
  assert.equal(full.items.length, 100);
  assert.deepEqual(addItem(full, quantity(1), quoteAbc1(tenOClock), tenOClock), { ok: false, error: "too-many-items" });
});

await test("example 7: placing a draft with no items is EmptyOrder", () => {
  assert.deepEqual(placeOrder(testDraft(), tenOClock), { ok: false, error: "empty-order" });
});

await test("example 8: PlaceOrder at 10:00 gives a placed order with that item, and OrderPlaced", () => {
  const placed = must(placeOrder(draftWithItems(1), tenOClock));
  assert.equal(placed.order.kind, "placed");
  assert.deepEqual(placed.order.items, [{ sku: "ABC-1", quantity: 1, unitPrice: 999 }]);
  assert.equal(placed.order.placedAt, tenOClock);
  assert.deepEqual(placed.events, [{ type: "order-placed", orderId, at: tenOClock }]);
});

await test("example 9: cancelling a draft at 10:05 with a reason", () => {
  const later = at(tenOClock, 5 * MINUTE);
  const cancelled = cancelOrder(testDraft(), reason("changed my mind"), later);
  assert.equal(cancelled.order.kind, "cancelled");
  assert.equal(cancelled.order.reason, "changed my mind");
  assert.deepEqual(cancelled.events, [{ type: "order-cancelled", orderId, reason: "changed my mind", at: later }]);
});

await test("example 10: cancelling an order placed at 10:00, at 10:05 with a reason", () => {
  const later = at(tenOClock, 5 * MINUTE);
  const placed = must(placeOrder(draftWithItems(1), tenOClock));
  const cancelled = cancelOrder(placed.order, reason("found it cheaper"), later);
  assert.equal(cancelled.order.kind, "cancelled");
  assert.equal(cancelled.order.reason, "found it cheaper");
  assert.deepEqual(cancelled.events, [{ type: "order-cancelled", orderId, reason: "found it cheaper", at: later }]);
});

await test("a decision returns a new order and leaves the one it was given as it was", () => {
  const draft = draftWithItems(1);
  const more = must(addItem(draft, quantity(5), quoteAbc1(tenOClock), tenOClock));
  const placed = must(placeOrder(draft, tenOClock));
  assert.equal(draft.items.length, 1);
  assert.equal(more.items.length, 2);
  assert.equal(placed.order.items.length, 1);
});
