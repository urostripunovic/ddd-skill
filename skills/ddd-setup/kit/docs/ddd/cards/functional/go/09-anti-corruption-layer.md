# Anti-corruption layer: Go

The rules are in [the card](../09-anti-corruption-layer.md).

Check as: boundary

In a real project `Payment` lives in the domain package and `Charge` in the adapter package. They share one block here only so the example compiles alone.

```go
package pspadapter

import (
	"errors"
	"fmt"
)

var ErrUnknownStatus = errors.New("unknown provider status")

//sumtype:decl
type Payment interface{ isPayment() }

type Authorized struct{ AmountMinor int64 }
type Declined struct{ Reason string }

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
		return Authorized{AmountMinor: c.AmountMinor}, nil
	case "declined", "failed":
		return Declined{Reason: c.FailureCode}, nil
	default:
		// A status added by the provider must fail loudly, not be treated as a known state.
		return nil, fmt.Errorf("%w: %q", ErrUnknownStatus, c.Status)
	}
}
```
