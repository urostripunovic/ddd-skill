export type Sku = string & { readonly __brand: "Sku" };

export function parseSku(raw: string): Sku {
  const cleaned = raw.trim().toUpperCase();
  if (!/^[A-Z0-9-]{3,32}$/.test(cleaned)) {
    throw new Error(`bad sku: ${raw}`);
  }
  // eslint-disable-next-line @typescript-eslint/consistent-type-assertions -- the brand is applied only here, after validation
  return cleaned as Sku;
}

export type Item = {
  sku: Sku;
  quantity: number;
  unitPrice: number;
};

export type Order = {
  status: "draft" | "placed" | "cancelled";
  id: string;
  customerEmail: string;
  items: Item[];
  placedAt?: Date;
  cancelReason?: string;
};

export function addItem(order: Order, item: Item): Order {
  order.items.push(item);
  return order;
}

export function place(order: Order): Order {
  if (order.status !== "draft") {
    throw new Error("wrong state");
  }
  if (order.items.length === 0) {
    throw new Error("empty order");
  }
  order.status = "placed";
  order.placedAt = new Date();
  return order;
}

export function describe(order: Order): string {
  // eslint-disable-next-line @typescript-eslint/switch-exhaustiveness-check
  switch (order.status) {
    case "draft":
      return "Draft";
    default:
      return "Other";
  }
}
