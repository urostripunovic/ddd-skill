# Context: <name>

Status: draft
<!-- One line, always starting with "Status:". Values:
     draft
     derived from code, not confirmed, read at <short commit>
     approved by <name> on <date>, model-hash <output of tools/model-hash.sh for this file>
     Either may end with ", reviewed <date> at <hash>" once a model review has no blockers left.
     Write this line with tools/stamp-model.sh (approve, review or draft), never by hand.
     The hash covers the model before the trailing "## Migration" / "## Amendments" / "## Pending"
     sections, except the Status line. Keep all model sections before that tail. -->

Depth: standard
<!-- Optional: Strict commands: PlaceOrder, CancelOrder
     Use names from the Commands blocks, comma-separated. Each one's strict scope (its Issued by row,
     matrix column, failures, use-case failures, events, the rows that name it, and every primitive
     its states and inputs use) is strict even in a standard context. tools/check-model.sh prints it. -->
<!-- How much is settled before code is written.
     standard: the core is confirmed (states, commands and who may issue them, invariants, aggregate
               boundaries, the glossary). The rest is a best guess marked "(assumed)", and implementation
               records what it learns under Amendments.
     strict:   everything is confirmed and reviewed before code, and implementation stops at any gap.
               For money, credentials, authorisation, and anything that cannot be undone. -->

<!-- "(assumed)" at the end of a cell marks a value nobody has confirmed: a bound, what a failure carries,
     an edge case. It is implemented as written, and it is the first place to look when behaviour surprises.
     It is never used for the core: an "Issued by" cell or an invariant marked "(assumed)", or holding a
     placeholder such as TBD, fails tools/check-model.sh. Ask, and list it under Open questions until answered. -->

<!-- tools/check-model.sh reads this file. Keep the headings, the table columns and the notation in the
     code blocks as they are here, or the check cannot find them. The Order example below is only an
     example: replace it. -->

## The flow

<!-- The model as a story, for a person to read from start to finish before any table. Five to fifteen
     numbered steps in plain sentences, in the order things happen, each naming the command it is about
     in backticks. Who does what, what has to be true, what happens next, and the one or two ways it
     usually goes wrong. No bounds, no payloads, no edge cases: those are in the tables below, and a
     reader who wants them follows the command name there.

     1. A customer starts an order (`StartOrder`). It is theirs, and it is empty.
     2. They add items while it is a draft (`AddItem`). Each item takes its price from a quote that is at most five minutes old.
     3. They place it (`PlaceOrder`). An empty order cannot be placed. From here the warehouse is picking, so nothing can be added.
     4. They may cancel a draft or a placed order (`CancelOrder`), with a reason. Cancelling is final. -->

## Domain primitives

Every bound is stated, with the reason for it. "No limit" is not an answer. A reason can be short ("a homelab never needs more"), and a bound nobody has confirmed says `(assumed)` in the Why column: a limit with no reason gets questioned in every review.

| Name | Underlying type | Rules (range, length, format, allowed characters) | Why this limit | Sensitive? |
|---|---|---|---|---|
| <!-- Quantity --> | <!-- integer --> | <!-- 1..1000 --> | <!-- the largest pallet the warehouse ships holds 1000 --> | <!-- no --> |

## Aggregate: <name>

### States

`Timestamp` and `Boolean` are built in. Every other type is a primitive from the table above or is defined in this block. `terminal` lists the states nothing leads out of.

```
type Order = DraftOrder | PlacedOrder | CancelledOrder
terminal CancelledOrder

DraftOrder     = { id: OrderId, items: Item[] }
PlacedOrder    = { id: OrderId, items: Item[] (at least 1), placedAt: Timestamp }
CancelledOrder = { id: OrderId, reason: CancellationReason }

Item = { sku: Sku, quantity: Quantity }
```

What ends each state that is not terminal if nothing happens: a command the scheduler issues, and after how long, or "no expiry".

- DraftOrder: no expiry
- PlacedOrder: no expiry

### Commands

A command lists only the states it is legal in, so "wrong state" is never one of its failures. A command that creates the aggregate starts from `()`.

```
StartOrder  : () -> DraftOrder + [OrderStarted]
AddItem     : DraftOrder -> DraftOrder
PlaceOrder  : DraftOrder -> PlacedOrder + [OrderPlaced] | EmptyOrder
CancelOrder : DraftOrder | PlacedOrder -> CancelledOrder + [OrderCancelled]
```

Who may issue each command is part of the model. A command that time issues ("48 hours after the offer") names the scheduler and the delay here. **Input** lists the values a command takes that are not in the state it starts from, as `name: Type` with a primitive or a defined type, or `none`.

| Command | Issued by | Input | Notes |
|---|---|---|---|
| <!-- PlaceOrder --> | <!-- the customer who owns the order --> | <!-- none --> | |

### Command × state matrix

One row per state, one column per command (creating commands are left out). A cell is `yes`, or `no:` followed by the business's reason. The `no` cells are the point: each one is a question somebody answered. A `no` without a reason has not been asked yet.

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

Each invariant names where it is enforced: **type** (cannot be represented), **constructor**, **decision function**, or **not in types** (say how it is checked instead). The last column lists every command that could break it if written carelessly, or `none`.

| # | Invariant | Enforced by | Commands that could break it |
|---|---|---|---|
| 1 | <!-- A placed order has at least one item --> | <!-- decision function PlaceOrder --> | <!-- PlaceOrder --> |

### Failures

| Failure | When | Data it carries |
|---|---|---|
| <!-- EmptyOrder --> | <!-- placing an order with no items --> | <!-- none --> |

### Use-case failures

Failures that belong to the use case and not to a decision: the aggregate does not exist, the caller may not issue the command, or the aggregate is not in a state the command accepts. The workflow raises these when it loads and narrows the aggregate.

| Failure | Raised when |
|---|---|
| <!-- OrderNotFound --> | <!-- no order has the given id --> |
| <!-- OrderNotDraft --> | <!-- PlaceOrder is requested for an order that is not a draft --> |

### Examples

Rules with real values filled in, as the domain expert confirmed them. Every command and every failure has at least one, and every bound has one on each side of it. These rows become the table tests, so write values, not descriptions: "an order of 9 999 kr", not "a small order". Row numbers are permanent, because tests and tickets refer to them: a new row takes the next unused number, and a removed row leaves a gap.

| # | Covers | Given | When | Then |
|---|---|---|---|---|
| 1 | <!-- EmptyOrder, invariant 1 --> | <!-- a draft order with no items --> | <!-- PlaceOrder at 10:00 --> | <!-- EmptyOrder --> |
| 2 | <!-- PlaceOrder --> | <!-- a draft order with 2 × ABC-1 --> | <!-- PlaceOrder at 10:00 --> | <!-- PlacedOrder placed at 10:00, OrderPlaced --> |

### Races

Two commands for the same aggregate that arrive at the same moment: two browser tabs, a customer and a scheduler, a retry. For each pair where the order matters, the business says which wins and what the other is told.

| Commands | Who wins | What the other gets |
|---|---|---|
| <!-- PlaceOrder and CancelOrder on the same draft --> | <!-- whichever is saved first --> | <!-- PlaceOrder after a cancel: OrderNotDraft. CancelOrder after a place: it succeeds, a placed order can be cancelled --> |

### Facts from outside

Data a command needs that the aggregate does not hold, including who the caller is. For each: where it comes from, what is checked before it is believed, what happens when that fails or the source does not answer, and whether it may be slightly out of date. This is where the model meets the systems around it; the code for it is an adapter.

| Fact | Used by | Source | Believed when | If not, or no answer | May it be stale? |
|---|---|---|---|---|---|
| <!-- PriceQuote { sku, unitPrice, quotedAt } --> | <!-- AddItem --> | <!-- Pricing service --> | <!-- the answer is for the product asked about, and the price is a valid Price --> | <!-- PricingUnavailable; nothing is added --> | <!-- yes, up to 5 minutes --> |
| <!-- Customer { email } --> | <!-- every command --> | <!-- the sign-in token from the identity provider --> | <!-- signature, issuer, audience and expiry are checked, and the email is marked verified --> | <!-- NotAuthenticated --> | <!-- yes, until the token expires: at most 15 minutes --> |

## Rules across aggregates

A rule inside one aggregate holds the moment a command finishes. A rule that involves two aggregates, or two instances of one, does not: it either holds a moment later, or the two are really one aggregate. The business chooses, by what it costs when the rule is broken for a few seconds.

| Rule | Involves | Immediate or eventual | Kept by | While it does not hold |
|---|---|---|---|---|
| <!-- A product is never sold beyond its stock --> | <!-- Order, Stock --> | <!-- eventual --> | <!-- policy: OrderPlaced reserves stock; a failed reservation cancels the order --> | <!-- the customer sees a placed order for up to a minute, then a cancellation with an apology --> |

## Policies

"Whenever this has happened, do that." One row per reaction to an event, in this context or another.

| When (event) | Then (command) | On | If the command fails |
|---|---|---|---|
| <!-- OrderPlaced --> | <!-- ReserveStock --> | <!-- Stock, in Inventory --> | <!-- CancelOrder with reason "out of stock" --> |

## Decisions

Why, where the model alone does not say. Only for a decision that is hard to reverse, would surprise a later reader, and had a real alternative. An aggregate boundary that was chosen over another belongs here, with the example that decided it.

| Date | Decision | Why, and what was rejected |
|---|---|---|
| <!-- 2026-01-15 --> | <!-- A handed-over order cannot be cancelled; it becomes a return --> | <!-- Cancelling after hand-over needed a carrier recall, which the business does not offer --> |

## Open questions

<!-- Anything assumed and not confirmed by someone who knows the domain. Write "None." when there are none. -->

## Amendments

What implementation learned after approval, at standard depth and outside any strict scope. Rows here do not change the model-hash, so recording one does not undo the approval. At strict depth, or touching a strict scope, `tools/check-model.sh` rejects them: those gaps go under Pending and through `ddd-modelling`. Fold them into the sections above, and approve again, when there are enough to be worth it or before the next larger change. Write "None." when there are none.

| Date | Section | The model said | What was learned, and what the code does |
|---|---|---|---|
| <!-- 2026-01-20 --> | <!-- Examples, row 44 --> | <!-- 5 attempts are recorded --> | <!-- With 1 000 requests at once the retries run out first: at most 5 are recorded. The test asserts "at most 5 tokens, exactly 1 delivered" --> |

## Pending

Gaps implementation found and cannot settle itself: a gap in the core, or any gap at strict depth or in a strict scope. Each row waits for an answer from the user; `ddd-modelling` settles it in the model and removes the row once the model is approved again. Rows here do not change the model-hash. Write "None." when there are none.

| Date | Command | The gap, and the question for the user | Found while |
|---|---|---|---|
| <!-- 2026-01-21 --> | <!-- RefundPayment --> | <!-- Is a refund rounded to whole öre, and which way? The model gives no rounding rule --> | <!-- writing example 12 as a test --> |
