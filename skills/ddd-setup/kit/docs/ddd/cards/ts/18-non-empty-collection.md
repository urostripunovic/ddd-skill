# Non-empty collection: TypeScript

The rules are in [the card](../18-non-empty-collection.md).

```ts
export type Result<T, E> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E };

export type NonEmpty<T> = readonly [T, ...T[]];

export type Item = { readonly sku: string };

const MAX_ITEMS = 200;

export function parseItems(items: readonly Item[]): Result<NonEmpty<Item>, "empty-order" | "too-many-items"> {
  if (items.length > MAX_ITEMS) return { ok: false, error: "too-many-items" };
  const [first, ...rest] = items;
  if (first === undefined) return { ok: false, error: "empty-order" };
  return { ok: true, value: [first, ...rest] };
}

export type DraftOrder = { readonly kind: "draft"; readonly items: readonly Item[] };
export type PlacedOrder = { readonly kind: "placed"; readonly items: NonEmpty<Item> };

// The only place the rule is checked. After this, the type carries it.
export function place(order: DraftOrder): Result<PlacedOrder, "empty-order" | "too-many-items"> {
  const items = parseItems(order.items);
  if (!items.ok) return items;
  return { ok: true, value: { kind: "placed", items: items.value } };
}

export function firstItem(order: PlacedOrder): Item {
  return order.items[0];
}
```
