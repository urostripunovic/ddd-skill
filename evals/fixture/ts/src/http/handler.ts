import { addItem, type Order, type Sku } from "../ordering/order.js";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function handleAddItem(order: Order, body: any): Order {
  // eslint-disable-next-line @typescript-eslint/consistent-type-assertions, @typescript-eslint/no-unsafe-member-access
  const sku = body.sku as Sku;
  // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
  const quantity = Number(body.quantity);
  // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
  const unitPrice = Number(body.unitPrice);
  console.log("adding item", body);
  return addItem(order, { sku, quantity, unitPrice });
}
