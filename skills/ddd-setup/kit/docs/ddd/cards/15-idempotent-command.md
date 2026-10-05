# Idempotent command

**Use when:** a command can arrive more than once: a client retries after a timeout, a queue redelivers, a user double-clicks. Assume this for every command that crosses a network.

**Never:** look up whether the command was handled and then act, with nothing else. Two copies can both pass the lookup.

## Rules

- The caller chooses a command ID and sends the same one on every retry. It is a domain primitive, parsed at the boundary.
- The state change and the command ID are stored in one transaction. A unique constraint on the command ID rejects the second writer.
- A repeat returns the first outcome and does not decide again. To the caller, a retry of a command that succeeded is a success, not "wrong state".
- The workflow looks the ID up first so a plain retry is answered without loading anything. The constraint is what makes it correct; the lookup only makes it cheap.
- A command issued by a [policy](16-policy.md) derives its ID from the event that caused it, so a redelivered event produces the same command.
- The model says how long a command ID is remembered.

## Enforced by

- The database: the unique constraint on the command ID.
- Both: the workflow's signature. It cannot be called without a command ID.

## Anti-pattern

```go
if !repo.WasHandled(cmdID) { // two retries can both get false here
	repo.Save(order)
	repo.MarkHandled(cmdID)
}
```

## Example

One file per language: [Go](go/15-idempotent-command.md), [TypeScript](ts/15-idempotent-command.md). Read only the one for the language you are writing.

## Corrections

<!-- Add a dated line each time an agent gets this pattern wrong. -->
