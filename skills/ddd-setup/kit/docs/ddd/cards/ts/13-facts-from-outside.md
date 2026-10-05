# Facts from outside the aggregate: TypeScript

The rules are in [the card](../13-facts-from-outside.md).

```ts
export type Result<T, E> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E };

export type Sku = string & { readonly __brand: "Sku" };
export type Quantity = number & { readonly __brand: "Quantity" };
export type Price = bigint & { readonly __brand: "Price" };

// A fact gathered by the workflow: what was learned, about what, and when.
export type PriceQuote = {
  readonly sku: Sku;
  readonly unit: Price;
  readonly quotedAt: Date;
};

export type Item = {
  readonly sku: Sku;
  readonly quantity: Quantity;
  // Captured when the item is added, so a later price change does not alter this order.
  readonly unit: Price;
};

export type DraftOrder = { readonly kind: "draft"; readonly items: readonly Item[] };

export type AddItemError = "quote-mismatch" | "quote-expired";

const MAX_QUOTE_AGE_MS = 5 * 60 * 1000;

export function addItem(
  order: DraftOrder,
  sku: Sku,
  quantity: Quantity,
  quote: PriceQuote,
  now: Date,
): Result<DraftOrder, AddItemError> {
  if (quote.sku !== sku) return { ok: false, error: "quote-mismatch" };
  if (now.getTime() - quote.quotedAt.getTime() > MAX_QUOTE_AGE_MS) {
    return { ok: false, error: "quote-expired" };
  }
  return {
    ok: true,
    value: { kind: "draft", items: [...order.items, { sku, quantity, unit: quote.unit }] },
  };
}

export type AddItemDeps = {
  readonly quotePrice: (sku: Sku) => Promise<PriceQuote>;
  readonly now: () => Date;
};

// The workflow gathers the fact, then hands it to the pure decision.
export async function addItemToOrder(
  deps: AddItemDeps,
  order: DraftOrder,
  sku: Sku,
  quantity: Quantity,
): Promise<Result<DraftOrder, AddItemError>> {
  const quote = await deps.quotePrice(sku);
  return addItem(order, sku, quantity, quote, deps.now());
}
```
