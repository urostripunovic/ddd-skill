# Errors as values: Go

The rules are in [the card](../10-errors-as-values.md).

```go
package ordering

import (
	"errors"
	"fmt"
)

var ErrOrderAlreadyPlaced = errors.New("order already placed")

type SKU struct{ v string }

func (s SKU) String() string { return s.v }

type Quantity struct{ v int }

func (q Quantity) Int() int { return q.v }

// A separate type from Quantity so "requested" and "available" cannot be swapped.
type StockLevel struct{ v int }

func (l StockLevel) Int() int { return l.v }

type InsufficientStockError struct {
	SKU       SKU
	Requested Quantity
	Available StockLevel
}

func (e InsufficientStockError) Error() string {
	return fmt.Sprintf("insufficient stock for %s: requested %d, available %d", e.SKU, e.Requested.Int(), e.Available.Int())
}

func Reserve(sku SKU, requested Quantity, available StockLevel) error {
	if requested.Int() > available.Int() {
		return InsufficientStockError{SKU: sku, Requested: requested, Available: available}
	}
	return nil
}

func UserMessage(err error) string {
	var stock InsufficientStockError
	switch {
	case errors.As(err, &stock):
		return fmt.Sprintf("Only %d left in stock.", stock.Available.Int())
	case errors.Is(err, ErrOrderAlreadyPlaced):
		return "This order has already been placed."
	default:
		// Unknown errors get a fixed message so internals never reach the user.
		return "Something went wrong."
	}
}
```
