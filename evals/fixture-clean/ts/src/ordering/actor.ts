import type { Order } from "./order.ts";
import { sameCustomer, type CustomerEmail } from "./primitives.ts";
import type { Result } from "./result.ts";

// What a verified credential says about its bearer.
export type Claims = { readonly customer: CustomerEmail };

// Implemented by the adapter that holds the request. It returns claims only
// for a credential it has checked.
export type VerifyCredential = () => Promise<Result<Claims, "not-authenticated">>;

// The model has one kind of actor. A second kind makes this a union, and the two
// functions below then switch on `kind` so that neither can forget the new one.
export type Actor = {
  readonly __brand: "Actor";
  readonly kind: "customer";
  readonly email: CustomerEmail;
};

export async function authenticate(verify: VerifyCredential): Promise<Result<Actor, "not-authenticated">> {
  const claims = await verify();
  if (!claims.ok) return claims;
  const unbranded = { kind: "customer", email: claims.value.customer };
  // eslint-disable-next-line @typescript-eslint/consistent-type-assertions -- the brand is applied only here, after the credential was verified
  return { ok: true, value: unbranded as Actor };
}

// "Any signed-in customer": the new order belongs to whoever starts it.
export function ownerOfNewOrder(actor: Actor): CustomerEmail {
  return actor.email;
}

// The model gives AddItem, PlaceOrder and CancelOrder the same rule: the customer who owns the order.
export function mayChangeOrder(actor: Actor, order: Order): boolean {
  return sameCustomer(actor.email, order.customer);
}
