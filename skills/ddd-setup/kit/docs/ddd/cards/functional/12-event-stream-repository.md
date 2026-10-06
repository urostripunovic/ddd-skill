# Event stream repository

**Use when:** an aggregate is event-sourced with a [decider](11-decider.md) and its events must be stored and loaded.

**Never:** update or delete a stored event. Never check the version in application code and then insert; two requests can pass that check at the same time.

## Rules

- Each aggregate instance has one stream: an append-only, ordered list of events. The version is the number of events in it.
- `load` returns the events and the version. `append` takes the version that was loaded, and fails with a conflict if the stream has moved on since.
- The store enforces the version check itself, with a uniqueness constraint on stream and version. This is optimistic concurrency: nothing is locked, and a clash is detected at the moment of saving.

  ```sql
  CREATE TABLE events (
    stream_id text  NOT NULL,
    version   int   NOT NULL,
    type      text  NOT NULL,
    data      jsonb NOT NULL,
    PRIMARY KEY (stream_id, version)
  );
  ```

- On a conflict, load again and decide again against the new state. Never re-append the events from the first decision: they were decided on a state that no longer exists.
- Retries are bounded. After the last attempt the conflict is returned to the caller.
- All events from one decision are appended atomically, or none are.
- Loaded events are untrusted input and are parsed into event types. An unknown event type is an error, not something to skip. See [parse at the boundary](07-parse-at-the-boundary.md).
- Event types change over time; stored events do not. Old shapes are converted to the current shape while loading.
- Events are kept forever. Do not put secrets in them, and keep personal data that may have to be erased outside the stream, referenced by ID.
- State changes and event publication to other systems must not be two separate writes. Publish from the stored stream.

## Enforced by

- The database: the primary key on `(stream_id, version)` rejects the second writer.
- Go: `Handle` is the only code path that appends, and it always passes the loaded version.
- TypeScript: `append` returns a `Result`, so a conflict cannot be ignored without the compiler noticing.

## Anti-pattern

```ts
const current = await db.maxVersion(streamId);
if (current === loadedVersion) {
  await db.insert(streamId, current + 1, event); // another request can insert between the check and this line
}
```

## Example

One file per language: [Go](go/12-event-stream-repository.md), [TypeScript](ts/12-event-stream-repository.md). Read only the one for the language you are writing.

## Corrections

<!-- Add a dated line each time an agent gets this pattern wrong. -->
