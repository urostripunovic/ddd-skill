# Repository: TypeScript

The rules are in [the card](../08-repository.md).

```ts
export type OrderId = string & { readonly __brand: "OrderId" };

export type DraftOrder = { readonly kind: "draft"; readonly id: OrderId };
export type PlacedOrder = { readonly kind: "placed"; readonly id: OrderId; readonly placedAt: Date };
export type Order = DraftOrder | PlacedOrder;

// Declared in the domain so the domain owns the contract; the database
// implementation lives in infrastructure and imports this type.
export type Orders = {
  readonly byId: (id: OrderId) => Promise<Order | undefined>;
  readonly save: (order: Order) => Promise<void>;
};
```
