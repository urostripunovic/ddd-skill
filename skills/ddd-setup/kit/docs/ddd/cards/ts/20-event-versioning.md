# Event versioning: TypeScript

The rules are in [the card](../20-event-versioning.md).

Check as: boundary

```ts
export type Result<T, E> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E };

export type OrderId = string & { readonly __brand: "OrderId" };
export type Channel = "web" | "app";

// The domain event has one shape: the current one.
export type OrderPlaced = {
  readonly type: "order-placed";
  readonly orderId: OrderId;
  readonly channel: Channel;
};

export type StoredEvent = {
  readonly type: string;
  readonly version: number;
  readonly data: unknown;
};

export type DecodeError = "unknown-event" | "corrupt-event";

function parseOrderId(raw: unknown): OrderId | undefined {
  if (typeof raw !== "string" || raw.length !== 36) return undefined;
  // eslint-disable-next-line @typescript-eslint/consistent-type-assertions -- the brand is applied only here, after validation
  return raw as OrderId;
}

function parseChannel(raw: unknown): Channel | undefined {
  return raw === "web" || raw === "app" ? raw : undefined;
}

function field(data: unknown, name: string): unknown {
  if (typeof data !== "object" || data === null) return undefined;
  const entry = Object.entries(data).find(([key]) => key === name);
  return entry?.[1];
}

export function decodeOrderPlaced(stored: StoredEvent): Result<OrderPlaced, DecodeError> {
  if (stored.type !== "order-placed") return { ok: false, error: "unknown-event" };

  const orderId = parseOrderId(field(stored.data, "orderId"));
  if (orderId === undefined) return { ok: false, error: "corrupt-event" };

  switch (stored.version) {
    case 1:
      // Model decision: the app launched together with version 2, so every earlier order came from the web.
      return { ok: true, value: { type: "order-placed", orderId, channel: "web" } };
    case 2: {
      const channel = parseChannel(field(stored.data, "channel"));
      if (channel === undefined) return { ok: false, error: "corrupt-event" };
      return { ok: true, value: { type: "order-placed", orderId, channel } };
    }
    default:
      return { ok: false, error: "unknown-event" };
  }
}
```
