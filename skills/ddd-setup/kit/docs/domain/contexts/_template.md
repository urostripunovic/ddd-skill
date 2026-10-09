# Context: <name>

Status: draft
<!-- draft, then "approved <date>" on the user's yes; ", reviewed <date>" is added after a model review. -->

Depth: standard
<!-- standard or strict. Optional next line: Strict commands: PlaceOrder, CancelOrder -->

## The flow

<!-- 1. A customer starts an order (`StartOrder`). It is theirs, and it is empty.
     2. They add items while it is a draft (`AddItem`). Each item takes its price from a quote that is at most five minutes old.
     3. They place it (`PlaceOrder`). An empty order cannot be placed. From here the warehouse is picking, so nothing can be added.
     4. They may cancel a draft or a placed order (`CancelOrder`), with a reason. Cancelling is final. -->

## Domain primitives

| Name | Underlying type | Rules (range, length, format, allowed characters) | Why this limit | Sensitive? |
|---|---|---|---|---|
| <!-- Quantity --> | <!-- integer --> | <!-- 1..1000 --> | <!-- the largest pallet the warehouse ships holds 1000 --> | <!-- no --> |

## Aggregate: <name>

### States

```
type Order = DraftOrder | PlacedOrder | CancelledOrder
terminal CancelledOrder

DraftOrder     = { id: OrderId, items: Item[] }
PlacedOrder    = { id: OrderId, items: Item[] (at least 1), placedAt: Timestamp }
CancelledOrder = { id: OrderId, reason: CancellationReason }

Item = { sku: Sku, quantity: Quantity }
```

- DraftOrder: no expiry
- PlacedOrder: no expiry

### Commands

```
StartOrder  : () -> DraftOrder + [OrderStarted]
AddItem     : DraftOrder -> DraftOrder
PlaceOrder  : DraftOrder -> PlacedOrder + [OrderPlaced] | EmptyOrder
CancelOrder : DraftOrder | PlacedOrder -> CancelledOrder + [OrderCancelled]
```

| Command | Issued by | Input | Notes |
|---|---|---|---|
| <!-- PlaceOrder --> | <!-- the customer who owns the order --> | <!-- none --> | |

### Command × state matrix

| State | AddItem | PlaceOrder | CancelOrder |
|---|---|---|---|
| <!-- DraftOrder --> | <!-- yes --> | <!-- yes --> | <!-- yes --> |
| <!-- PlacedOrder --> | <!-- no: the warehouse has started picking; a new order is needed --> | <!-- no: it is already placed --> | <!-- yes --> |
| <!-- CancelledOrder --> | <!-- no: cancelling is final --> | <!-- no: cancelling is final --> | <!-- no: it is already cancelled --> |

### Events

| Event | Carries | Consumed by |
|---|---|---|
| <!-- OrderPlaced --> | <!-- orderId, at --> | <!-- Billing --> |

### Invariants

| # | Invariant | Enforced by | Commands that could break it |
|---|---|---|---|
| 1 | <!-- A placed order has at least one item --> | <!-- decision function PlaceOrder --> | <!-- PlaceOrder --> |

### Failures

| Failure | When | Data it carries |
|---|---|---|
| <!-- EmptyOrder --> | <!-- placing an order with no items --> | <!-- none --> |

### Use-case failures

| Failure | Raised when |
|---|---|
| <!-- OrderNotFound --> | <!-- no order has the given id --> |
| <!-- OrderNotDraft --> | <!-- PlaceOrder is requested for an order that is not a draft --> |

### Examples

| # | Covers | Given | When | Then |
|---|---|---|---|---|
| 1 | <!-- EmptyOrder, invariant 1 --> | <!-- a draft order with no items --> | <!-- PlaceOrder at 10:00 --> | <!-- EmptyOrder --> |
| 2 | <!-- PlaceOrder --> | <!-- a draft order with 2 × ABC-1 --> | <!-- PlaceOrder at 10:00 --> | <!-- PlacedOrder placed at 10:00, OrderPlaced --> |

### Races

| Commands | Who wins | What the other gets |
|---|---|---|
| <!-- PlaceOrder and CancelOrder on the same draft --> | <!-- whichever is saved first --> | <!-- PlaceOrder after a cancel: OrderNotDraft. CancelOrder after a place: it succeeds, a placed order can be cancelled --> |

### Facts from outside

| Fact | Used by | Source | Believed when | If not, or no answer | May it be stale? |
|---|---|---|---|---|---|
| <!-- PriceQuote { sku, unitPrice, quotedAt } --> | <!-- AddItem --> | <!-- Pricing service --> | <!-- the answer is for the product asked about, and the price is a valid Price --> | <!-- PricingUnavailable; nothing is added --> | <!-- yes, up to 5 minutes --> |
| <!-- Customer { email } --> | <!-- every command --> | <!-- the sign-in token from the identity provider --> | <!-- signature, issuer, audience and expiry are checked, and the email is marked verified --> | <!-- NotAuthenticated --> | <!-- yes, until the token expires: at most 15 minutes --> |

## Rules across aggregates

| Rule | Involves | Immediate or eventual | Kept by | While it does not hold |
|---|---|---|---|---|
| <!-- A product is never sold beyond its stock --> | <!-- Order, Stock --> | <!-- eventual --> | <!-- policy: OrderPlaced reserves stock; a failed reservation cancels the order --> | <!-- the customer sees a placed order for up to a minute, then a cancellation with an apology --> |

## Policies

| When (event) | Then (command) | On | If the command fails |
|---|---|---|---|
| <!-- OrderPlaced --> | <!-- ReserveStock --> | <!-- Stock, in Inventory --> | <!-- CancelOrder with reason "out of stock" --> |

## Decisions

| Date | Decision | Why, and what was rejected |
|---|---|---|
| <!-- 2026-01-15 --> | <!-- A handed-over order cannot be cancelled; it becomes a return --> | <!-- Cancelling after hand-over needed a carrier recall, which the business does not offer --> |

## Open questions

<!-- Anything assumed and not confirmed by someone who knows the domain. Write "None." when there are none. -->

## Amendments

| Date | Section | The model said | What was learned, and what the code does |
|---|---|---|---|
| <!-- 2026-01-20 --> | <!-- Examples, row 44 --> | <!-- 5 attempts are recorded --> | <!-- With 1 000 requests at once the retries run out first: at most 5 are recorded. The test asserts "at most 5 tokens, exactly 1 delivered" --> |

## Pending

| Date | Command | The gap, and the question for the user | Found while |
|---|---|---|---|
| <!-- 2026-01-21 --> | <!-- RefundPayment --> | <!-- Is a refund rounded to whole öre, and which way? The model gives no rounding rule --> | <!-- writing example 12 as a test --> |
