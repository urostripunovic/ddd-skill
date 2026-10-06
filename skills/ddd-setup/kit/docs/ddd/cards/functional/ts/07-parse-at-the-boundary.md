# Parse at the boundary: TypeScript

The rules are in [the card](../07-parse-at-the-boundary.md).

Check as: boundary

```ts
export type Result<T, E> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E };

export type Email = string & { readonly __brand: "Email" };

const MAX_EMAIL_LENGTH = 254;
const EMAIL_SHAPE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export type EmailError = "not-a-string" | "too-long" | "malformed";

export function parseEmail(raw: unknown): Result<Email, EmailError> {
  if (typeof raw !== "string") return { ok: false, error: "not-a-string" };
  // Length is checked before the regex so oversized input never reaches the costlier check.
  if (raw.length > MAX_EMAIL_LENGTH) return { ok: false, error: "too-long" };
  if (!EMAIL_SHAPE.test(raw)) return { ok: false, error: "malformed" };
  // eslint-disable-next-line @typescript-eslint/consistent-type-assertions -- the brand is applied only here, after validation
  return { ok: true, value: raw as Email };
}

export type RegisterCustomer = { readonly email: Email };

export type RegisterError = "not-an-object" | "unknown-field" | EmailError;

function isRecord(x: unknown): x is Record<string, unknown> {
  return typeof x === "object" && x !== null && !Array.isArray(x);
}

export function parseRegisterCustomer(body: unknown): Result<RegisterCustomer, RegisterError> {
  if (!isRecord(body)) return { ok: false, error: "not-an-object" };
  if (Object.keys(body).some((key) => key !== "email")) {
    return { ok: false, error: "unknown-field" };
  }
  const email = parseEmail(body["email"]);
  if (!email.ok) return email;
  return { ok: true, value: { email: email.value } };
}
```
