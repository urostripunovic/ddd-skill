package ordering

import (
	"slices"
	"time"
)

type Item struct {
	sku       SKU
	quantity  Quantity
	unitPrice Price
}

func (i Item) SKU() SKU           { return i.sku }
func (i Item) Quantity() Quantity { return i.quantity }
func (i Item) UnitPrice() Price   { return i.unitPrice }

//sumtype:decl
type Order interface {
	isOrder()
	ID() OrderID
	Customer() CustomerEmail
}

type DraftOrder struct {
	id       OrderID
	customer CustomerEmail
	items    []Item
}

type PlacedOrder struct {
	id       OrderID
	customer CustomerEmail
	items    []Item
	placedAt time.Time
}

type CancelledOrder struct {
	id       OrderID
	customer CustomerEmail
	reason   CancellationReason
}

func (DraftOrder) isOrder()     {}
func (PlacedOrder) isOrder()    {}
func (CancelledOrder) isOrder() {}

func (o DraftOrder) ID() OrderID             { return o.id }
func (o DraftOrder) Customer() CustomerEmail { return o.customer }
func (o DraftOrder) Items() []Item           { return slices.Clone(o.items) }

func (o PlacedOrder) ID() OrderID             { return o.id }
func (o PlacedOrder) Customer() CustomerEmail { return o.customer }
func (o PlacedOrder) Items() []Item           { return slices.Clone(o.items) }
func (o PlacedOrder) PlacedAt() time.Time     { return o.placedAt }

func (o CancelledOrder) ID() OrderID                { return o.id }
func (o CancelledOrder) Customer() CustomerEmail    { return o.customer }
func (o CancelledOrder) Reason() CancellationReason { return o.reason }

// fmt prints unexported fields by reflection and does not call their String methods,
// so without these a "%+v" of an order would print the customer's address.
func (o DraftOrder) String() string       { return "DraftOrder " + o.id.String() }
func (o DraftOrder) GoString() string     { return o.String() }
func (o PlacedOrder) String() string      { return "PlacedOrder " + o.id.String() }
func (o PlacedOrder) GoString() string    { return o.String() }
func (o CancelledOrder) String() string   { return "CancelledOrder " + o.id.String() }
func (o CancelledOrder) GoString() string { return o.String() }

// The states CancelOrder is legal in. Go has no inline union, so the subset gets its own sealed interface.
//
//sumtype:decl
type CancellableOrder interface {
	Order
	isCancellable()
}

func (DraftOrder) isCancellable()  {}
func (PlacedOrder) isCancellable() {}

//sumtype:decl
type Event interface{ isEvent() }

type OrderPlaced struct {
	OrderID OrderID
	At      time.Time
}

type OrderCancelled struct {
	OrderID OrderID
	Reason  CancellationReason
	At      time.Time
}

func (OrderPlaced) isEvent()    {}
func (OrderCancelled) isEvent() {}

// A fact from the Pricing service: what one product cost, and when that was said.
type PriceQuote struct {
	sku       SKU
	unitPrice Price
	quotedAt  time.Time
}

func NewPriceQuote(sku SKU, unitPrice Price, quotedAt time.Time) PriceQuote {
	return PriceQuote{sku: sku, unitPrice: unitPrice, quotedAt: quotedAt}
}

func (q PriceQuote) SKU() SKU { return q.sku }

// The narrowing switches live here and not in the workflow package, because
// gochecksumtype under golangci-lint only checks switches in the package that
// declares the sum type. A new state must fail the lint at these two places.
func AsDraft(o Order) (DraftOrder, bool) {
	switch o := o.(type) {
	case DraftOrder:
		return o, true
	case PlacedOrder, CancelledOrder:
		return DraftOrder{}, false
	}
	return DraftOrder{}, false
}

func AsCancellable(o Order) (CancellableOrder, bool) {
	switch o := o.(type) {
	case DraftOrder:
		return o, true
	case PlacedOrder:
		return o, true
	case CancelledOrder:
		return nil, false
	}
	return nil, false
}
