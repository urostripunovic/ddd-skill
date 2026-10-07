# Anticorruption layer: Go

The rules are in [the card](../09-anticorruption-layer.md).

Check as: boundary

In a real project `Payment` and its primitives live in the domain package and `Charge` in the adapter package. They share one block here only so the example compiles alone.

```go
package pspadapter

import (
	"errors"
	"fmt"
)

var (
	ErrUnknownStatus   = errors.New("unknown provider status")
	ErrMalformedCharge = errors.New("malformed provider charge")
)

// Example bounds, not payment rules: take the real ones from the model's Domain primitives table,
// and what happens when a value breaks them. Here a decline reason over the bound makes the charge
// malformed, which is an error, not a decline.
const maxDeclineReason = 64

type AmountMinor struct{ v int64 }

func NewAmountMinor(v int64) (AmountMinor, error) {
	if v < 0 {
		return AmountMinor{}, fmt.Errorf("amount %d is negative", v)
	}
	return AmountMinor{v: v}, nil
}

func (a AmountMinor) Int64() int64 { return a.v }

// The zero value is the empty string, which NewDeclineReason rejects, so it is detectable with IsZero.
type DeclineReason struct{ v string }

func NewDeclineReason(v string) (DeclineReason, error) {
	if v == "" || len(v) > maxDeclineReason {
		return DeclineReason{}, fmt.Errorf("decline reason must be 1 to %d bytes", maxDeclineReason)
	}
	return DeclineReason{v: v}, nil
}

func (r DeclineReason) String() string { return r.v }
func (r DeclineReason) IsZero() bool   { return r.v == "" }

//sumtype:decl
type Payment interface{ isPayment() }

type Authorized struct{ Amount AmountMinor }
type Declined struct{ Reason DeclineReason }

func (Authorized) isPayment() {}
func (Declined) isPayment()   {}

type Charge struct {
	Status      string `json:"status"`
	AmountMinor int64  `json:"amount"`
	FailureCode string `json:"failure_code"`
}

func ToPayment(c Charge) (Payment, error) {
	switch c.Status {
	case "authorized", "captured":
		amount, err := NewAmountMinor(c.AmountMinor)
		if err != nil {
			return nil, fmt.Errorf("%w: %w", ErrMalformedCharge, err)
		}
		return Authorized{Amount: amount}, nil
	case "declined", "failed":
		reason, err := NewDeclineReason(c.FailureCode)
		if err != nil {
			return nil, fmt.Errorf("%w: %w", ErrMalformedCharge, err)
		}
		return Declined{Reason: reason}, nil
	default:
		// A status added by the provider must fail loudly, not be treated as a known state.
		return nil, fmt.Errorf("%w: %q", ErrUnknownStatus, c.Status)
	}
}
```
