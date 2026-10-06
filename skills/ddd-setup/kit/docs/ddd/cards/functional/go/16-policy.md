# Policy: Go

The rules are in [the card](../16-policy.md).

```go
package stock

type EventID struct{ v string }

func (id EventID) String() string { return id.v }

type OrderID struct{ v string }

func (id OrderID) String() string { return id.v }

type CommandID struct{ v string }

func (id CommandID) String() string { return id.v }

// Derived, not generated, so a redelivered event yields the same command ID.
func commandIDFor(policy string, e EventID) CommandID {
	return CommandID{v: policy + ":" + e.v}
}

// Ordering's events as this context sees them, after its anti-corruption layer.
//
//sumtype:decl
type OrderEvent interface{ isOrderEvent() }

type OrderPlaced struct {
	EventID EventID
	OrderID OrderID
}

type OrderCancelled struct {
	EventID EventID
	OrderID OrderID
}

func (OrderPlaced) isOrderEvent()    {}
func (OrderCancelled) isOrderEvent() {}

//sumtype:decl
type Command interface{ isCommand() }

type ReserveStock struct {
	CommandID CommandID
	OrderID   OrderID
}

type ReleaseStock struct {
	CommandID CommandID
	OrderID   OrderID
}

func (ReserveStock) isCommand() {}
func (ReleaseStock) isCommand() {}

// "Whenever an order is placed, reserve its stock; whenever it is cancelled, release it."
func ReservationPolicy(e OrderEvent) []Command {
	const name = "reservation"
	switch e := e.(type) {
	case OrderPlaced:
		return []Command{ReserveStock{CommandID: commandIDFor(name, e.EventID), OrderID: e.OrderID}}
	case OrderCancelled:
		return []Command{ReleaseStock{CommandID: commandIDFor(name, e.EventID), OrderID: e.OrderID}}
	}
	return nil
}
```
