# Anti-corruption layer: TypeScript

The rules are in [the card](../09-anti-corruption-layer.md).

Check as: boundary

```ts
export type Result<T, E> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E };

export type Authorized = { readonly kind: "authorized"; readonly amountMinor: bigint };
export type Declined = { readonly kind: "declined"; readonly reason: string };
export type Payment = Authorized | Declined;

function isRecord(x: unknown): x is Record<string, unknown> {
  return typeof x === "object" && x !== null && !Array.isArray(x);
}

export function toPayment(charge: unknown): Result<Payment, "malformed-charge" | "unknown-status"> {
  if (!isRecord(charge)) return { ok: false, error: "malformed-charge" };
  const status = charge["status"];
  const amount = charge["amount"];
  const failureCode = charge["failure_code"];

  switch (status) {
    case "authorized":
    case "captured":
      if (typeof amount !== "number" || !Number.isSafeInteger(amount)) {
        return { ok: false, error: "malformed-charge" };
      }
      return { ok: true, value: { kind: "authorized", amountMinor: BigInt(amount) } };
    case "declined":
    case "failed":
      if (typeof failureCode !== "string") return { ok: false, error: "malformed-charge" };
      return { ok: true, value: { kind: "declined", reason: failureCode } };
    default:
      // A status added by the provider must fail loudly, not be treated as a known state.
      return { ok: false, error: "unknown-status" };
  }
}
```
