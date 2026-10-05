# Policy

**Use when:** something must happen because something else happened, across aggregates or contexts: "whenever an order is placed, reserve stock".

**Never:** have one aggregate's decision function change another aggregate, or put the reaction inside the workflow that produced the event. The first workflow then has to know every consequence of its event.

## Rules

- A policy is a pure function from an event to the commands that follow from it, often none. It is named in the ubiquitous language, as the business says it: "whenever X, then Y".
- It holds no rule of the target aggregate. It issues a command; the target's decision function decides, and may refuse.
- Events are delivered at least once, so every command a policy issues is an [idempotent command](15-idempotent-command.md) whose ID is derived from the event's ID.
- The switch over events lists every variant. A new event then forces a choice about whether the policy reacts to it.
- The handler around the policy does the I/O: receive the event, call the policy, send the commands. The policy does none.
- A refused command is an outcome the model must name: what corrects it, and who is told.

## Enforced by

- Both: the policy's signature. It receives an event and returns values, so it has nothing to call.
- Go: `gochecksumtype` on the event switch.
- TypeScript: `switch-exhaustiveness-check` and `assertNever`.

## Anti-pattern

```go
func PlaceOrder(ctx context.Context, id OrderID) error {
	// ...
	stock.Reserve(ctx, order.Items()) // Ordering now depends on Stock, and on every later consequence
	return nil
}
```

## Example

One file per language: [Go](go/16-policy.md), [TypeScript](ts/16-policy.md). Read only the one for the language you are writing.

## Corrections

<!-- Add a dated line each time an agent gets this pattern wrong. -->
