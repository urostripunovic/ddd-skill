# Domain event: Go

The rules are in [the card](../05-domain-event.md).

```go
package ordering

import (
	"fmt"
	"time"
)

type OrderID struct{ v string }

func (id OrderID) String() string { return id.v }

type CancellationReason struct{ v string }

func (r CancellationReason) String() string { return r.v }

//sumtype:decl
type Event interface {
	isEvent()
	OccurredAt() time.Time
}

type OrderPlaced struct {
	OrderID OrderID
	At      time.Time
}

type OrderCancelled struct {
	OrderID OrderID
	Reason  CancellationReason
	At      time.Time
}

func (OrderPlaced) isEvent()                   {}
func (OrderCancelled) isEvent()                {}
func (e OrderPlaced) OccurredAt() time.Time    { return e.At }
func (e OrderCancelled) OccurredAt() time.Time { return e.At }

func Describe(e Event) string {
	switch e := e.(type) {
	case OrderPlaced:
		return fmt.Sprintf("order %s placed", e.OrderID)
	case OrderCancelled:
		return fmt.Sprintf("order %s cancelled: %s", e.OrderID, e.Reason)
	}
	panic("ordering: nil Event")
}
```
