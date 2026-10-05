import assert from "node:assert/strict";
import { test } from "node:test";
import { addItemTo, cancelOrderWith, placeOrderWith, startOrderFor, type Deps } from "../src/app/workflows.ts";
import { authenticate, type Actor } from "../src/ordering/actor.ts";
import { cancelOrder, placeOrder } from "../src/ordering/decisions.ts";
import type { Order, OrderEvent } from "../src/ordering/order.ts";
import { parseOrderId, parseSku, type OrderId } from "../src/ordering/primitives.ts";
import { FIRST_VERSION, nextVersion, type Orders, type Version } from "../src/ordering/repository.ts";
import { email, must, orderId, quantity, quoteAbc1, reason, tenOClock } from "./support.ts";

type Stored = { readonly order: Order; readonly version: Version };

// An in-memory Orders with the same version check a database implementation makes.
type MemOrders = Orders & {
  readonly stored: (id: OrderId) => Order;
  readonly events: () => readonly OrderEvent[];
  readonly saves: () => number;
  // Stores an order behind the back of the workflow under test, as a competing request would.
  readonly overwrite: (order: Order) => void;
  // Runs once, just before the next save.
  readonly beforeNextSave: (hook: () => void) => void;
};

function memOrders(): MemOrders {
  const orders = new Map<OrderId, Stored>();
  let events: readonly OrderEvent[] = [];
  let saves = 0;
  let hook: (() => void) | undefined;

  const stored = (id: OrderId): Stored => {
    const found = orders.get(id);
    assert.ok(found !== undefined, "no such order in the test repository");
    return found;
  };

  return {
    create: (order) => {
      orders.set(order.id, { order, version: FIRST_VERSION });
      return Promise.resolve();
    },
    load: (id) => {
      const found = orders.get(id);
      return Promise.resolve(found === undefined ? { ok: false, error: "order-not-found" } : { ok: true, value: found });
    },
    save: (order, newEvents, loaded) => {
      saves++;
      const competing = hook;
      hook = undefined;
      competing?.();
      if (stored(order.id).version !== loaded) return Promise.resolve({ ok: false, error: "conflict" });
      orders.set(order.id, { order, version: nextVersion(loaded) });
      events = [...events, ...newEvents];
      return Promise.resolve({ ok: true, value: undefined });
    },
    stored: (id) => stored(id).order,
    events: () => events,
    saves: () => saves,
    overwrite: (order) => {
      orders.set(order.id, { order, version: nextVersion(stored(order.id).version) });
    },
    beforeNextSave: (next) => {
      hook = next;
    },
  };
}

async function actorFor(address: string): Promise<Actor> {
  return must(await authenticate(() => Promise.resolve({ ok: true, value: { customer: email(address) } })));
}

type Fixture = {
  readonly deps: Deps;
  readonly orders: MemOrders;
  readonly owner: Actor;
  readonly other: Actor;
};

async function setup(): Promise<Fixture> {
  const orders = memOrders();
  return {
    orders,
    deps: {
      orders,
      quotePrice: () => Promise.resolve(quoteAbc1(tenOClock)),
      newOrderId: () => orderId,
      now: () => tenOClock,
    },
    owner: await actorFor("owner@example.com"),
    other: await actorFor("other@example.com"),
  };
}

const sku = must(parseSku("ABC-1"));
const one = quantity(1);
const changedMyMind = reason("changed my mind");

async function draftWithItem(f: Fixture): Promise<OrderId> {
  const id = await startOrderFor(f.deps, f.owner);
  assert.deepEqual(await addItemTo(f.deps, f.owner, id, sku, one), { ok: true, value: undefined });
  return id;
}

// What a competing request leaves behind, decided by the same functions the workflows use.
function placedBehindTheBack(f: Fixture, id: OrderId): void {
  const order = f.orders.stored(id);
  assert.equal(order.kind, "draft");
  f.orders.overwrite(must(placeOrder(order, tenOClock)).order);
}

function cancelledBehindTheBack(f: Fixture, id: OrderId): void {
  const order = f.orders.stored(id);
  if (order.kind === "cancelled") assert.fail("the order was already cancelled");
  f.orders.overwrite(cancelOrder(order, reason("someone was quicker"), tenOClock).order);
}

await test("authenticate gives no actor without a verified credential", async () => {
  const result = await authenticate(() => Promise.resolve({ ok: false, error: "not-authenticated" }));
  assert.deepEqual(result, { ok: false, error: "not-authenticated" });
});

await test("start, add, place: the order is stored as placed, with OrderPlaced alone", async () => {
  const f = await setup();
  const id = await draftWithItem(f);
  assert.equal(f.orders.stored(id).customer.reveal(), "owner@example.com");
  assert.deepEqual(await placeOrderWith(f.deps, f.owner, id), { ok: true, value: undefined });
  assert.equal(f.orders.stored(id).kind, "placed");
  assert.deepEqual(f.orders.events(), [{ type: "order-placed", orderId: id, at: tenOClock }]);
});

await test("NotAllowed: only the owner may change an order, and nothing is saved", async () => {
  const commands = {
    AddItem: (f: Fixture, id: OrderId) => addItemTo(f.deps, f.other, id, sku, one),
    PlaceOrder: (f: Fixture, id: OrderId) => placeOrderWith(f.deps, f.other, id),
    CancelOrder: (f: Fixture, id: OrderId) => cancelOrderWith(f.deps, f.other, id, changedMyMind),
  };
  for (const [name, command] of Object.entries(commands)) {
    const f = await setup();
    const id = await draftWithItem(f);
    const saves = f.orders.saves();
    assert.deepEqual(await command(f, id), { ok: false, error: "not-allowed" }, name);
    assert.equal(f.orders.saves(), saves, `${name}: the order was saved`);
  }
});

await test("someone else learns nothing about the order's state", async () => {
  const f = await setup();
  const id = await draftWithItem(f);
  assert.ok((await placeOrderWith(f.deps, f.owner, id)).ok);
  // The owner would get OrderNotDraft here. Someone else must not be told that much.
  assert.deepEqual(await placeOrderWith(f.deps, f.other, id), { ok: false, error: "not-allowed" });
});

await test("OrderNotFound: no order has the given id", async () => {
  const f = await setup();
  const missing = must(parseOrderId("00000000-0000-0000-0000-000000000000"));
  assert.deepEqual(await placeOrderWith(f.deps, f.owner, missing), { ok: false, error: "order-not-found" });
});

await test("OrderNotDraft: AddItem or PlaceOrder for an order that is not a draft", async () => {
  const f = await setup();
  const id = await draftWithItem(f);
  assert.ok((await placeOrderWith(f.deps, f.owner, id)).ok);
  assert.deepEqual(await placeOrderWith(f.deps, f.owner, id), { ok: false, error: "order-not-draft" });
  assert.deepEqual(await addItemTo(f.deps, f.owner, id, sku, one), { ok: false, error: "order-not-draft" });
});

await test("a business failure of a decision reaches the caller and nothing is saved", async () => {
  const f = await setup();
  const id = await startOrderFor(f.deps, f.owner);
  assert.deepEqual(await placeOrderWith(f.deps, f.owner, id), { ok: false, error: "empty-order" });
  assert.equal(f.orders.saves(), 0);
});

await test("a quote for another product is refused, and the order does not change", async () => {
  const f = await setup();
  const id = await startOrderFor(f.deps, f.owner);
  const deps: Deps = { ...f.deps, quotePrice: () => Promise.resolve({ ...quoteAbc1(tenOClock), sku: must(parseSku("OTHER-9")) }) };
  await assert.rejects(addItemTo(deps, f.owner, id, sku, one));
  const stored = f.orders.stored(id);
  assert.ok(stored.kind === "draft" && stored.items.length === 0);
});

// The Races table of the model: the command that is saved second is judged against what the first left behind.

await test("race: PlaceOrder after a cancel gets OrderNotDraft", async () => {
  const f = await setup();
  const id = await draftWithItem(f);
  f.orders.beforeNextSave(() => {
    cancelledBehindTheBack(f, id);
  });
  assert.deepEqual(await placeOrderWith(f.deps, f.owner, id), { ok: false, error: "order-not-draft" });
  assert.equal(f.orders.stored(id).kind, "cancelled");
});

await test("race: CancelOrder after a place succeeds", async () => {
  const f = await setup();
  const id = await draftWithItem(f);
  f.orders.beforeNextSave(() => {
    placedBehindTheBack(f, id);
  });
  assert.deepEqual(await cancelOrderWith(f.deps, f.owner, id, changedMyMind), { ok: true, value: undefined });
  assert.equal(f.orders.stored(id).kind, "cancelled");
});

await test("race: AddItem after a place gets OrderNotDraft, and the item is not in the order", async () => {
  const f = await setup();
  const id = await draftWithItem(f);
  f.orders.beforeNextSave(() => {
    placedBehindTheBack(f, id);
  });
  assert.deepEqual(await addItemTo(f.deps, f.owner, id, sku, one), { ok: false, error: "order-not-draft" });
  const stored = f.orders.stored(id);
  assert.ok(stored.kind === "placed" && stored.items.length === 1);
});

await test("race: CancelOrder twice gets OrderAlreadyCancelled, and the first reason stands", async () => {
  const f = await setup();
  const id = await draftWithItem(f);
  f.orders.beforeNextSave(() => {
    cancelledBehindTheBack(f, id);
  });
  assert.deepEqual(await cancelOrderWith(f.deps, f.owner, id, changedMyMind), {
    ok: false,
    error: "order-already-cancelled",
  });
  const stored = f.orders.stored(id);
  assert.ok(stored.kind === "cancelled" && stored.reason === "someone was quicker");
});

await test("an order that keeps changing is given up on after three attempts", async () => {
  const f = await setup();
  const id = await draftWithItem(f);
  const saves = f.orders.saves();
  const bump = (): void => {
    f.orders.overwrite(f.orders.stored(id));
    f.orders.beforeNextSave(bump);
  };
  f.orders.beforeNextSave(bump);
  assert.deepEqual(await placeOrderWith(f.deps, f.owner, id), { ok: false, error: "conflict" });
  assert.equal(f.orders.saves() - saves, 3);
});
