# Read-once secret: TypeScript

The rules are in [the card](../17-read-once-secret.md).

```ts
export type Result<T, E> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E };

export type Secret = {
  readonly reveal: () => Result<string, "secret-already-read">;
  readonly toString: () => string;
  readonly toJSON: () => never;
};

const MAX_SECRET_LENGTH = 1024;

export function parseSecret(raw: string): Result<Secret, "invalid-secret"> {
  // The value is not included in the error: a rejected secret is still a secret.
  if (raw.length === 0 || raw.length > MAX_SECRET_LENGTH) return { ok: false, error: "invalid-secret" };

  // Held in the closure so no property of the object contains it.
  let value: string | undefined = raw;
  return {
    ok: true,
    value: Object.freeze({
      reveal: (): Result<string, "secret-already-read"> => {
        if (value === undefined) return { ok: false, error: "secret-already-read" };
        const revealed = value;
        value = undefined;
        return { ok: true, value: revealed };
      },
      toString: () => "[secret]",
      // Throwing is right here: serialising a secret is a bug, not a business outcome.
      toJSON: (): never => {
        // eslint-disable-next-line no-restricted-syntax -- serialising a secret is a programming error
        throw new Error("secret cannot be serialised");
      },
    }),
  };
}
```
