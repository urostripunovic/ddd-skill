// Random command sequences, with the model's invariants checked after every step.
// The examples in decisions.test.ts cover the cases somebody thought of; this covers the orders nobody did.
// A failure names its seed: rerun with that seed alone to reproduce it.
import assert from "node:assert/strict";
import { test } from "node:test";
import { addItem, cancelOrder, placeOrder } from "../src/ordering/decisions.ts";
import type { Order } from "../src/ordering/order.ts";
import type { Timestamp } from "../src/ordering/primitives.ts";
import { MINUTE, SECOND, at, draftWithItems, quantity, quoteAbc1, reason, tenOClock, testDraft } from "./support.ts";

const SEQUENCES = 2000;
const STEPS = 60;

// mulberry32: small, and the same seed always gives the same sequence.
function random(seed: number): (below: number) => number {
  let state = seed;
  return (below) => {
    state = (state + 0x6d2b79f5) | 0;
    let t = Math.imul(state ^ (state >>> 15), 1 | state);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return Math.floor((((t ^ (t >>> 14)) >>> 0) / 4294967296) * below);
  };
}

// Applies one command if the state allows it, as a workflow would after narrowing.
// A command the state does not allow has no function that accepts it: that is invariants 4 and 5, held by the types.
function randomCommand(next: (below: number) => number, order: Order, now: Timestamp): Order {
  const roll = next(100);
  if (roll < 88) {
    if (order.kind !== "draft") return order;
    const age = next(400) * SECOND;
    const added = addItem(order, quantity(1 + next(1000)), quoteAbc1(at(now, -age)), now);
    if (added.ok) return added.value;
    const expected =
      (added.error === "quote-expired" && age > 5 * MINUTE) ||
      (added.error === "too-many-items" && order.items.length === 100);
    assert.ok(expected, `AddItem with ${String(order.items.length)} items and a quote ${String(age)} ms old: ${added.error}`);
    return order;
  }
  if (roll < 96) {
    if (order.kind !== "draft") return order;
    const placed = placeOrder(order, now);
    if (placed.ok) return placed.value.order;
    assert.equal(order.items.length, 0, `PlaceOrder with items: ${placed.error}`);
    return order;
  }
  if (order.kind === "cancelled") return order;
  return cancelOrder(order, reason("changed my mind"), now).order;
}

function brokenInvariant(before: Order, after: Order): string | undefined {
  if (after.id !== before.id || after.customer !== before.customer) return "the order's id or customer changed";
  switch (after.kind) {
    case "draft":
      if (after.items.length > 100) return "invariant 6: a draft order has more than 100 items";
      if (before.kind !== "draft") return "an order went back to being a draft";
      return undefined;
    case "placed":
      if (after.items.length === 0) return "invariant 1: a placed order has no items";
      if (after.items.length > 100) return "invariant 6: a placed order has more than 100 items";
      if (before.kind === "placed" && (before.items.length !== after.items.length || before.placedAt !== after.placedAt)) {
        return "invariant 4: a placed order changed";
      }
      if (before.kind === "cancelled") return "invariant 5: a cancelled order was placed";
      return undefined;
    case "cancelled":
      if (after.reason.length === 0) return "invariant 3: a cancelled order has no reason";
      if (before.kind === "cancelled" && before.reason !== after.reason) return "invariant 5: a cancelled order changed";
      return undefined;
  }
}

await test("the invariants hold for any sequence of commands", () => {
  let reachedLimit = 0;
  for (let seed = 0; seed < SEQUENCES; seed++) {
    const next = random(seed);
    // A random sequence almost never adds 100 items before it places or cancels,
    // so some start close to the limit to make sure it is exercised.
    let order: Order = seed % 4 === 0 ? draftWithItems(97) : testDraft();
    let now = tenOClock;
    for (let step = 0; step < STEPS; step++) {
      now = at(now, next(120) * SECOND);
      const before = order;
      order = randomCommand(next, order, now);
      const problem = brokenInvariant(before, order);
      assert.equal(problem, undefined, `seed ${String(seed)}, step ${String(step)}: ${String(problem)}`);
      if (order.kind === "draft" && order.items.length === 100) reachedLimit++;
    }
  }
  // A generator that never reaches the limit would prove nothing about it.
  assert.ok(reachedLimit > 0, "no sequence reached 100 items");
});
