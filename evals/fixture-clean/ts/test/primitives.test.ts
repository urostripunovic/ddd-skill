import assert from "node:assert/strict";
import { test } from "node:test";
import { inspect } from "node:util";
import {
  parseCancellationReason,
  parseCustomerEmail,
  parseOrderId,
  parsePrice,
  parseQuantity,
  parseSku,
  parseTimestamp,
  sameCustomer,
} from "../src/ordering/primitives.ts";
import type { Result } from "../src/ordering/result.ts";
import { must } from "./support.ts";

type Case<T> = readonly [name: string, input: T, valid: boolean];

function check<T>(parse: (raw: T) => Result<unknown, string>, error: string, cases: readonly Case<T>[]): void {
  for (const [name, input, valid] of cases) {
    const result = parse(input);
    assert.equal(result.ok, valid, name);
    if (!result.ok) assert.equal(result.error, error, name);
  }
}

// Example 6 of the model: 1 and 1000 are accepted; 0 and 1001 are not a Quantity.
await test("Quantity: 1..1000, whole numbers only", () => {
  check(parseQuantity, "invalid-quantity", [
    ["below", 0, false],
    ["lowest", 1, true],
    ["highest", 1000, true],
    ["above", 1001, false],
    ["negative", -1, false],
    ["fraction", 1.5, false],
    ["NaN", Number.NaN, false],
    ["infinity", Number.POSITIVE_INFINITY, false],
    ["huge", 2 ** 40, false],
  ]);
  assert.equal(must(parseQuantity(1000)), 1000);
});

await test("Price: 0..100000000 minor units, never a fraction", () => {
  check(parsePrice, "invalid-price", [
    ["below", -1, false],
    ["lowest", 0, true],
    ["highest", 100_000_000, true],
    ["above", 100_000_001, false],
    ["fraction of a minor unit", 9.99, false],
    ["NaN", Number.NaN, false],
  ]);
});

await test("Sku: 3..32 characters, only A-Z, 0-9 and hyphen", () => {
  check(parseSku, "invalid-sku", [
    ["shortest", "AB1", true],
    ["longest", "A".repeat(32), true],
    ["with hyphen", "ABC-1", true],
    ["too short", "AB", false],
    ["too long", "A".repeat(33), false],
    ["empty", "", false],
    ["lower case is not repaired", "abc-1", false],
    ["surrounding space is not trimmed", " ABC-1 ", false],
    ["trailing newline", "ABC-1\n", false],
    ["query fragment", "ABC&key=1", false],
    ["markup", "<b>ABC</b>", false],
    ["non-ASCII letter", "ÅBC-1", false],
    ["far too large", "A".repeat(1 << 20), false],
  ]);
});

await test("OrderId: a UUID of exactly 36 characters", () => {
  check(parseOrderId, "invalid-order-id", [
    ["valid", "123e4567-e89b-12d3-a456-426614174000", true],
    ["one short", "123e4567-e89b-12d3-a456-42661417400", false],
    ["one long", "123e4567-e89b-12d3-a456-4266141740000", false],
    ["right length, wrong shape", "123e4567xe89bx12d3xa456x426614174000", false],
    ["upper case is not repaired", "123E4567-E89B-12D3-A456-426614174000", false],
    ["empty", "", false],
    ["far too large", "a".repeat(1 << 20), false],
  ]);
});

await test("CustomerEmail: at most 254 characters, one @", () => {
  check(parseCustomerEmail, "invalid-customer-email", [
    ["valid", "a@example.com", true],
    ["longest", `${"a".repeat(242)}@example.com`, true],
    ["one too long", `${"a".repeat(243)}@example.com`, false],
    ["no @", "a.example.com", false],
    ["two @", "a@b@example.com", false],
    ["empty", "", false],
    ["far too large", `${"a".repeat(1 << 20)}@example.com`, false],
  ]);
});

await test("CustomerEmail never prints or serialises its address", () => {
  const address = "secret.person@example.com";
  const customer = must(parseCustomerEmail(address));
  // inspect is what console.log uses.
  const printed = [String(customer), customer.toString(), inspect(customer), JSON.stringify(customer), JSON.stringify({ customer })];
  for (const text of printed) {
    assert.ok(!text.includes("secret.person"), text);
  }
  // No property holds the address, so nothing that walks the object can find it.
  assert.deepEqual(
    Object.values(customer).filter((value) => typeof value === "string"),
    ["CustomerEmail"],
  );
  assert.equal(customer.reveal(), address);
});

await test("CustomerEmail is compared by address", () => {
  assert.ok(sameCustomer(must(parseCustomerEmail("a@example.com")), must(parseCustomerEmail("a@example.com"))));
  assert.ok(!sameCustomer(must(parseCustomerEmail("a@example.com")), must(parseCustomerEmail("b@example.com"))));
});

await test("CancellationReason: 1..200 characters", () => {
  check(parseCancellationReason, "invalid-cancellation-reason", [
    ["shortest", "x", true],
    ["longest", "x".repeat(200), true],
    ["one too long", "x".repeat(201), false],
    ["empty", "", false],
    ["200 characters that are two code units each", "😀".repeat(200), true],
    ["201 of them", "😀".repeat(201), false],
    ["half a surrogate pair", "\ud83d", false],
    ["far too large", "x".repeat(1 << 20), false],
  ]);
});

await test("Timestamp: whole milliseconds a Date can hold", () => {
  check(parseTimestamp, "invalid-timestamp", [
    ["the epoch", 0, true],
    ["highest", 8_640_000_000_000_000, true],
    ["above", 8_640_000_000_000_001, false],
    ["before the epoch", -1, false],
    ["fraction", 0.5, false],
    ["NaN", Number.NaN, false],
  ]);
});
