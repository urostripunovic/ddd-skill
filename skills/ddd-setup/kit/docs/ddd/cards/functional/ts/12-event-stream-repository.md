# Event stream repository: TypeScript

The rules are in [the card](../12-event-stream-repository.md).

Check as: boundary

```ts
export type Result<T, E> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E };

export type StreamId = string & { readonly __brand: "StreamId" };
export type Version = number & { readonly __brand: "Version" };

export type Decider<C, S, E, Err> = {
  readonly decide: (command: C, state: S) => Result<readonly E[], Err>;
  readonly evolve: (state: S, event: E) => S;
  readonly initialState: S;
};

export type Loaded<E> = { readonly events: readonly E[]; readonly version: Version };

// Declared with the domain so the domain owns the contract; the database
// implementation lives in infrastructure.
export type Streams<E> = {
  readonly load: (id: StreamId) => Promise<Loaded<E>>;
  readonly append: (
    id: StreamId,
    expected: Version,
    events: readonly E[],
  ) => Promise<Result<void, "conflict">>;
};

const MAX_ATTEMPTS = 3;

export async function handle<C, S, E, Err>(
  decider: Decider<C, S, E, Err>,
  streams: Streams<E>,
  id: StreamId,
  command: C,
): Promise<Result<readonly E[], Err | "conflict">> {
  for (let attempt = 0; attempt < MAX_ATTEMPTS; attempt++) {
    const { events, version } = await streams.load(id);

    let state = decider.initialState;
    for (const event of events) {
      state = decider.evolve(state, event);
    }

    const decision = decider.decide(command, state);
    if (!decision.ok) return decision;

    // A conflict falls through to the next attempt, which decides again from a fresh load.
    const appended = await streams.append(id, version, decision.value);
    if (appended.ok) return decision;
  }
  return { ok: false, error: "conflict" };
}
```
