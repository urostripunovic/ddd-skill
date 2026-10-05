package ordering

import (
	"context"
	"errors"
	"fmt"
	"strings"
	"testing"
	"time"
)

// These tests are the Examples table of docs/domain/contexts/ordering.md, row by row.

var tenOClock = time.Date(2026, 3, 1, 10, 0, 0, 0, time.UTC)

func must[T any](v T, err error) T {
	if err != nil {
		panic(err)
	}
	return v
}

func testDraft() DraftOrder {
	id := must(NewOrderID("123e4567-e89b-12d3-a456-426614174000"))
	return StartOrder(id, must(NewCustomerEmail("a@example.com")))
}

func quoteABC1(at time.Time) PriceQuote {
	return NewPriceQuote(must(NewSKU("ABC-1")), must(NewPrice(999)), at)
}

func draftWithItems(t *testing.T, n int) DraftOrder {
	t.Helper()
	o := testDraft()
	for range n {
		next, err := AddItem(o, must(NewQuantity(1)), quoteABC1(tenOClock), tenOClock)
		if err != nil {
			t.Fatalf("building a draft with %d items: %v", n, err)
		}
		o = next
	}
	return o
}

func TestExample1StartOrder(t *testing.T) {
	o := testDraft()
	if len(o.Items()) != 0 || o.Customer().Reveal() != "a@example.com" {
		t.Fatalf("got %d items for %s", len(o.Items()), o.Customer().Reveal())
	}
}

func TestExample2AddItem(t *testing.T) {
	o, err := AddItem(testDraft(), must(NewQuantity(2)), quoteABC1(tenOClock), tenOClock.Add(time.Minute))
	if err != nil {
		t.Fatal(err)
	}
	items := o.Items()
	if len(items) != 1 || items[0].SKU().String() != "ABC-1" || items[0].Quantity().Int() != 2 || items[0].UnitPrice().Minor() != 999 {
		t.Fatalf("got %+v", items)
	}
}

func TestExample3SameProductTwiceGivesTwoItems(t *testing.T) {
	if got := len(draftWithItems(t, 2).Items()); got != 2 {
		t.Fatalf("got %d items", got)
	}
}

func TestExample4QuoteExpired(t *testing.T) {
	quote := quoteABC1(tenOClock)
	if _, err := AddItem(testDraft(), must(NewQuantity(2)), quote, tenOClock.Add(5*time.Minute)); err != nil {
		t.Fatalf("a quote exactly five minutes old was rejected: %v", err)
	}
	_, err := AddItem(testDraft(), must(NewQuantity(2)), quote, tenOClock.Add(5*time.Minute+time.Second))
	if !errors.Is(err, ErrQuoteExpired) {
		t.Fatalf("got %v; want ErrQuoteExpired", err)
	}
}

func TestExample5TooManyItems(t *testing.T) {
	full := draftWithItems(t, 100)
	if _, err := AddItem(full, must(NewQuantity(1)), quoteABC1(tenOClock), tenOClock); !errors.Is(err, ErrTooManyItems) {
		t.Fatalf("got %v; want ErrTooManyItems", err)
	}
}

func TestExample7EmptyOrder(t *testing.T) {
	if _, _, err := PlaceOrder(testDraft(), tenOClock); !errors.Is(err, ErrEmptyOrder) {
		t.Fatalf("got %v; want ErrEmptyOrder", err)
	}
}

func TestExample8PlaceOrder(t *testing.T) {
	draft := draftWithItems(t, 1)
	placed, events, err := PlaceOrder(draft, tenOClock)
	if err != nil {
		t.Fatal(err)
	}
	if len(placed.Items()) != 1 || !placed.PlacedAt().Equal(tenOClock) {
		t.Fatalf("got %d items placed at %s", len(placed.Items()), placed.PlacedAt())
	}
	want := OrderPlaced{OrderID: draft.ID(), At: tenOClock}
	if len(events) != 1 || events[0] != want {
		t.Fatalf("got events %+v", events)
	}
}

func TestExamples9And10CancelOrder(t *testing.T) {
	placed, _, err := PlaceOrder(draftWithItems(t, 1), tenOClock)
	if err != nil {
		t.Fatal(err)
	}
	later := tenOClock.Add(5 * time.Minute)
	for name, tc := range map[string]struct {
		order  CancellableOrder
		reason string
	}{
		"a draft order":  {testDraft(), "changed my mind"},
		"a placed order": {placed, "found it cheaper"},
	} {
		t.Run(name, func(t *testing.T) {
			reason := must(NewCancellationReason(tc.reason))
			cancelled, events := CancelOrder(tc.order, reason, later)
			if cancelled.Reason() != reason || cancelled.ID() != tc.order.ID() {
				t.Fatalf("got %+v", cancelled)
			}
			want := OrderCancelled{OrderID: tc.order.ID(), Reason: reason, At: later}
			if len(events) != 1 || events[0] != want {
				t.Fatalf("got events %+v", events)
			}
		})
	}
}

func TestStatesDoNotShareItems(t *testing.T) {
	draft := draftWithItems(t, 1)
	placed, _, err := PlaceOrder(draft, tenOClock)
	if err != nil {
		t.Fatal(err)
	}
	draft.Items()[0] = Item{}
	more, err := AddItem(draft, must(NewQuantity(5)), quoteABC1(tenOClock), tenOClock)
	if err != nil {
		t.Fatal(err)
	}
	if len(placed.Items()) != 1 || len(draft.Items()) != 1 || len(more.Items()) != 2 || draft.Items()[0].Quantity().Int() != 1 {
		t.Fatal("a later change reached an earlier state")
	}
}

// Two results built from the same draft must not share a backing array.
func TestAddItemTwiceFromTheSameDraft(t *testing.T) {
	base := draftWithItems(t, 3)
	first, err := AddItem(base, must(NewQuantity(7)), quoteABC1(tenOClock), tenOClock)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := AddItem(base, must(NewQuantity(9)), quoteABC1(tenOClock), tenOClock); err != nil {
		t.Fatal(err)
	}
	if got := first.Items()[3].Quantity().Int(); got != 7 {
		t.Fatalf("an earlier state changed: quantity %d, want 7", got)
	}
}

func TestActorIsNeverPrintedWithItsEmail(t *testing.T) {
	const raw = "private@example.com"
	actor, err := Authenticate(context.Background(), func(context.Context) (Claims, error) {
		return Claims{Customer: must(NewCustomerEmail(raw))}, nil
	})
	if err != nil {
		t.Fatal(err)
	}
	for _, printed := range []string{
		fmt.Sprint(actor), fmt.Sprintf("%v", actor), fmt.Sprintf("%+v", actor), fmt.Sprintf("%#v", actor),
	} {
		if strings.Contains(printed, raw) {
			t.Fatalf("the email was printed: %s", printed)
		}
	}
}
