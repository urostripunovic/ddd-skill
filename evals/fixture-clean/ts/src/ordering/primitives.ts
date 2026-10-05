import type { Result } from "./result.ts";

// No error here carries the rejected input: it is untrusted, and may be large or sensitive.

export type OrderId = string & { readonly __brand: "OrderId" };

const ORDER_ID_LENGTH = 36;
const ORDER_ID_SHAPE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;

export function parseOrderId(raw: string): Result<OrderId, "invalid-order-id"> {
  // Length first, so the regular expression never runs on oversized input.
  if (raw.length !== ORDER_ID_LENGTH) return { ok: false, error: "invalid-order-id" };
  if (!ORDER_ID_SHAPE.test(raw)) return { ok: false, error: "invalid-order-id" };
  // eslint-disable-next-line @typescript-eslint/consistent-type-assertions -- the brand is applied only here, after validation
  return { ok: true, value: raw as OrderId };
}

export type Sku = string & { readonly __brand: "Sku" };

const MIN_SKU_LENGTH = 3;
const MAX_SKU_LENGTH = 32;
const SKU_SHAPE = /^[A-Z0-9-]+$/;

export function parseSku(raw: string): Result<Sku, "invalid-sku"> {
  if (raw.length < MIN_SKU_LENGTH || raw.length > MAX_SKU_LENGTH) return { ok: false, error: "invalid-sku" };
  if (!SKU_SHAPE.test(raw)) return { ok: false, error: "invalid-sku" };
  // eslint-disable-next-line @typescript-eslint/consistent-type-assertions -- the brand is applied only here, after validation
  return { ok: true, value: raw as Sku };
}

export type Quantity = number & { readonly __brand: "Quantity" };

const MIN_QUANTITY = 1;
const MAX_QUANTITY = 1000;

export function parseQuantity(raw: number): Result<Quantity, "invalid-quantity"> {
  if (!Number.isInteger(raw) || raw < MIN_QUANTITY || raw > MAX_QUANTITY) {
    return { ok: false, error: "invalid-quantity" };
  }
  // eslint-disable-next-line @typescript-eslint/consistent-type-assertions -- the brand is applied only here, after validation
  return { ok: true, value: raw as Quantity };
}

// Minor units. Zero is a valid price: nothing to pay.
export type Price = number & { readonly __brand: "Price" };

const MAX_PRICE_MINOR = 100_000_000;

export function parsePrice(minor: number): Result<Price, "invalid-price"> {
  // isInteger also rejects NaN and the infinities, so a fraction of a minor unit cannot get in.
  if (!Number.isInteger(minor) || minor < 0 || minor > MAX_PRICE_MINOR) {
    return { ok: false, error: "invalid-price" };
  }
  // eslint-disable-next-line @typescript-eslint/consistent-type-assertions -- the brand is applied only here, after validation
  return { ok: true, value: minor as Price };
}

// Sensitive in the model. A branded string would be printed by any log line or
// JSON.stringify that reached it, so the address is held in a closure and every
// way of printing or serialising the value gives a placeholder.
export type CustomerEmail = {
  readonly __brand: "CustomerEmail";
  // For the adapter that has to send or store the address. Nothing else calls it.
  readonly reveal: () => string;
  readonly toString: () => string;
  readonly toJSON: () => string;
};

const MAX_CUSTOMER_EMAIL_LENGTH = 254;
const EMAIL_PLACEHOLDER = "[customer email]";

export function parseCustomerEmail(raw: string): Result<CustomerEmail, "invalid-customer-email"> {
  if (raw.length === 0 || raw.length > MAX_CUSTOMER_EMAIL_LENGTH) {
    return { ok: false, error: "invalid-customer-email" };
  }
  if (raw.split("@").length !== 2) return { ok: false, error: "invalid-customer-email" };
  return {
    ok: true,
    value: Object.freeze({
      __brand: "CustomerEmail",
      reveal: () => raw,
      toString: () => EMAIL_PLACEHOLDER,
      toJSON: () => EMAIL_PLACEHOLDER,
    }),
  };
}

// Two parsed addresses are different objects, so === would compare identity.
export function sameCustomer(a: CustomerEmail, b: CustomerEmail): boolean {
  return a.reveal() === b.reveal();
}

export type CancellationReason = string & { readonly __brand: "CancellationReason" };

const MAX_CANCELLATION_REASON_LENGTH = 200;
// With the u flag a surrogate pair is one character, so this matches only half of a pair on its own.
const LONE_SURROGATE = /\p{Surrogate}/u;

export function parseCancellationReason(raw: string): Result<CancellationReason, "invalid-cancellation-reason"> {
  // Code units before characters: a character is at most two code units, so a
  // string longer than this cannot be short enough, and is never iterated.
  if (raw.length === 0 || raw.length > MAX_CANCELLATION_REASON_LENGTH * 2) {
    return { ok: false, error: "invalid-cancellation-reason" };
  }
  if (LONE_SURROGATE.test(raw) || Array.from(raw).length > MAX_CANCELLATION_REASON_LENGTH) {
    return { ok: false, error: "invalid-cancellation-reason" };
  }
  // eslint-disable-next-line @typescript-eslint/consistent-type-assertions -- the brand is applied only here, after validation
  return { ok: true, value: raw as CancellationReason };
}

// The model's built-in Timestamp, as milliseconds since the epoch. A Date can be
// changed by whoever holds it (setTime), so no state or event carries one.
export type Timestamp = number & { readonly __brand: "Timestamp" };

// The range a Date can represent.
const MAX_TIMESTAMP = 8_640_000_000_000_000;

export function parseTimestamp(epochMillis: number): Result<Timestamp, "invalid-timestamp"> {
  if (!Number.isInteger(epochMillis) || epochMillis < 0 || epochMillis > MAX_TIMESTAMP) {
    return { ok: false, error: "invalid-timestamp" };
  }
  // eslint-disable-next-line @typescript-eslint/consistent-type-assertions -- the brand is applied only here, after validation
  return { ok: true, value: epochMillis as Timestamp };
}
