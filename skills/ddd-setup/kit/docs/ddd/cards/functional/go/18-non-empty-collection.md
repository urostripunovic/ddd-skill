# Non-empty collection: Go

The rules are in [the card](../18-non-empty-collection.md).

```go
package ordering

import (
	"errors"
	"slices"
)

var (
	ErrEmptyOrder   = errors.New("order has no items")
	ErrTooManyItems = errors.New("order has too many items")
)

const maxItems = 200

type SKU struct{ v string }

func (s SKU) String() string { return s.v }

type Item struct{ sku SKU }

func (l Item) SKU() SKU { return l.sku }

// The first item is its own field, so a Items built by NewItems always has one.
type Items struct {
	first Item
	rest  []Item
}

func NewItems(ls []Item) (Items, error) {
	if len(ls) == 0 {
		return Items{}, ErrEmptyOrder
	}
	if len(ls) > maxItems {
		return Items{}, ErrTooManyItems
	}
	return Items{first: ls[0], rest: slices.Clone(ls[1:])}, nil
}

func (l Items) First() Item  { return l.first }
func (l Items) All() []Item  { return append([]Item{l.first}, l.rest...) }
func (l Items) IsZero() bool { return l.first == Item{} && len(l.rest) == 0 }

type DraftOrder struct{ items []Item }

type PlacedOrder struct{ items Items }

func (o PlacedOrder) Items() Items { return o.items }

// The only place the rule is checked. After this, the type carries it.
func Place(o DraftOrder) (PlacedOrder, error) {
	items, err := NewItems(o.items)
	if err != nil {
		return PlacedOrder{}, err
	}
	return PlacedOrder{items: items}, nil
}
```
