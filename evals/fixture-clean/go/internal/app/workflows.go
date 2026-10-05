// Package app holds one function per use case: load, authorise, narrow, decide, save.
// The rules are in package ordering.
package app

import (
	"context"
	"errors"
	"fmt"
	"time"

	"fixture/internal/ordering"
)

var (
	ErrOrderNotDraft         = errors.New("order is not a draft")
	ErrOrderAlreadyCancelled = errors.New("order is already cancelled")
)

const maxAttempts = 3

type Deps struct {
	Orders     ordering.Orders
	QuotePrice func(ctx context.Context, sku ordering.SKU) (ordering.PriceQuote, error)
	NewOrderID func() (ordering.OrderID, error)
	Now        func() time.Time
}

type decision func(ordering.Order) (ordering.Order, []ordering.Event, error)

// On a conflict the order is loaded and decided again, so the command that was
// saved second is judged against what the first one left behind.
func change(ctx context.Context, deps Deps, actor ordering.Actor, id ordering.OrderID, decide decision) error {
	for range maxAttempts {
		order, version, err := deps.Orders.Load(ctx, id)
		if err != nil {
			return fmt.Errorf("load order: %w", err)
		}
		// Before narrowing, so someone who does not own the order learns nothing about its state.
		if !ordering.MayChangeOrder(actor, order) {
			return ordering.ErrNotAllowed
		}
		next, events, err := decide(order)
		if err != nil {
			return err
		}
		err = deps.Orders.Save(ctx, next, events, version)
		if err == nil {
			return nil
		}
		if !errors.Is(err, ordering.ErrConflict) {
			return fmt.Errorf("save order: %w", err)
		}
	}
	return ordering.ErrConflict
}

func asDraft(o ordering.Order) (ordering.DraftOrder, error) {
	draft, ok := ordering.AsDraft(o)
	if !ok {
		return ordering.DraftOrder{}, ErrOrderNotDraft
	}
	return draft, nil
}

func asCancellable(o ordering.Order) (ordering.CancellableOrder, error) {
	cancellable, ok := ordering.AsCancellable(o)
	if !ok {
		return nil, ErrOrderAlreadyCancelled
	}
	return cancellable, nil
}

func StartOrder(ctx context.Context, deps Deps, actor ordering.Actor) (ordering.OrderID, error) {
	owner, ok := ordering.MayStartOrder(actor)
	if !ok {
		return ordering.OrderID{}, ordering.ErrNotAllowed
	}
	id, err := deps.NewOrderID()
	if err != nil {
		return ordering.OrderID{}, fmt.Errorf("new order id: %w", err)
	}
	if err := deps.Orders.Create(ctx, ordering.StartOrder(id, owner)); err != nil {
		return ordering.OrderID{}, fmt.Errorf("create order: %w", err)
	}
	return id, nil
}

func AddItem(ctx context.Context, deps Deps, actor ordering.Actor, id ordering.OrderID, sku ordering.SKU, quantity ordering.Quantity) error {
	return change(ctx, deps, actor, id, func(o ordering.Order) (ordering.Order, []ordering.Event, error) {
		draft, err := asDraft(o)
		if err != nil {
			return nil, nil, err
		}
		// Fetched after the checks above, so a price is only requested for an order this caller may change.
		quote, err := deps.QuotePrice(ctx, sku)
		if err != nil {
			return nil, nil, fmt.Errorf("quote price: %w", err)
		}
		// The item takes its product from the quote, so an answer for another product would be stored unnoticed.
		if quote.SKU() != sku {
			return nil, nil, errors.New("quote price: the answer is for another product")
		}
		next, err := ordering.AddItem(draft, quantity, quote, deps.Now())
		if err != nil {
			return nil, nil, err
		}
		return next, nil, nil
	})
}

func PlaceOrder(ctx context.Context, deps Deps, actor ordering.Actor, id ordering.OrderID) error {
	return change(ctx, deps, actor, id, func(o ordering.Order) (ordering.Order, []ordering.Event, error) {
		draft, err := asDraft(o)
		if err != nil {
			return nil, nil, err
		}
		placed, events, err := ordering.PlaceOrder(draft, deps.Now())
		if err != nil {
			return nil, nil, err
		}
		return placed, events, nil
	})
}

func CancelOrder(ctx context.Context, deps Deps, actor ordering.Actor, id ordering.OrderID, reason ordering.CancellationReason) error {
	return change(ctx, deps, actor, id, func(o ordering.Order) (ordering.Order, []ordering.Event, error) {
		cancellable, err := asCancellable(o)
		if err != nil {
			return nil, nil, err
		}
		cancelled, events := ordering.CancelOrder(cancellable, reason, deps.Now())
		return cancelled, events, nil
	})
}
