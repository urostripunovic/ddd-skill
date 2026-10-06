# Facts from outside the aggregate

**Use when:** a decision needs data the aggregate does not hold: a current price, a stock level, a customer's credit limit, whether an email address is already taken.

**Never:** pass a repository, client, interface or callback into a decision function so it can fetch the data itself. That is I/O in the domain with one extra step.

## Rules

- The workflow fetches the data first and passes it to the decision function as a value. The decision stays pure.
- The value is a named domain type that says what was learned and when: `PriceQuote`, `StockLevel`, `CreditLimit`. Not a bare `bool` or number.
- A fact is already old when the decision uses it. For each fact, the model says whether that matters:
  - **It does not matter** (a price quoted a few seconds ago): give the fact a maximum age and let the decision reject one that is too old.
  - **It matters** (uniqueness, stock that must never go negative): the pre-check cannot guarantee it. Enforce it where the write happens, and translate the storage error into the named domain failure.
- Uniqueness across aggregates is enforced by a unique constraint in the database. Looking it up first is only for a friendlier error message; two requests can both pass the lookup.
- If a rule needs two aggregates to agree at the same instant, they are either one aggregate, or the model accepts a short inconsistency and names what corrects it. The model must say which.
- Record the fact that was used in the resulting state or event (the unit price at the time the item was added), so a later price change does not rewrite history.

## Enforced by

- Both: the decision function's signature. Its parameters are values, so it has nothing to call.
- The database: unique constraints and version checks ([repository](08-repository.md), [event stream repository](12-event-stream-repository.md)).

## Anti-pattern

```go
func AddItem(o DraftOrder, sku SKU, qty Quantity, prices PriceService) (DraftOrder, error) {
	price, err := prices.Current(sku) // I/O inside the decision
	// ...
}
```

## Example

One file per language: [Go](go/13-facts-from-outside.md), [TypeScript](ts/13-facts-from-outside.md). Read only the one for the language you are writing.

## Corrections

<!-- Add a dated line each time an agent gets this pattern wrong. -->
