# Workflow as function

**Use when:** implementing a use case: load state, make a decision, persist, publish.

**Never:** put business rules in the workflow. It orchestrates; the decision function decides. See [aggregate as decision functions](04-aggregate-as-decision-functions.md).

## Rules

- One function per use case, named after the command in the ubiquitous language.
- Dependencies (load, save, publish, clock) are passed in explicitly. No globals, no singletons, no DI container.
- The shape is always: load, narrow, decide, persist, publish. All I/O is at the edges; the decision in the middle is pure.
- A repository returns the whole sum type. The workflow narrows it to the state the command needs, and returns a named "wrong state" failure otherwise. The decision function never sees a wrong state.
- Saving state and publishing events must be atomic. Use a transactional outbox or save both in one transaction; this function does not solve that by itself.
- Go: when the workflow is in another package than the aggregate, the narrowing switch stays in the aggregate's package and the workflow calls it. The exhaustiveness lint does not reach a switch in another package ([states as types](03-states-as-types.md)).

## Enforced by

- Both: the decision function has no access to the dependencies, so it cannot do I/O.
- Go: plain `(T, error)` returns. No Result types or pipeline combinators; they are not idiomatic Go.
- TypeScript: `Result` returned, never thrown, so the caller must handle every error kind.

## Anti-pattern

```ts
class OrderService {
  async place(id: string) {
    const o = await db.orders.find(id);
    if (o.items.length === 0) throw new Error("empty"); // rule buried in orchestration
    o.status = "placed";
    await db.orders.save(o);
  }
}
```

Examples: [Go](go/06-workflow-as-function.md) · [TypeScript](ts/06-workflow-as-function.md). Read only the one for your language.

## Corrections

<!-- Add a dated line each time an agent gets this pattern wrong. -->
