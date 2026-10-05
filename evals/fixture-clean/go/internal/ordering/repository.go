package ordering

import (
	"context"
	"errors"
)

var (
	ErrOrderNotFound = errors.New("order not found")
	// Returned by Save when the order was changed by someone else after it was loaded.
	ErrConflict = errors.New("order changed since it was loaded")
)

type Version int

// Declared here so the domain owns the contract. The implementation lives outside this package.
type Orders interface {
	Create(ctx context.Context, o DraftOrder) error
	// Load returns ErrOrderNotFound when there is no such order.
	Load(ctx context.Context, id OrderID) (Order, Version, error)
	// Save stores the state and its events in one transaction. It returns ErrConflict
	// when the stored version is no longer the one that was loaded.
	Save(ctx context.Context, o Order, events []Event, loaded Version) error
}
