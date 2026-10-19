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
// A string brand ({ __brand: "Actor" }) can be typed out in an object literal anywhere,
// which forges an actor. Only this module can name an unexported symbol.
const actorBrand: unique symbol = Symbol("Actor");

export type Actor = {
  readonly kind: "customer";
  readonly email: CustomerEmail;
  readonly [actorBrand]: true;
};

export async function authenticate(verify: VerifyCredential): Promise<Result<Actor, "not-authenticated">> {
  const claims = await verify();
  if (!claims.ok) return claims;
  return { ok: true, value: { kind: "customer", email: claims.value.customer, [actorBrand]: true } };
}

// "Any signed-in customer": the new order belongs to whoever starts it.
export function ownerOfNewOrder(actor: Actor): CustomerEmail {
  return actor.email;
}

// The model gives AddItem, PlaceOrder and CancelOrder the same rule: the customer who owns the order.
export function mayChangeOrder(actor: Actor, order: Order): boolean {
  return sameCustomer(actor.email, order.customer);
}
