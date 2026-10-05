# Authorisation: Go

The rules are in [the card](../14-authorisation.md).

```go
package ordering

import (
	"context"
	"errors"
	"fmt"
)

var (
	ErrNotAuthenticated = errors.New("not authenticated")
	ErrNotAllowed       = errors.New("not allowed")
)

type CustomerID struct{ v string }

func (id CustomerID) String() string { return id.v }

type OrderID struct{ v string }

func (id OrderID) String() string { return id.v }

// What a verified credential says about its bearer.
type Claims struct {
	Subject CustomerID
	Support bool
}

// Implemented by the adapter that holds the request. It returns claims only
// for a credential it has checked: a signature, a session lookup.
type VerifyCredential func(ctx context.Context) (Claims, error)

//sumtype:decl
type Actor interface{ isActor() }

// Unexported, so no other package can build an actor without Authenticate.
type customer struct{ id CustomerID }
type supportAgent struct{}

func (customer) isActor()     {}
func (supportAgent) isActor() {}

func Authenticate(ctx context.Context, verify VerifyCredential) (Actor, error) {
	claims, err := verify(ctx)
	if err != nil {
		// Not wrapped: the adapter's error may describe the credential.
		return nil, ErrNotAuthenticated
	}
	if claims.Support {
		return supportAgent{}, nil
	}
	return customer{id: claims.Subject}, nil
}

type DraftOrder struct {
	id    OrderID
	owner CustomerID
}

func (o DraftOrder) ID() OrderID { return o.id }

// The model's "Issued by" rule for CancelOrder.
func MayCancel(a Actor, o DraftOrder) bool {
	switch a := a.(type) {
	case customer:
		return a.id == o.owner
	case supportAgent:
		return true
	}
	// A nil Actor: nobody was authenticated, so nothing is allowed.
	return false
}

type CancelOrderDeps struct {
	LoadDraft     func(ctx context.Context, id OrderID) (DraftOrder, error)
	SaveCancelled func(ctx context.Context, id OrderID) error
}

func CancelOrder(ctx context.Context, deps CancelOrderDeps, actor Actor, id OrderID) error {
	draft, err := deps.LoadDraft(ctx, id)
	if err != nil {
		return fmt.Errorf("load order: %w", err)
	}
	// After loading, because the rule depends on the owner; before any decision or write.
	if !MayCancel(actor, draft) {
		return ErrNotAllowed
	}
	if err := deps.SaveCancelled(ctx, draft.ID()); err != nil {
		return fmt.Errorf("save cancelled order: %w", err)
	}
	return nil
}
```
