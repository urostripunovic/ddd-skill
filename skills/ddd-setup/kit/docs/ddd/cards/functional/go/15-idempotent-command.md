# Idempotent command: Go

The rules are in [the card](../15-idempotent-command.md).

Check as: boundary

```go
package ordering

import (
	"context"
	"errors"
	"fmt"
	"time"
)

var ErrCommandAlreadyHandled = errors.New("command already handled")

type CommandID struct{ v string }

func (id CommandID) String() string { return id.v }

type OrderID struct{ v string }

func (id OrderID) String() string { return id.v }

type DraftOrder struct{ id OrderID }

type PlacedOrder struct {
	id       OrderID
	placedAt time.Time
}

func (o PlacedOrder) ID() OrderID         { return o.id }
func (o PlacedOrder) PlacedAt() time.Time { return o.placedAt }

func Place(o DraftOrder, now time.Time) PlacedOrder {
	return PlacedOrder{id: o.id, placedAt: now}
}

type PlaceOrderDeps struct {
	WasHandled func(ctx context.Context, cmd CommandID) (bool, error)
	LoadDraft  func(ctx context.Context, id OrderID) (DraftOrder, error)
	// Stores the order and the command ID in one transaction. Returns
	// ErrCommandAlreadyHandled when the unique constraint on the command ID rejects it.
	SavePlaced func(ctx context.Context, o PlacedOrder, cmd CommandID) error
	Now        func() time.Time
}

func PlaceOrder(ctx context.Context, deps PlaceOrderDeps, cmd CommandID, id OrderID) error {
	handled, err := deps.WasHandled(ctx, cmd)
	if err != nil {
		return fmt.Errorf("look up command %s: %w", cmd, err)
	}
	if handled {
		return nil
	}
	draft, err := deps.LoadDraft(ctx, id)
	if err != nil {
		return fmt.Errorf("load order: %w", err)
	}
	err = deps.SavePlaced(ctx, Place(draft, deps.Now()), cmd)
	// A concurrent copy of this command won the race; its outcome is ours.
	if errors.Is(err, ErrCommandAlreadyHandled) {
		return nil
	}
	if err != nil {
		return fmt.Errorf("save placed order: %w", err)
	}
	return nil
}
```
