# Policy: TypeScript

The rules are in [the card](../16-policy.md).

```ts
export type EventId = string & { readonly __brand: "EventId" };
export type OrderId = string & { readonly __brand: "OrderId" };
export type CommandId = string & { readonly __brand: "CommandId" };

// Ordering's events as this context sees them, after its anticorruption layer.
export type OrderEvent =
  | { readonly type: "order-placed"; readonly eventId: EventId; readonly orderId: OrderId }
  | { readonly type: "order-cancelled"; readonly eventId: EventId; readonly orderId: OrderId };

export type StockCommand =
  | { readonly type: "reserve-stock"; readonly commandId: CommandId; readonly orderId: OrderId }
  | { readonly type: "release-stock"; readonly commandId: CommandId; readonly orderId: OrderId };

// Derived, not generated, so a redelivered event yields the same command ID.
function commandIdFor(policy: string, event: EventId): CommandId {
  // eslint-disable-next-line @typescript-eslint/consistent-type-assertions -- built from an already valid EventId and a constant
  return `${policy}:${event}` as CommandId;
}

function assertNever(value: never): never {
  // eslint-disable-next-line no-restricted-syntax -- an unhandled variant is a bug, not a business failure
  throw new Error(`unhandled variant: ${JSON.stringify(value)}`);
}

// "Whenever an order is placed, reserve its stock; whenever it is cancelled, release it."
export function reservationPolicy(event: OrderEvent): readonly StockCommand[] {
  const name = "reservation";
  switch (event.type) {
    case "order-placed":
      return [{ type: "reserve-stock", commandId: commandIdFor(name, event.eventId), orderId: event.orderId }];
    case "order-cancelled":
      return [{ type: "release-stock", commandId: commandIdFor(name, event.eventId), orderId: event.orderId }];
    default:
      return assertNever(event);
  }
}
```
