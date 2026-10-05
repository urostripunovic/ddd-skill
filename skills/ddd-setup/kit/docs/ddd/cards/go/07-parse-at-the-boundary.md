# Parse at the boundary: Go

The rules are in [the card](../07-parse-at-the-boundary.md).

Check as: boundary

```go
package httpapi

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"regexp"
)

var ErrInvalidEmail = errors.New("invalid email")

const (
	maxBodyBytes   = 4 << 10
	maxEmailLength = 254
)

var emailShape = regexp.MustCompile(`^[^\s@]+@[^\s@]+\.[^\s@]+$`)

type Email struct{ v string }

func (e Email) String() string { return e.v }

func ParseEmail(raw string) (Email, error) {
	// Length is checked before the regex so oversized input never reaches the costlier check.
	if len(raw) > maxEmailLength {
		return Email{}, fmt.Errorf("%w: too long", ErrInvalidEmail)
	}
	if !emailShape.MatchString(raw) {
		return Email{}, fmt.Errorf("%w: malformed", ErrInvalidEmail)
	}
	return Email{v: raw}, nil
}

type RegisterCustomer struct{ Email Email }

type registerRequest struct {
	Email string `json:"email"`
}

func DecodeRegisterCustomer(body io.Reader) (RegisterCustomer, error) {
	dec := json.NewDecoder(io.LimitReader(body, maxBodyBytes))
	dec.DisallowUnknownFields()

	var req registerRequest
	if err := dec.Decode(&req); err != nil {
		return RegisterCustomer{}, fmt.Errorf("decode request: %w", err)
	}
	email, err := ParseEmail(req.Email)
	if err != nil {
		return RegisterCustomer{}, err
	}
	return RegisterCustomer{Email: email}, nil
}
```
