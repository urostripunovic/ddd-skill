# Decider: Go

The rules are in [the card](../11-decider.md).

```go
package ordering

import (
	"errors"
	"fmt"
	"time"
)

var (
	ErrOrderExists   = errors.New("order already exists")
	ErrOrderNotDraft = errors.New("order is not a draft")
	ErrEmptyOrder    = errors.New("order has no items")
)

type OrderID struct{ v string }

func (id OrderID) String() string { return id.v }

//sumtype:decl
type Order interface{ isOrder() }

type NoOrder struct{}

type DraftOrder struct {
	id        OrderID
	itemCount int
}

type PlacedOrder struct {
	id       OrderID
	placedAt time.Time
}

func (o PlacedOrder) ID() OrderID         { return o.id }
func (o PlacedOrder) PlacedAt() time.Time { return o.placedAt }

func (NoOrder) isOrder()     {}
func (DraftOrder) isOrder()  {}
func (PlacedOrder) isOrder() {}

//sumtype:decl
type Command interface{ isCommand() }

type CreateOrder struct{ ID OrderID }
type AddItem struct{}
type PlaceOrder struct{ At time.Time }

func (CreateOrder) isCommand() {}
func (AddItem) isCommand()     {}
func (PlaceOrder) isCommand()  {}

//sumtype:decl
type Event interface{ isEvent() }

type OrderCreated struct{ OrderID OrderID }
type ItemAdded struct{}
type OrderPlaced struct{ At time.Time }

func (OrderCreated) isEvent() {}
func (ItemAdded) isEvent()    {}
func (OrderPlaced) isEvent()  {}

func InitialState() Order { return NoOrder{} }

func Decide(cmd Command, state Order) ([]Event, error) {
	switch c := cmd.(type) {
	case CreateOrder:
		if _, ok := state.(NoOrder); !ok {
			return nil, ErrOrderExists
		}
		return []Event{OrderCreated{OrderID: c.ID}}, nil
	case AddItem:
		if _, ok := state.(DraftOrder); !ok {
			return nil, ErrOrderNotDraft
		}
		return []Event{ItemAdded{}}, nil
	case PlaceOrder:
		draft, ok := state.(DraftOrder)
		if !ok {
			return nil, ErrOrderNotDraft
		}
		return place(draft, c.At)
	}
	return nil, errors.New("ordering: nil Command")
}

// The rule lives here, behind a parameter type that only a draft satisfies.
func place(o DraftOrder, at time.Time) ([]Event, error) {
	if o.itemCount == 0 {
		return nil, ErrEmptyOrder
	}
	return []Event{OrderPlaced{At: at}}, nil
}

// The error return is only for a history that does not fit together, which is a bug.
func Evolve(state Order, event Event) (Order, error) {
	switch e := event.(type) {
	case OrderCreated:
		return DraftOrder{id: e.OrderID}, nil
	case ItemAdded:
		draft, ok := state.(DraftOrder)
		if !ok {
			return nil, fmt.Errorf("ordering: corrupt history: %T after %T", e, state)
		}
		draft.itemCount++
		return draft, nil
	case OrderPlaced:
		draft, ok := state.(DraftOrder)
		if !ok {
			return nil, fmt.Errorf("ordering: corrupt history: %T after %T", e, state)
		}
		return PlacedOrder{id: draft.id, placedAt: e.At}, nil
	}
	return nil, errors.New("ordering: nil Event")
}

func Replay(events []Event) (Order, error) {
	state := InitialState()
	for _, e := range events {
		next, err := Evolve(state, e)
		if err != nil {
			return nil, err
		}
		state = next
	}
	return state, nil
}
```
