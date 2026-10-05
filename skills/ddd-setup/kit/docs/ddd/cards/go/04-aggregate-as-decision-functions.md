# Aggregate as data plus decision functions: Go

The rules are in [the card](../04-aggregate-as-decision-functions.md).

```go
package ordering

import (
	"errors"
	"slices"
	"time"
)

var ErrEmptyOrder = errors.New("order has no items")

type OrderID struct{ v string }
type SKU struct{ v string }
type Quantity struct{ v int }

func (id OrderID) String() string { return id.v }
func (s SKU) String() string      { return s.v }
func (q Quantity) Int() int       { return q.v }

type Item struct {
	sku SKU
	qty Quantity
}

type DraftOrder struct {
	id    OrderID
	items []Item
}

type PlacedOrder struct {
	id       OrderID
	items    []Item
	placedAt time.Time
}

func (o PlacedOrder) ID() OrderID         { return o.id }
func (o PlacedOrder) Items() []Item       { return slices.Clone(o.items) }
func (o PlacedOrder) PlacedAt() time.Time { return o.placedAt }
func (l Item) SKU() SKU                   { return l.sku }
func (l Item) Quantity() Quantity         { return l.qty }

//sumtype:decl
type Event interface{ isEvent() }

type OrderPlaced struct {
	OrderID OrderID
	At      time.Time
}

func (OrderPlaced) isEvent() {}

// now is a parameter so the decision stays pure and can be tested without a clock.
func Place(o DraftOrder, now time.Time) (PlacedOrder, []Event, error) {
	if len(o.items) == 0 {
		return PlacedOrder{}, nil, ErrEmptyOrder
	}
	// Cloned so later changes to the draft's backing array cannot alter the placed order.
	placed := PlacedOrder{id: o.id, items: slices.Clone(o.items), placedAt: now}
	return placed, []Event{OrderPlaced{OrderID: o.id, At: now}}, nil
}
```
