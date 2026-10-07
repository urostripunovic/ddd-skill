# Decider

**Use when:** the aggregate is event-sourced, or you want every command of an aggregate behind one uniform entry point with tests that read "given these events, when this command, then these events".

**Never:** put a business rule in `evolve`, or I/O in either function. If the state is stored in a table and not rebuilt from events, use [aggregate as decision functions](04-aggregate-as-decision-functions.md) alone.

## Rules

- Three parts: `decide(command, state)` returns events, `evolve(state, event)` returns the next state, and `initialState` is where every aggregate starts.
- `decide` holds all the rules and may reject. `evolve` holds none and never rejects a valid history: the event already happened.
- Both are pure. Time and generated IDs arrive inside the command.
- `decide` accepts every state, so a wrong state is a runtime failure here and not a compile error. Keep that cost small: `decide` only narrows the state and dispatches, and the rules live in per-state functions that take the specific state type.
- A business failure is returned as an error ([errors as values](10-errors-as-values.md)). It becomes an event only if the model says the rejection itself must be recorded.
- An event that does not fit the current state in `evolve` means the stored history is corrupt. That is a bug, reported as one, not a business failure.
- Current state is `events` folded through `evolve` from `initialState`. Nothing else may produce a state.
- Storing and loading the events, and what happens when two commands race, is covered by [event stream repository](12-event-stream-repository.md).

## Enforced by

- Go: `//sumtype:decl` on the state, command and event interfaces, so `Decide` and `Evolve` must handle every variant.
- TypeScript: discriminated unions with `assertNever` in both functions.
- Both: the per-state function's parameter type. `place` cannot be handed anything but a draft.
- Go: state fields are unexported, so a state with contents can only come from `Evolve`.

## Anti-pattern

```ts
function evolve(state: Order, event: OrderEvent): Order {
  if (event.type === "order-placed" && state.itemCount === 0) {
    return state; // a rule in evolve: the event is silently dropped and history no longer matches state
  }
  // ...
}
```

Examples: [Go](go/11-decider.md) · [TypeScript](ts/11-decider.md). Read only the one for your language.

## Corrections

<!-- Add a dated line each time an agent gets this pattern wrong. -->
