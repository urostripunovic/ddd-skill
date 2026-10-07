# States as types: Go

The rules are in [the card](../03-states-as-types.md).

```go
package ordering

import "time"

type OrderID struct{ v string }

func (id OrderID) String() string { return id.v }

type CancellationReason struct{ v string }

func (r CancellationReason) String() string { return r.v }

//sumtype:decl
type Order interface{ isOrder() }

type DraftOrder struct {
	id OrderID
}

type PlacedOrder struct {
	id       OrderID
	placedAt time.Time
}

type CancelledOrder struct {
	id     OrderID
	reason CancellationReason
}

func (o PlacedOrder) ID() OrderID                   { return o.id }
func (o PlacedOrder) PlacedAt() time.Time           { return o.placedAt }
func (o CancelledOrder) ID() OrderID                { return o.id }
func (o CancelledOrder) Reason() CancellationReason { return o.reason }

func (DraftOrder) isOrder()     {}
func (PlacedOrder) isOrder()    {}
func (CancelledOrder) isOrder() {}

// Narrower sum type for a command that is legal in more than one state.
// Go has no inline union, so the subset gets its own sealed interface.
//
//sumtype:decl
type CancellableOrder interface {
	Order
	isCancellable()
}

func (DraftOrder) isCancellable()  {}
func (PlacedOrder) isCancellable() {}

func Cancel(o CancellableOrder, reason CancellationReason) CancelledOrder {
	switch o := o.(type) {
	case DraftOrder:
		return CancelledOrder{id: o.id, reason: reason}
	case PlacedOrder:
		return CancelledOrder{id: o.id, reason: reason}
	}
	panic("ordering: nil CancellableOrder")
}

func CanBeEdited(o Order) bool {
	switch o.(type) {
	case DraftOrder:
		return true
	case PlacedOrder, CancelledOrder:
		return false
	}
	// Only reachable with a nil Order, which the linter cannot rule out.
	panic("ordering: nil Order")
}
```
