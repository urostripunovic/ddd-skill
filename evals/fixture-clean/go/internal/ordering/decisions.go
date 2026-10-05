package ordering

import (
	"errors"
	"slices"
	"time"
)

var (
	ErrEmptyOrder   = errors.New("order has no items")
	ErrQuoteExpired = errors.New("price quote is too old")
	ErrTooManyItems = errors.New("order has too many items")
)

const (
	maxItems    = 100
	maxQuoteAge = 5 * time.Minute
)

func StartOrder(id OrderID, customer CustomerEmail) DraftOrder {
	return DraftOrder{id: id, customer: customer}
}

// The item's product and price both come from the quote, so they cannot disagree.
func AddItem(o DraftOrder, quantity Quantity, quote PriceQuote, now time.Time) (DraftOrder, error) {
	if now.Sub(quote.quotedAt) > maxQuoteAge {
		return DraftOrder{}, ErrQuoteExpired
	}
	if len(o.items) >= maxItems {
		return DraftOrder{}, ErrTooManyItems
	}
	// Cloned so the returned draft does not share a backing array with the one passed in.
	items := append(slices.Clone(o.items), Item{sku: quote.sku, quantity: quantity, unitPrice: quote.unitPrice})
	return DraftOrder{id: o.id, customer: o.customer, items: items}, nil
}

func PlaceOrder(o DraftOrder, now time.Time) (PlacedOrder, []Event, error) {
	if len(o.items) == 0 {
		return PlacedOrder{}, nil, ErrEmptyOrder
	}
	placed := PlacedOrder{id: o.id, customer: o.customer, items: slices.Clone(o.items), placedAt: now}
	return placed, []Event{OrderPlaced{OrderID: o.id, At: now}}, nil
}

func CancelOrder(o CancellableOrder, reason CancellationReason, now time.Time) (CancelledOrder, []Event) {
	switch o.(type) {
	case DraftOrder, PlacedOrder:
		cancelled := CancelledOrder{id: o.ID(), customer: o.Customer(), reason: reason}
		return cancelled, []Event{OrderCancelled{OrderID: o.ID(), Reason: reason, At: now}}
	}
	// Only reachable with a nil CancellableOrder, which the linter cannot rule out.
	panic("ordering: nil CancellableOrder")
}
