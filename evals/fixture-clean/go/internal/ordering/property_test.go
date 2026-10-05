package ordering

import (
	"errors"
	"math/rand/v2"
	"testing"
	"time"
)

// Random command sequences, with the model's invariants checked after every step.
// The examples in decisions_test.go cover the cases somebody thought of; this covers the orders nobody did.
// A failure prints its seed: rerun with that seed alone to reproduce it.
func TestInvariantsHoldForAnyCommandSequence(t *testing.T) {
	const sequences, steps = 2000, 60
	for seed := range uint64(sequences) {
		r := rand.New(rand.NewPCG(seed, 0))
		var order Order = testDraft()
		if seed%4 == 0 {
			// A random sequence almost never adds 100 items before it places or cancels,
			// so some start close to the limit to make sure it is exercised.
			order = draftWithItems(t, 97)
		}
		now := tenOClock
		for step := range steps {
			now = now.Add(time.Duration(r.IntN(120)) * time.Second)
			before := order
			order = randomCommand(t, r, order, now)
			if problem := brokenInvariant(before, order); problem != "" {
				t.Fatalf("seed %d, step %d: %s", seed, step, problem)
			}
		}
	}
}

// Applies one command if the state allows it, as a workflow would after narrowing.
// A command the state does not allow has no function to call: that is invariants 4 and 5, enforced by the types.
func randomCommand(t *testing.T, r *rand.Rand, o Order, now time.Time) Order {
	t.Helper()
	draft, isDraft := o.(DraftOrder)
	switch roll := r.IntN(100); {
	case roll < 88:
		if !isDraft {
			return o
		}
		age := time.Duration(r.IntN(400)) * time.Second
		next, err := AddItem(draft, must(NewQuantity(1+r.IntN(1000))), quoteABC1(now.Add(-age)), now)
		switch {
		case err == nil:
			return next
		case errors.Is(err, ErrQuoteExpired) && age > 5*time.Minute:
		case errors.Is(err, ErrTooManyItems) && len(draft.Items()) == 100:
		default:
			t.Fatalf("AddItem with %d items and a quote %s old: %v", len(draft.Items()), age, err)
		}
		return o
	case roll < 96:
		if !isDraft {
			return o
		}
		placed, _, err := PlaceOrder(draft, now)
		if err != nil {
			if !errors.Is(err, ErrEmptyOrder) || len(draft.Items()) != 0 {
				t.Fatalf("PlaceOrder with %d items: %v", len(draft.Items()), err)
			}
			return o
		}
		return placed
	default:
		cancellable, ok := o.(CancellableOrder)
		if !ok {
			return o
		}
		cancelled, _ := CancelOrder(cancellable, must(NewCancellationReason("changed my mind")), now)
		return cancelled
	}
}

func brokenInvariant(before, after Order) string {
	if after.ID() != before.ID() || after.Customer() != before.Customer() {
		return "the order's id or customer changed"
	}
	switch o := after.(type) {
	case DraftOrder:
		if len(o.Items()) > 100 {
			return "a draft order has more than 100 items"
		}
		if _, wasDraft := before.(DraftOrder); !wasDraft {
			return "an order went back to being a draft"
		}
	case PlacedOrder:
		if len(o.Items()) == 0 {
			return "invariant 1: a placed order has no items"
		}
		if o.PlacedAt().IsZero() {
			return "invariant 2: a placed order has no time of placing"
		}
		if was, ok := before.(PlacedOrder); ok && (len(was.Items()) != len(o.Items()) || !was.PlacedAt().Equal(o.PlacedAt())) {
			return "invariant 4: a placed order changed"
		}
		if _, wasCancelled := before.(CancelledOrder); wasCancelled {
			return "invariant 5: a cancelled order was placed"
		}
	case CancelledOrder:
		if o.Reason().IsZero() {
			return "invariant 3: a cancelled order has no reason"
		}
	}
	return ""
}
