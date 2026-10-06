# Event versioning: Go

The rules are in [the card](../20-event-versioning.md).

Check as: boundary

```go
package orderstore

import (
	"encoding/json"
	"errors"
	"fmt"
)

var (
	ErrUnknownEvent = errors.New("unknown event type or version")
	ErrCorruptEvent = errors.New("stored event does not parse")
)

type OrderID struct{ v string }

func NewOrderID(v string) (OrderID, error) {
	if len(v) != 36 {
		return OrderID{}, ErrCorruptEvent
	}
	return OrderID{v: v}, nil
}

func (id OrderID) String() string { return id.v }

type Channel int

const (
	ChannelWeb Channel = iota + 1
	ChannelApp
)

func parseChannel(v string) (Channel, error) {
	switch v {
	case "web":
		return ChannelWeb, nil
	case "app":
		return ChannelApp, nil
	}
	return 0, ErrCorruptEvent
}

// The domain event has one shape: the current one.
type OrderPlaced struct {
	OrderID OrderID
	Channel Channel
}

type StoredEvent struct {
	Type    string
	Version int
	Data    []byte
}

type orderPlacedV1 struct {
	OrderID string `json:"orderId"`
}

type orderPlacedV2 struct {
	OrderID string `json:"orderId"`
	Channel string `json:"channel"`
}

func DecodeOrderPlaced(s StoredEvent) (OrderPlaced, error) {
	if s.Type != "order-placed" {
		return OrderPlaced{}, fmt.Errorf("%w: %s", ErrUnknownEvent, s.Type)
	}
	switch s.Version {
	case 1:
		var raw orderPlacedV1
		if err := json.Unmarshal(s.Data, &raw); err != nil {
			return OrderPlaced{}, ErrCorruptEvent
		}
		id, err := NewOrderID(raw.OrderID)
		if err != nil {
			return OrderPlaced{}, err
		}
		// Model decision: the app launched together with version 2, so every earlier order came from the web.
		return OrderPlaced{OrderID: id, Channel: ChannelWeb}, nil
	case 2:
		var raw orderPlacedV2
		if err := json.Unmarshal(s.Data, &raw); err != nil {
			return OrderPlaced{}, ErrCorruptEvent
		}
		id, err := NewOrderID(raw.OrderID)
		if err != nil {
			return OrderPlaced{}, err
		}
		channel, err := parseChannel(raw.Channel)
		if err != nil {
			return OrderPlaced{}, err
		}
		return OrderPlaced{OrderID: id, Channel: channel}, nil
	}
	return OrderPlaced{}, fmt.Errorf("%w: %s version %d", ErrUnknownEvent, s.Type, s.Version)
}
```
