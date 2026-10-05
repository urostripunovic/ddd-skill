package ordering

import (
	"errors"
	"regexp"
	"strings"
	"unicode/utf8"
)

// None of these errors carries the rejected input: it is untrusted, and may be large or sensitive.
var (
	ErrInvalidOrderID            = errors.New("invalid order id")
	ErrInvalidSKU                = errors.New("invalid sku")
	ErrInvalidQuantity           = errors.New("invalid quantity")
	ErrInvalidPrice              = errors.New("invalid price")
	ErrInvalidCustomerEmail      = errors.New("invalid customer email")
	ErrInvalidCancellationReason = errors.New("invalid cancellation reason")
)

const (
	orderIDLen               = 36
	minSKULen                = 3
	maxSKULen                = 32
	minQuantity              = 1
	maxQuantity              = 1000
	maxPriceMinor            = 100_000_000
	maxCustomerEmailLen      = 254
	maxCancellationReasonLen = 200
	emailPlaceholder         = "[customer email]"
)

var orderIDShape = regexp.MustCompile(`^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$`)

type OrderID struct{ v string }

func NewOrderID(raw string) (OrderID, error) {
	// Length first, so the regular expression never runs on oversized input.
	if len(raw) != orderIDLen {
		return OrderID{}, ErrInvalidOrderID
	}
	if !orderIDShape.MatchString(raw) {
		return OrderID{}, ErrInvalidOrderID
	}
	return OrderID{v: raw}, nil
}

func (id OrderID) String() string { return id.v }
func (id OrderID) IsZero() bool   { return id.v == "" }

type SKU struct{ v string }

func NewSKU(raw string) (SKU, error) {
	if len(raw) < minSKULen || len(raw) > maxSKULen {
		return SKU{}, ErrInvalidSKU
	}
	for _, c := range []byte(raw) {
		if (c < 'A' || c > 'Z') && (c < '0' || c > '9') && c != '-' {
			return SKU{}, ErrInvalidSKU
		}
	}
	return SKU{v: raw}, nil
}

func (s SKU) String() string { return s.v }
func (s SKU) IsZero() bool   { return s.v == "" }

type Quantity struct{ v int }

func NewQuantity(v int) (Quantity, error) {
	if v < minQuantity || v > maxQuantity {
		return Quantity{}, ErrInvalidQuantity
	}
	return Quantity{v: v}, nil
}

func (q Quantity) Int() int     { return q.v }
func (q Quantity) IsZero() bool { return q.v == 0 }

// The zero value is a valid price: nothing to pay.
type Price struct{ minor int64 }

func NewPrice(minor int64) (Price, error) {
	if minor < 0 || minor > maxPriceMinor {
		return Price{}, ErrInvalidPrice
	}
	return Price{minor: minor}, nil
}

func (p Price) Minor() int64 { return p.minor }

// Sensitive in the model, so every way of printing or serialising it gives a placeholder.
type CustomerEmail struct{ v string }

func NewCustomerEmail(raw string) (CustomerEmail, error) {
	if len(raw) == 0 || len(raw) > maxCustomerEmailLen {
		return CustomerEmail{}, ErrInvalidCustomerEmail
	}
	if strings.Count(raw, "@") != 1 {
		return CustomerEmail{}, ErrInvalidCustomerEmail
	}
	return CustomerEmail{v: raw}, nil
}

// Reveal is for the adapter that has to send or store the address. Nothing else calls it.
func (e CustomerEmail) Reveal() string { return e.v }
func (e CustomerEmail) IsZero() bool   { return e.v == "" }

func (CustomerEmail) String() string               { return emailPlaceholder }
func (CustomerEmail) GoString() string             { return emailPlaceholder }
func (CustomerEmail) MarshalJSON() ([]byte, error) { return []byte(`"` + emailPlaceholder + `"`), nil }

type CancellationReason struct{ v string }

func NewCancellationReason(raw string) (CancellationReason, error) {
	// Bytes before characters: a string longer than this in bytes cannot be short enough in characters.
	if len(raw) == 0 || len(raw) > maxCancellationReasonLen*utf8.UTFMax {
		return CancellationReason{}, ErrInvalidCancellationReason
	}
	if !utf8.ValidString(raw) || utf8.RuneCountInString(raw) > maxCancellationReasonLen {
		return CancellationReason{}, ErrInvalidCancellationReason
	}
	return CancellationReason{v: raw}, nil
}

func (r CancellationReason) String() string { return r.v }
func (r CancellationReason) IsZero() bool   { return r.v == "" }
