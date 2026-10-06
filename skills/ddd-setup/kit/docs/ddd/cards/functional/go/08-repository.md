# Repository: Go

The rules are in [the card](../08-repository.md).

```go
package ordering

import (
	"context"
	"errors"
)

var ErrOrderNotFound = errors.New("order not found")

type OrderID struct{ v string }

func (id OrderID) String() string { return id.v }

//sumtype:decl
type Order interface{ isOrder() }

type DraftOrder struct{ ID OrderID }

func (DraftOrder) isOrder() {}

// Declared here so the domain owns the contract; the SQL implementation
// lives in another package and imports this one.
type Orders interface {
	// ByID returns ErrOrderNotFound when no order has the given ID.
	ByID(ctx context.Context, id OrderID) (Order, error)
	Save(ctx context.Context, o Order) error
}
```
