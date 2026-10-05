# Decider: TypeScript

The rules are in [the card](../11-decider.md).

```ts
export type Result<T, E> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E };

export type OrderId = string & { readonly __brand: "OrderId" };

export type NoOrder = { readonly kind: "none" };
export type DraftOrder = { readonly kind: "draft"; readonly id: OrderId; readonly itemCount: number };
export type PlacedOrder = { readonly kind: "placed"; readonly id: OrderId; readonly placedAt: Date };
export type Order = NoOrder | DraftOrder | PlacedOrder;

export type Command =
  | { readonly type: "create-order"; readonly id: OrderId }
  | { readonly type: "add-item" }
  | { readonly type: "place-order"; readonly at: Date };

export type OrderEvent =
  | { readonly type: "order-created"; readonly id: OrderId }
  | { readonly type: "item-added" }
  | { readonly type: "order-placed"; readonly at: Date };

export type DecideError = "order-already-exists" | "order-not-draft" | "empty-order";

type Decision = Result<readonly OrderEvent[], DecideError>;

function assertNever(x: never): never {
  // eslint-disable-next-line no-restricted-syntax -- an unhandled variant is a bug, not a business failure
  throw new Error(`unhandled variant: ${JSON.stringify(x)}`);
}

export const initialState: Order = { kind: "none" };

// The rule lives here, behind a parameter type that only a draft satisfies.
function place(order: DraftOrder, at: Date): Decision {
  if (order.itemCount === 0) return { ok: false, error: "empty-order" };
  return { ok: true, value: [{ type: "order-placed", at }] };
}

export function decide(command: Command, state: Order): Decision {
  switch (command.type) {
    case "create-order":
      if (state.kind !== "none") return { ok: false, error: "order-already-exists" };
      return { ok: true, value: [{ type: "order-created", id: command.id }] };
    case "add-item":
      if (state.kind !== "draft") return { ok: false, error: "order-not-draft" };
      return { ok: true, value: [{ type: "item-added" }] };
    case "place-order":
      if (state.kind !== "draft") return { ok: false, error: "order-not-draft" };
      return place(state, command.at);
    default:
      return assertNever(command);
  }
}

// Throwing is correct here: an event that does not fit the state means the stored history is corrupt, which is a bug.
function corruptHistory(state: Order, event: OrderEvent): never {
  // eslint-disable-next-line no-restricted-syntax -- corrupt stored history is a bug, not a business failure
  throw new Error(`corrupt history: ${event.type} after ${state.kind}`);
}

export function evolve(state: Order, event: OrderEvent): Order {
  switch (event.type) {
    case "order-created":
      return { kind: "draft", id: event.id, itemCount: 0 };
    case "item-added":
      if (state.kind !== "draft") return corruptHistory(state, event);
      return { ...state, itemCount: state.itemCount + 1 };
    case "order-placed":
      if (state.kind !== "draft") return corruptHistory(state, event);
      return { kind: "placed", id: state.id, placedAt: event.at };
    default:
      return assertNever(event);
  }
}

export function replay(events: readonly OrderEvent[]): Order {
  let state = initialState;
  for (const event of events) {
    state = evolve(state, event);
  }
  return state;
}
```
