# Value object: Go

The rules are in [the card](../02-value-object.md).

```go
package billing

import (
	"errors"
	"fmt"
)

var (
	ErrNegativeAmount   = errors.New("negative amount")
	ErrUnknownCurrency  = errors.New("unknown currency")
	ErrCurrencyMismatch = errors.New("currency mismatch")
)

type Currency int

// Starts at 1 so the zero value is not a real currency.
const (
	SEK Currency = iota + 1
	EUR
)

func (c Currency) valid() bool {
	switch c {
	case SEK, EUR:
		return true
	}
	return false
}

type Money struct {
	minor    int64
	currency Currency
}

func NewMoney(minor int64, c Currency) (Money, error) {
	if !c.valid() {
		return Money{}, ErrUnknownCurrency
	}
	if minor < 0 {
		return Money{}, fmt.Errorf("%w: %d", ErrNegativeAmount, minor)
	}
	return Money{minor: minor, currency: c}, nil
}

func (m Money) Add(o Money) (Money, error) {
	if m.currency != o.currency {
		return Money{}, ErrCurrencyMismatch
	}
	return Money{minor: m.minor + o.minor, currency: m.currency}, nil
}

func (m Money) Minor() int64       { return m.minor }
func (m Money) Currency() Currency { return m.currency }
```
