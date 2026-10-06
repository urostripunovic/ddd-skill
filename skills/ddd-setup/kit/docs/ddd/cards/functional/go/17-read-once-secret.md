# Read-once secret: Go

The rules are in [the card](../17-read-once-secret.md).

```go
package identity

import (
	"errors"
	"log/slog"
	"sync"
)

var (
	ErrInvalidSecret         = errors.New("invalid secret")
	ErrSecretAlreadyRead     = errors.New("secret already read")
	ErrSecretNotSerialisable = errors.New("secret cannot be serialised")
)

const (
	maxSecretLen = 1024
	placeholder  = "[secret]"
)

type Secret struct {
	mu   sync.Mutex
	v    []byte
	read bool
}

func NewSecret(v []byte) (*Secret, error) {
	if len(v) == 0 || len(v) > maxSecretLen {
		// The value is not included: a rejected secret is still a secret.
		return nil, ErrInvalidSecret
	}
	return &Secret{v: append([]byte(nil), v...)}, nil
}

func (s *Secret) Reveal() ([]byte, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	if s.read {
		return nil, ErrSecretAlreadyRead
	}
	s.read = true
	v := s.v
	s.v = nil
	return v, nil
}

func (s *Secret) String() string               { return placeholder }
func (s *Secret) GoString() string             { return placeholder }
func (s *Secret) LogValue() slog.Value         { return slog.StringValue(placeholder) }
func (s *Secret) MarshalJSON() ([]byte, error) { return nil, ErrSecretNotSerialisable }
```
