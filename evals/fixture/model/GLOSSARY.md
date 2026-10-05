# Ordering

Takes, places and cancels customer orders. Payment, delivery and prices belong to other contexts.

## Language

**Order**:
A customer's request to buy one or more products.
_Avoid_: Purchase

**Draft order**:
An order the customer is still putting together. It may have no items.
_Avoid_: Cart, Basket

**Placed order**:
An order the customer has committed to. It has at least one item and a time of placing. Not a paid order, which belongs to Billing.
_Avoid_: Submitted order

**Cancelled order**:
An order that will not be fulfilled, with the reason given. Not a refund, which belongs to Billing.
_Avoid_: Voided order

**Item**:
One product in an order and the quantity wanted, with the unit price at the time it was added.
_Avoid_: Line, Row

**Price quote**:
What the Pricing service said one product costs, and when it said so.
_Avoid_: Price lookup
