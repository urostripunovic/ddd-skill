# Anticorruption layer: TypeScript

The rules are in [the card](../09-anticorruption-layer.md).

Check as: boundary

```ts
export type Result<T, E> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E };

// The domain's own types. In a real project they and their parsers live in the domain.
export type AmountMinor = bigint & { readonly __brand: "AmountMinor" };
export type DeclineReason = string & { readonly __brand: "DeclineReason" };

export type Authorized = { readonly kind: "authorized"; readonly amountMinor: AmountMinor };
export type Declined = { readonly kind: "declined"; readonly reason: DeclineReason };
export type Payment = Authorized | Declined;

// Example bounds, not payment rules: take the real ones from the model's Domain primitives table,
// and what happens when a value breaks them. Here a decline reason over the bound makes the charge
// malformed, which is an error, not a decline.
const MAX_DECLINE_REASON = 64;

export function parseAmountMinor(raw: number): Result<AmountMinor, "invalid-amount"> {
  if (!Number.isSafeInteger(raw) || raw < 0) return { ok: false, error: "invalid-amount" };
  // eslint-disable-next-line @typescript-eslint/consistent-type-assertions -- the brand is applied only here, after validation
  return { ok: true, value: BigInt(raw) as AmountMinor };
}

export function parseDeclineReason(raw: string): Result<DeclineReason, "invalid-decline-reason"> {
  if (raw.length === 0 || raw.length > MAX_DECLINE_REASON) return { ok: false, error: "invalid-decline-reason" };
  // eslint-disable-next-line @typescript-eslint/consistent-type-assertions -- the brand is applied only here, after validation
  return { ok: true, value: raw as DeclineReason };
}

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
    case "captured": {
      if (typeof amount !== "number") return { ok: false, error: "malformed-charge" };
      const amountMinor = parseAmountMinor(amount);
      if (!amountMinor.ok) return { ok: false, error: "malformed-charge" };
      return { ok: true, value: { kind: "authorized", amountMinor: amountMinor.value } };
    }
    case "declined":
    case "failed": {
      if (typeof failureCode !== "string") return { ok: false, error: "malformed-charge" };
      const reason = parseDeclineReason(failureCode);
      if (!reason.ok) return { ok: false, error: "malformed-charge" };
      return { ok: true, value: { kind: "declined", reason: reason.value } };
    }
    default:
      // A status added by the provider must fail loudly, not be treated as a known state.
      return { ok: false, error: "unknown-status" };
  }
}
```
