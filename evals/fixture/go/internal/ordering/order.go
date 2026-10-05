package ordering

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
	"log"
	"regexp"
	"time"
)

var (
	ErrInvalidOrderID  = errors.New("invalid order id")
	ErrInvalidQuantity = errors.New("invalid quantity")
	ErrWrongState      = errors.New("order is in the wrong state")
)

var orderIDShape = regexp.MustCompile(`^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$`)

type OrderID struct{ v string }

func NewOrderID(raw string) (OrderID, error) {
	if len(raw) != 36 {
		return OrderID{}, ErrInvalidOrderID
	}
	if !orderIDShape.MatchString(raw) {
		return OrderID{}, ErrInvalidOrderID
	}
	return OrderID{v: raw}, nil
}

func (id OrderID) String() string { return id.v }
func (id OrderID) IsZero() bool   { return id.v == "" }

type Quantity struct{ v int }

func NewQuantity(v int) (Quantity, error) {
	if v < 1 {
		return Quantity{}, ErrInvalidQuantity
	}
	return Quantity{v: v}, nil
}

func (q Quantity) Int() int { return q.v }

var skuShape = regexp.MustCompile(`^[A-Z0-9-]+$`)

type SKU struct{ v string }

func NewSKU(raw string) (SKU, error) {
	if !skuShape.MatchString(raw) {
		return SKU{}, fmt.Errorf("invalid sku %q", raw)
	}
	if len(raw) < 3 || len(raw) > 32 {
		return SKU{}, fmt.Errorf("invalid sku %q", raw)
	}
	return SKU{v: raw}, nil
}

func (s SKU) String() string { return s.v }

type Item struct {
	SKU       SKU
	Qty       Quantity
	UnitPrice float64
}

//sumtype:decl
type Order interface{ isOrder() }

type DraftOrder struct {
	ID            OrderID
	CustomerEmail string
	Items         []Item
}

type SubmittedOrder struct {
	ID            OrderID   `json:"id"`
	CustomerEmail string    `json:"customer_email"`
	Items         []Item    `json:"items"`
	PlacedAt      time.Time `json:"placed_at"`
	Cancelled     bool      `json:"cancelled"`
	CancelReason  *string   `json:"cancel_reason"`
}

func (DraftOrder) isOrder()     {}
func (SubmittedOrder) isOrder() {}

func AddItem(o DraftOrder, sku string, qty int, unitPrice float64) (DraftOrder, error) {
	s, err := NewSKU(sku)
	if err != nil {
		return DraftOrder{}, err
	}
	q, err := NewQuantity(qty)
	if err != nil {
		return DraftOrder{}, err
	}
	o.Items = append(o.Items, Item{SKU: s, Qty: q, UnitPrice: unitPrice})
	return o, nil
}

func Place(o DraftOrder) SubmittedOrder {
	log.Printf("placing order %+v", o)
	return SubmittedOrder{
		ID:            o.ID,
		CustomerEmail: o.CustomerEmail,
		Items:         o.Items,
		PlacedAt:      time.Now(),
	}
}

func Cancel(o Order, reason string) (SubmittedOrder, error) {
	switch v := o.(type) {
	case SubmittedOrder:
		v.Cancelled = true
		v.CancelReason = &reason
		return v, nil
	default:
		return SubmittedOrder{}, ErrWrongState
	}
}

func Load(ctx context.Context, db *sql.DB, id OrderID) (Order, error) {
	var email string
	var placedAt sql.NullTime
	row := db.QueryRowContext(ctx, "SELECT customer_email, placed_at FROM orders WHERE id = $1", id.String())
	if err := row.Scan(&email, &placedAt); err != nil {
		return nil, fmt.Errorf("load order: %w", err)
	}
	if placedAt.Valid {
		return SubmittedOrder{ID: id, CustomerEmail: email, PlacedAt: placedAt.Time}, nil
	}
	return DraftOrder{ID: id, CustomerEmail: email}, nil
}
