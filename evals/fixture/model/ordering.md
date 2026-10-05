# Context: Ordering

Status: draft

Depth: strict

## The flow

1. A signed-in customer starts an order (`StartOrder`). It is theirs, and it is empty.
2. While it is a draft, they add items (`AddItem`). Each item takes its price from a quote at most five minutes old, and an order holds at most 100 items.
3. They place it (`PlaceOrder`). An empty order cannot be placed. From here the warehouse is picking, so nothing can be added.
4. They may cancel a draft or a placed order (`CancelOrder`), with a reason. Cancelling is final.

## Domain primitives

| Name | Underlying type | Rules (range, length, format, allowed characters) | Sensitive? |
|---|---|---|---|
| OrderId | string | UUID, exactly 36 characters | no |
| Sku | string | 3..32 characters, only A-Z, 0-9 and hyphen | no |
| Quantity | integer | 1..1000 | no |
| Price | integer | minor units, 0..100000000, never a float | no |
| CustomerEmail | string | at most 254 characters, one @ | yes |
| CancellationReason | string | 1..200 characters | no |

## Aggregate: Order

### States

```
type Order = DraftOrder | PlacedOrder | CancelledOrder
terminal CancelledOrder

DraftOrder     = { id: OrderId, customer: CustomerEmail, items: Item[] }
PlacedOrder    = { id: OrderId, customer: CustomerEmail, items: Item[] (at least 1), placedAt: Timestamp }
CancelledOrder = { id: OrderId, customer: CustomerEmail, reason: CancellationReason }

Item = { sku: Sku, quantity: Quantity, unitPrice: Price }
```

### Commands

```
StartOrder  : () -> DraftOrder
AddItem     : DraftOrder -> DraftOrder | QuoteExpired | TooManyItems
PlaceOrder  : DraftOrder -> PlacedOrder + [OrderPlaced] | EmptyOrder
CancelOrder : DraftOrder | PlacedOrder -> CancelledOrder + [OrderCancelled]
```

| Command | Issued by | Notes |
|---|---|---|
| StartOrder | any signed-in customer | The order belongs to that customer |
| AddItem | the customer who owns the order | |
| PlaceOrder | the customer who owns the order | |
| CancelOrder | the customer who owns the order | |

### Command × state matrix

| State | AddItem | PlaceOrder | CancelOrder |
|---|---|---|---|
| DraftOrder | yes | yes | yes |
| PlacedOrder | no: the warehouse starts picking as soon as an order is placed; the customer starts a new order | no: it is already placed | yes |
| CancelledOrder | no: cancelling is final | no: cancelling is final | no: it is already cancelled, and the first reason stands |

### Events

| Event | Carries | Consumed by |
|---|---|---|
| OrderPlaced | orderId, at | Billing |
| OrderCancelled | orderId, reason, at | Billing |

### Invariants

| # | Invariant | Enforced by | Commands that could break it |
|---|---|---|---|
| 1 | A placed order has at least one item | decision function PlaceOrder | PlaceOrder |
| 2 | A placed order always has a time of placing | type | none |
| 3 | A cancelled order always has a reason | type | none |
| 4 | Only a draft order can receive items | type (AddItem takes DraftOrder) | AddItem |
| 5 | A draft or placed order can be cancelled; a cancelled order cannot | type (CancelOrder takes DraftOrder or PlacedOrder) | CancelOrder |
| 6 | An order has at most 100 items | decision function AddItem | AddItem |

### Failures

| Failure | When | Data it carries |
|---|---|---|
| EmptyOrder | placing an order with no items | none |
| QuoteExpired | adding an item with a price quote more than 5 minutes old | none |
| TooManyItems | adding an item to an order that already has 100 | none |

### Use-case failures

| Failure | Raised when |
|---|---|
| OrderNotFound | no order has the given id |
| OrderNotDraft | AddItem or PlaceOrder is requested for an order that is not a draft |
| OrderAlreadyCancelled | CancelOrder is requested for a cancelled order |
| NotAllowed | the caller does not own the order |

### Examples

| # | Covers | Given | When | Then |
|---|---|---|---|---|
| 1 | StartOrder | no order | StartOrder for a@example.com | a DraftOrder for a@example.com with no items |
| 2 | AddItem | a draft order with no items; ABC-1 quoted at 999 at 10:00 | AddItem 2 × ABC-1 at 10:01 | a DraftOrder with one item: 2 × ABC-1 at 999 |
| 3 | AddItem | a draft order with 1 × ABC-1 | AddItem 1 × ABC-1 again | a DraftOrder with two items; the same product twice is two items, not one with quantity 2 |
| 4 | QuoteExpired | a draft order; ABC-1 quoted at 10:00 | AddItem at 10:05:00, and at 10:05:01 | accepted at 10:05:00; QuoteExpired at 10:05:01 |
| 5 | TooManyItems, invariant 6 | a draft order with 99 items, and one with 100 | AddItem | accepted with 99, giving 100; TooManyItems with 100 |
| 6 | Quantity bounds | a draft order | AddItem with quantity 0, 1, 1000 and 1001 | 1 and 1000 are accepted; 0 and 1001 are not a Quantity |
| 7 | EmptyOrder, invariant 1 | a draft order with no items | PlaceOrder at 10:00 | EmptyOrder |
| 8 | PlaceOrder | a draft order with 1 × ABC-1 at 999 | PlaceOrder at 10:00 | a PlacedOrder with that item, placed at 10:00; OrderPlaced at 10:00 |
| 9 | CancelOrder | a draft order with no items | CancelOrder at 10:05, reason "changed my mind" | a CancelledOrder with that reason; OrderCancelled at 10:05 |
| 10 | CancelOrder | an order placed at 10:00 | CancelOrder at 10:05, reason "found it cheaper" | a CancelledOrder with that reason; OrderCancelled at 10:05 |

### Races

| Commands | Who wins | What the other gets |
|---|---|---|
| PlaceOrder and CancelOrder on the same draft | whichever is saved first | PlaceOrder after the cancel: OrderNotDraft. CancelOrder after the place: it succeeds |
| AddItem and PlaceOrder on the same draft | whichever is saved first | AddItem after the place: OrderNotDraft, and the item is not in the order |
| CancelOrder twice | the first | OrderAlreadyCancelled; the first reason stands |

### Facts from outside

| Fact | Used by | Source | May it be stale? |
|---|---|---|---|
| PriceQuote { sku, unitPrice, quotedAt } | AddItem | Pricing service | yes, up to 5 minutes |

## Rules across aggregates

None. Every rule in this context concerns one order.

## Policies

None in this context. Billing reacts to OrderPlaced and OrderCancelled, and that policy is Billing's.

## Decisions

| Date | Decision | Why, and what was rejected |
|---|---|---|
| 2026-10-03 | A placed order cannot receive items | The warehouse starts picking at once. Allowing changes until picking starts was rejected: Ordering would have to know the warehouse's state. |

## Open questions

None.
