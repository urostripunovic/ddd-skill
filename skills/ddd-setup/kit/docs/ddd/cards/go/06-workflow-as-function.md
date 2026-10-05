# Workflow as function: Go

The rules are in [the card](../06-workflow-as-function.md).

Check as: boundary

```go
package ordering

import (
	"context"
	"errors"
	"fmt"
	"time"
)

var (
	ErrEmptyOrder    = errors.New("order has no items")
	ErrOrderNotDraft = errors.New("order is not a draft")
)

type OrderID struct{ v string }

func (id OrderID) String() string { return id.v }

type DraftOrder struct {
	id    OrderID
	items int
}
type PlacedOrder struct {
	id       OrderID
	placedAt time.Time
}

//sumtype:decl
type Order interface{ isOrder() }

func (DraftOrder) isOrder()  {}
func (PlacedOrder) isOrder() {}

func (o PlacedOrder) ID() OrderID         { return o.id }
func (o PlacedOrder) PlacedAt() time.Time { return o.placedAt }

//sumtype:decl
type Event interface{ isEvent() }
type OrderPlaced struct{ OrderID OrderID }

func (OrderPlaced) isEvent() {}

func Place(o DraftOrder, now time.Time) (PlacedOrder, []Event, error) {
	if o.items == 0 {
		return PlacedOrder{}, nil, ErrEmptyOrder
	}
	return PlacedOrder{id: o.id, placedAt: now}, []Event{OrderPlaced{OrderID: o.id}}, nil
}

func asDraft(o Order) (DraftOrder, error) {
	switch o := o.(type) {
	case DraftOrder:
		return o, nil
	case PlacedOrder:
		return DraftOrder{}, ErrOrderNotDraft
	}
	return DraftOrder{}, errors.New("ordering: nil Order")
}

type PlaceOrderDeps struct {
	LoadOrder func(ctx context.Context, id OrderID) (Order, error)
	// Takes state and events together so the implementation can commit both in one transaction.
	SavePlaced func(ctx context.Context, o PlacedOrder, events []Event) error
	Now        func() time.Time
}

func PlaceOrder(ctx context.Context, deps PlaceOrderDeps, id OrderID) error {
	order, err := deps.LoadOrder(ctx, id)
	if err != nil {
		return fmt.Errorf("load order: %w", err)
	}
	draft, err := asDraft(order)
	if err != nil {
		return err
	}
	placed, events, err := Place(draft, deps.Now())
	if err != nil {
		return err
	}
	if err := deps.SavePlaced(ctx, placed, events); err != nil {
		return fmt.Errorf("save placed order: %w", err)
	}
	return nil
}
```
