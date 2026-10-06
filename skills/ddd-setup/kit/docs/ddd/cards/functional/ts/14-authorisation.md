# Authorisation: TypeScript

The rules are in [the card](../14-authorisation.md).

```ts
export type Result<T, E> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E };

export type CustomerId = string & { readonly __brand: "CustomerId" };
export type OrderId = string & { readonly __brand: "OrderId" };

// What a verified credential says about its bearer.
export type Claims = { readonly subject: CustomerId; readonly support: boolean };

// Implemented by the adapter that holds the request. It returns claims only
// for a credential it has checked: a signature, a session lookup.
export type VerifyCredential = () => Promise<Result<Claims, "not-authenticated">>;

type Authenticated = { readonly __brand: "Actor" };

export type Actor =
  | ({ readonly kind: "customer"; readonly id: CustomerId } & Authenticated)
  | ({ readonly kind: "support-agent" } & Authenticated);

export async function authenticate(verify: VerifyCredential): Promise<Result<Actor, "not-authenticated">> {
  const claims = await verify();
  if (!claims.ok) return claims;
  const unbranded = claims.value.support
    ? { kind: "support-agent" }
    : { kind: "customer", id: claims.value.subject };
  // eslint-disable-next-line @typescript-eslint/consistent-type-assertions -- the brand is applied only here, after the credential was verified
  return { ok: true, value: unbranded as Actor };
}

export type DraftOrder = {
  readonly kind: "draft";
  readonly id: OrderId;
  readonly owner: CustomerId;
};

// The model's "Issued by" rule for CancelOrder.
export function mayCancel(actor: Actor, order: DraftOrder): boolean {
  switch (actor.kind) {
    case "customer":
      return actor.id === order.owner;
    case "support-agent":
      return true;
  }
}

export type CancelOrderDeps = {
  readonly loadDraft: (id: OrderId) => Promise<DraftOrder | undefined>;
  readonly saveCancelled: (id: OrderId) => Promise<void>;
};

export type CancelOrderError = "order-not-found" | "not-allowed";

export async function cancelOrder(
  deps: CancelOrderDeps,
  actor: Actor,
  id: OrderId,
): Promise<Result<OrderId, CancelOrderError>> {
  const draft = await deps.loadDraft(id);
  if (draft === undefined) return { ok: false, error: "order-not-found" };
  // After loading, because the rule depends on the owner; before any decision or write.
  if (!mayCancel(actor, draft)) return { ok: false, error: "not-allowed" };

  await deps.saveCancelled(draft.id);
  return { ok: true, value: draft.id };
}
```
