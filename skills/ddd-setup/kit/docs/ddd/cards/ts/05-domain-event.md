# Domain event: TypeScript

The rules are in [the card](../05-domain-event.md).

```ts
export type OrderId = string & { readonly __brand: "OrderId" };

export type OrderPlaced = {
  readonly type: "order-placed";
  readonly orderId: OrderId;
  readonly at: Date;
};

export type OrderCancelled = {
  readonly type: "order-cancelled";
  readonly orderId: OrderId;
  readonly reason: string;
  readonly at: Date;
};

export type OrderEvent = OrderPlaced | OrderCancelled;

function assertNever(x: never): never {
  // eslint-disable-next-line no-restricted-syntax -- an unhandled variant is a bug, not a business failure
  throw new Error(`unhandled variant: ${JSON.stringify(x)}`);
}

export function describe(event: OrderEvent): string {
  switch (event.type) {
    case "order-placed":
      return `order ${event.orderId} placed`;
    case "order-cancelled":
      return `order ${event.orderId} cancelled: ${event.reason}`;
    default:
      return assertNever(event);
  }
}
```
