# Event stream repository: Go

The rules are in [the card](../12-event-stream-repository.md).

Check as: boundary

```go
package eventstore

import (
	"context"
	"errors"
	"fmt"
)

var ErrConflict = errors.New("stream changed since it was loaded")

const maxAttempts = 3

type StreamID struct{ v string }

func (id StreamID) String() string { return id.v }

type Version int

type Decider[C, S, E any] struct {
	Decide  func(cmd C, state S) ([]E, error)
	Evolve  func(state S, event E) (S, error)
	Initial func() S
}

// Declared with the domain so the domain owns the contract; the database
// implementation lives in another package.
type Streams[E any] interface {
	Load(ctx context.Context, id StreamID) ([]E, Version, error)
	// Append returns ErrConflict when the stream is no longer at expected.
	Append(ctx context.Context, id StreamID, expected Version, events []E) error
}

func Handle[C, S, E any](ctx context.Context, d Decider[C, S, E], s Streams[E], id StreamID, cmd C) ([]E, error) {
	for range maxAttempts {
		events, version, err := s.Load(ctx, id)
		if err != nil {
			return nil, fmt.Errorf("load stream %s: %w", id, err)
		}

		state := d.Initial()
		for _, e := range events {
			if state, err = d.Evolve(state, e); err != nil {
				return nil, fmt.Errorf("replay stream %s: %w", id, err)
			}
		}

		decided, err := d.Decide(cmd, state)
		if err != nil {
			return nil, err
		}

		err = s.Append(ctx, id, version, decided)
		if err == nil {
			return decided, nil
		}
		// Only a conflict is retried, and the retry decides again from a fresh load.
		if !errors.Is(err, ErrConflict) {
			return nil, fmt.Errorf("append to stream %s: %w", id, err)
		}
	}
	return nil, ErrConflict
}
```
