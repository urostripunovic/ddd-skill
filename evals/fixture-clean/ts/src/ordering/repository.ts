import type { DraftOrder, Order, OrderEvent } from "./order.ts";
import type { OrderId } from "./primitives.ts";
import type { Result } from "./result.ts";

// How many times an order has been saved. Only this file makes one, so the
// number a save is checked against is always one that a load handed out.
export type Version = number & { readonly __brand: "Version" };

// eslint-disable-next-line @typescript-eslint/consistent-type-assertions -- the brand is applied only in this file
export const FIRST_VERSION = 1 as Version;

export function nextVersion(version: Version): Version {
  // eslint-disable-next-line @typescript-eslint/consistent-type-assertions -- the brand is applied only in this file
  return (version + 1) as Version;
}

export type Loaded = { readonly order: Order; readonly version: Version };

// Declared here so the domain owns the contract. The implementation lives outside the domain.
export type Orders = {
  readonly create: (order: DraftOrder) => Promise<void>;
  readonly load: (id: OrderId) => Promise<Result<Loaded, "order-not-found">>;
  // Stores the state and its events in one transaction. "conflict" means the stored
  // version is no longer the one that was loaded.
  readonly save: (order: Order, events: readonly OrderEvent[], loaded: Version) => Promise<Result<undefined, "conflict">>;
};
