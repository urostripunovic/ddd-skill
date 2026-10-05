package app_test

import (
	"context"
	"errors"
	"testing"
	"time"

	"fixture/internal/app"
	"fixture/internal/ordering"
)

var tenOClock = time.Date(2026, 3, 1, 10, 0, 0, 0, time.UTC)

func must[T any](v T, err error) T {
	if err != nil {
		panic(err)
	}
	return v
}

// An in-memory Orders with the same version check a database implementation makes.
type memOrders struct {
	orders   map[ordering.OrderID]ordering.Order
	versions map[ordering.OrderID]ordering.Version
	events   []ordering.Event
	// Runs once, just before the next Save, to play the part of a competing request.
	beforeSave func()
	saves      int
}

func newMemOrders() *memOrders {
	return &memOrders{orders: map[ordering.OrderID]ordering.Order{}, versions: map[ordering.OrderID]ordering.Version{}}
}

func (m *memOrders) Create(_ context.Context, o ordering.DraftOrder) error {
	m.orders[o.ID()] = o
	m.versions[o.ID()] = 1
	return nil
}

func (m *memOrders) Load(_ context.Context, id ordering.OrderID) (ordering.Order, ordering.Version, error) {
	o, ok := m.orders[id]
	if !ok {
		return nil, 0, ordering.ErrOrderNotFound
	}
	return o, m.versions[id], nil
}

func (m *memOrders) Save(_ context.Context, o ordering.Order, events []ordering.Event, loaded ordering.Version) error {
	m.saves++
	if hook := m.beforeSave; hook != nil {
		m.beforeSave = nil
		hook()
	}
	if m.versions[o.ID()] != loaded {
		return ordering.ErrConflict
	}
	m.orders[o.ID()] = o
	m.versions[o.ID()] = loaded + 1
	m.events = append(m.events, events...)
	return nil
}

func actorFor(t *testing.T, email string) ordering.Actor {
	t.Helper()
	actor, err := ordering.Authenticate(context.Background(), func(context.Context) (ordering.Claims, error) {
		return ordering.Claims{Customer: must(ordering.NewCustomerEmail(email))}, nil
	})
	if err != nil {
		t.Fatal(err)
	}
	return actor
}

type fixture struct {
	deps   app.Deps
	orders *memOrders
	owner  ordering.Actor
	other  ordering.Actor
	sku    ordering.SKU
	one    ordering.Quantity
	reason ordering.CancellationReason
}

func setup(t *testing.T) fixture {
	t.Helper()
	orders := newMemOrders()
	return fixture{
		orders: orders,
		deps: app.Deps{
			Orders: orders,
			QuotePrice: func(_ context.Context, sku ordering.SKU) (ordering.PriceQuote, error) {
				return ordering.NewPriceQuote(sku, must(ordering.NewPrice(999)), tenOClock), nil
			},
			NewOrderID: func() (ordering.OrderID, error) {
				return ordering.NewOrderID("123e4567-e89b-12d3-a456-426614174000")
			},
			Now: func() time.Time { return tenOClock },
		},
		owner:  actorFor(t, "owner@example.com"),
		other:  actorFor(t, "other@example.com"),
		sku:    must(ordering.NewSKU("ABC-1")),
		one:    must(ordering.NewQuantity(1)),
		reason: must(ordering.NewCancellationReason("changed my mind")),
	}
}

func (f fixture) draftWithItem(t *testing.T) ordering.OrderID {
	t.Helper()
	ctx := context.Background()
	id, err := app.StartOrder(ctx, f.deps, f.owner)
	if err != nil {
		t.Fatal(err)
	}
	if err := app.AddItem(ctx, f.deps, f.owner, id, f.sku, f.one); err != nil {
		t.Fatal(err)
	}
	return id
}

func TestStartAddPlace(t *testing.T) {
	f := setup(t)
	id := f.draftWithItem(t)
	if err := app.PlaceOrder(context.Background(), f.deps, f.owner, id); err != nil {
		t.Fatal(err)
	}
	if _, ok := f.orders.orders[id].(ordering.PlacedOrder); !ok {
		t.Fatalf("stored %T; want a placed order", f.orders.orders[id])
	}
	if len(f.orders.events) != 1 {
		t.Fatalf("stored %d events; want OrderPlaced alone", len(f.orders.events))
	}
}

func TestNobodySignedInCannotStartAnOrder(t *testing.T) {
	f := setup(t)
	if _, err := app.StartOrder(context.Background(), f.deps, nil); !errors.Is(err, ordering.ErrNotAllowed) {
		t.Fatalf("got %v; want ErrNotAllowed", err)
	}
	if len(f.orders.orders) != 0 {
		t.Fatal("an order was created")
	}
}

func TestOnlyTheOwnerMayChangeAnOrder(t *testing.T) {
	ctx := context.Background()
	for name, command := range map[string]func(fixture, ordering.Actor, ordering.OrderID) error{
		"AddItem": func(f fixture, a ordering.Actor, id ordering.OrderID) error {
			return app.AddItem(ctx, f.deps, a, id, f.sku, f.one)
		},
		"PlaceOrder": func(f fixture, a ordering.Actor, id ordering.OrderID) error {
			return app.PlaceOrder(ctx, f.deps, a, id)
		},
		"CancelOrder": func(f fixture, a ordering.Actor, id ordering.OrderID) error {
			return app.CancelOrder(ctx, f.deps, a, id, f.reason)
		},
	} {
		t.Run(name, func(t *testing.T) {
			for _, intruder := range []ordering.Actor{nil, setup(t).other} {
				f := setup(t)
				id := f.draftWithItem(t)
				saves := f.orders.saves
				if err := command(f, intruder, id); !errors.Is(err, ordering.ErrNotAllowed) {
					t.Fatalf("got %v; want ErrNotAllowed", err)
				}
				if f.orders.saves != saves {
					t.Fatal("the order was saved")
				}
			}
		})
	}
}

func TestSomeoneElseLearnsNothingAboutTheOrdersState(t *testing.T) {
	f := setup(t)
	ctx := context.Background()
	id := f.draftWithItem(t)
	if err := app.PlaceOrder(ctx, f.deps, f.owner, id); err != nil {
		t.Fatal(err)
	}
	// The owner would get ErrOrderNotDraft here. Someone else must not be told that much.
	if err := app.PlaceOrder(ctx, f.deps, f.other, id); !errors.Is(err, ordering.ErrNotAllowed) {
		t.Fatalf("got %v; want ErrNotAllowed", err)
	}
}

func TestUseCaseFailures(t *testing.T) {
	ctx := context.Background()
	f := setup(t)
	missing := must(ordering.NewOrderID("00000000-0000-0000-0000-000000000000"))
	if err := app.PlaceOrder(ctx, f.deps, f.owner, missing); !errors.Is(err, ordering.ErrOrderNotFound) {
		t.Fatalf("no such order: got %v; want ErrOrderNotFound", err)
	}

	id := f.draftWithItem(t)
	if err := app.PlaceOrder(ctx, f.deps, f.owner, id); err != nil {
		t.Fatal(err)
	}
	if err := app.PlaceOrder(ctx, f.deps, f.owner, id); !errors.Is(err, app.ErrOrderNotDraft) {
		t.Fatalf("placing twice: got %v; want ErrOrderNotDraft", err)
	}
	if err := app.AddItem(ctx, f.deps, f.owner, id, f.sku, f.one); !errors.Is(err, app.ErrOrderNotDraft) {
		t.Fatalf("adding to a placed order: got %v; want ErrOrderNotDraft", err)
	}
	if err := app.CancelOrder(ctx, f.deps, f.owner, id, f.reason); err != nil {
		t.Fatalf("cancelling a placed order: %v", err)
	}
	second := must(ordering.NewCancellationReason("another reason"))
	if err := app.CancelOrder(ctx, f.deps, f.owner, id, second); !errors.Is(err, app.ErrOrderAlreadyCancelled) {
		t.Fatalf("cancelling twice: got %v; want ErrOrderAlreadyCancelled", err)
	}
	cancelled, ok := f.orders.orders[id].(ordering.CancelledOrder)
	if !ok || cancelled.Reason() != f.reason {
		t.Fatal("the first reason did not stand")
	}
}

// The Races table of the model: the command that is saved second is judged against what the first left behind.
func TestRaces(t *testing.T) {
	ctx := context.Background()

	t.Run("PlaceOrder loses to a cancel", func(t *testing.T) {
		f := setup(t)
		id := f.draftWithItem(t)
		f.orders.beforeSave = func() {
			f.orders.orders[id], _ = ordering.CancelOrder(f.orders.orders[id].(ordering.DraftOrder), f.reason, tenOClock)
			f.orders.versions[id]++
		}
		if err := app.PlaceOrder(ctx, f.deps, f.owner, id); !errors.Is(err, app.ErrOrderNotDraft) {
			t.Fatalf("got %v; want ErrOrderNotDraft", err)
		}
	})

	t.Run("CancelOrder after a place still succeeds", func(t *testing.T) {
		f := setup(t)
		id := f.draftWithItem(t)
		f.orders.beforeSave = func() {
			placed, _, err := ordering.PlaceOrder(f.orders.orders[id].(ordering.DraftOrder), tenOClock)
			if err != nil {
				t.Fatal(err)
			}
			f.orders.orders[id] = placed
			f.orders.versions[id]++
		}
		if err := app.CancelOrder(ctx, f.deps, f.owner, id, f.reason); err != nil {
			t.Fatal(err)
		}
		if _, ok := f.orders.orders[id].(ordering.CancelledOrder); !ok {
			t.Fatalf("stored %T; want a cancelled order", f.orders.orders[id])
		}
	})

	t.Run("AddItem loses to a place", func(t *testing.T) {
		f := setup(t)
		id := f.draftWithItem(t)
		f.orders.beforeSave = func() {
			placed, _, err := ordering.PlaceOrder(f.orders.orders[id].(ordering.DraftOrder), tenOClock)
			if err != nil {
				t.Fatal(err)
			}
			f.orders.orders[id] = placed
			f.orders.versions[id]++
		}
		if err := app.AddItem(ctx, f.deps, f.owner, id, f.sku, f.one); !errors.Is(err, app.ErrOrderNotDraft) {
			t.Fatalf("got %v; want ErrOrderNotDraft", err)
		}
		if got := len(f.orders.orders[id].(ordering.PlacedOrder).Items()); got != 1 {
			t.Fatalf("the placed order has %d items; want the 1 it was placed with", got)
		}
	})
}

func TestAQuoteForAnotherProductIsRefused(t *testing.T) {
	f := setup(t)
	ctx := context.Background()
	id, err := app.StartOrder(ctx, f.deps, f.owner)
	if err != nil {
		t.Fatal(err)
	}
	f.deps.QuotePrice = func(context.Context, ordering.SKU) (ordering.PriceQuote, error) {
		return ordering.NewPriceQuote(must(ordering.NewSKU("OTHER-9")), must(ordering.NewPrice(0)), tenOClock), nil
	}
	if err := app.AddItem(ctx, f.deps, f.owner, id, f.sku, f.one); err == nil {
		t.Fatal("an item was added from a quote for another product")
	}
	draft, ok := f.orders.orders[id].(ordering.DraftOrder)
	if !ok || len(draft.Items()) != 0 {
		t.Fatal("the order changed")
	}
}
