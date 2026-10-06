# Authorisation

**Use when:** the model's "Issued by" column restricts who may issue a command, or on whose data.

**Never:** take the caller's identity from the request body, or leave the check to the HTTP handler alone. A second entry point (a queue consumer, an admin tool) would then skip it.

## Rules

- The caller is a domain value, the actor. The workflow receives it as a parameter.
- The only function that returns an actor is the one that verifies the credential. An actor cannot be written as a literal, so code that has one has been through verification.
- Kinds of actor are a sum type. A new kind then forces every rule to say what it may do.
- Each "Issued by" rule is a pure function of the actor and the loaded state. It is named after the command and tested like any decision.
- The workflow checks it after loading, because most rules depend on who owns the data, and before the decision and any write.
- "Not allowed" is a named use-case failure. Whether the outside world sees it as "not found" is the boundary's choice; say which in the model.
- Queries need the same check as commands. See [read model](19-read-model.md).

## Enforced by

- Both: the workflow's signature. It cannot be called without an actor.
- Go: the actor variants are unexported, so another package cannot name one or build one; it can only call `Authenticate`. `gochecksumtype` makes the switch over actor kinds exhaustive.
- TypeScript: the actor is branded and ESLint bans `as`, so an object literal is not an actor. `switch-exhaustiveness-check` makes the switch exhaustive.

## Anti-pattern

```ts
// The caller says who they are, and the handler believes it.
if (req.body.customerId !== order.customerId) return res.status(403).end();
```

## Example

One file per language: [Go](go/14-authorisation.md), [TypeScript](ts/14-authorisation.md). Read only the one for the language you are writing.

## Corrections

<!-- Add a dated line each time an agent gets this pattern wrong. -->
