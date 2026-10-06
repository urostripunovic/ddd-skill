# Domain primitive: Go

The rules are in [the card](../01-domain-primitive.md).

```go
package ordering

import (
	"errors"
	"fmt"
)

var ErrInvalidQuantity = errors.New("invalid quantity")

const maxQuantity = 1000

// The zero value is deliberately outside the valid range, so a Quantity
// that skipped NewQuantity is detectable with IsZero.
type Quantity struct{ v int }

func NewQuantity(v int) (Quantity, error) {
	if v < 1 || v > maxQuantity {
		return Quantity{}, fmt.Errorf("%w: %d not in 1..%d", ErrInvalidQuantity, v, maxQuantity)
	}
	return Quantity{v: v}, nil
}

func (q Quantity) Int() int     { return q.v }
func (q Quantity) IsZero() bool { return q.v == 0 }
```
