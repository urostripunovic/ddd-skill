# Facts from outside the aggregate: Go

The rules are in [the card](../13-facts-from-outside.md).

```go
package ordering

import (
	"context"
	"errors"
	"fmt"
	"slices"
	"time"
)

var (
	ErrQuoteMismatch = errors.New("price quote is for another product")
	ErrQuoteExpired  = errors.New("price quote is too old")
)

const maxQuoteAge = 5 * time.Minute

type SKU struct{ v string }

func (s SKU) String() string { return s.v }

type Quantity struct{ v int }

func (q Quantity) Int() int { return q.v }

type Price struct{ minor int64 }

func (p Price) Minor() int64 { return p.minor }

// A fact gathered by the workflow: what was learned, about what, and when.
type PriceQuote struct {
	sku      SKU
	unit     Price
	quotedAt time.Time
}

func NewPriceQuote(sku SKU, unit Price, quotedAt time.Time) PriceQuote {
	return PriceQuote{sku: sku, unit: unit, quotedAt: quotedAt}
}

type Item struct {
	sku SKU
	qty Quantity
	// Captured when the item is added, so a later price change does not alter this order.
	unit Price
}

func (l Item) SKU() SKU           { return l.sku }
func (l Item) Quantity() Quantity { return l.qty }
func (l Item) UnitPrice() Price   { return l.unit }

type DraftOrder struct{ items []Item }

func (o DraftOrder) Items() []Item { return slices.Clone(o.items) }

func AddItem(o DraftOrder, sku SKU, qty Quantity, quote PriceQuote, now time.Time) (DraftOrder, error) {
	if quote.sku != sku {
		return DraftOrder{}, ErrQuoteMismatch
	}
	if now.Sub(quote.quotedAt) > maxQuoteAge {
		return DraftOrder{}, ErrQuoteExpired
	}
	items := append(slices.Clone(o.items), Item{sku: sku, qty: qty, unit: quote.unit})
	return DraftOrder{items: items}, nil
}

type AddItemDeps struct {
	QuotePrice func(ctx context.Context, sku SKU) (PriceQuote, error)
	Now        func() time.Time
}

// The workflow gathers the fact, then hands it to the pure decision.
func AddItemToOrder(ctx context.Context, deps AddItemDeps, o DraftOrder, sku SKU, qty Quantity) (DraftOrder, error) {
	quote, err := deps.QuotePrice(ctx, sku)
	if err != nil {
		return DraftOrder{}, fmt.Errorf("quote price for %s: %w", sku, err)
	}
	return AddItem(o, sku, qty, quote, deps.Now())
}
```
