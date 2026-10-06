# Read model: Go

The rules are in [the card](../19-read-model.md).

Check as: boundary

```go
package orderviews

import (
	"context"
	"errors"
	"time"
)

var ErrInvalidPageSize = errors.New("invalid page size")

const maxPageSize = 100

type PageSize struct{ v int }

func NewPageSize(v int) (PageSize, error) {
	if v < 1 || v > maxPageSize {
		return PageSize{}, ErrInvalidPageSize
	}
	return PageSize{v: v}, nil
}

func (p PageSize) Int() int { return p.v }

type CustomerID struct{ v string }

func (id CustomerID) String() string { return id.v }

// Shaped for the "my orders" list. Plain values, because this is output and
// never enters a decision function.
type OrderSummary struct {
	OrderID   string
	Status    string
	ItemCount int
	// Nil until the order is placed.
	PlacedAt *time.Time
}

// Takes the customer whose orders are asked for; the caller has already
// checked that the actor may see them.
type OrderSummaries interface {
	ForCustomer(ctx context.Context, customer CustomerID, size PageSize) ([]OrderSummary, error)
}
```
