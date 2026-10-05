package ordering

import "testing"

func TestNewQuantity(t *testing.T) {
	q, err := NewQuantity(5)
	if err != nil || q.Int() != 5 {
		t.Fatalf("got %v, %v", q, err)
	}
}

func TestPlace(t *testing.T) {
	id, _ := NewOrderID("123e4567-e89b-12d3-a456-426614174000")
	draft, err := AddItem(DraftOrder{ID: id, CustomerEmail: "a@example.com"}, "ABC-1", 2, 9.99)
	if err != nil {
		t.Fatal(err)
	}
	placed := Place(draft)
	if len(placed.Items) != 1 {
		t.Fatalf("got %d items", len(placed.Items))
	}
}
