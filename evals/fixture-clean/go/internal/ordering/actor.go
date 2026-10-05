package ordering

import (
	"context"
	"errors"
)

var (
	ErrNotAuthenticated = errors.New("not authenticated")
	ErrNotAllowed       = errors.New("not allowed")
)

// What a verified credential says about its bearer.
type Claims struct {
	Customer CustomerEmail
}

// Implemented by the adapter that holds the request. It returns claims only
// for a credential it has checked.
type VerifyCredential func(ctx context.Context) (Claims, error)

//sumtype:decl
type Actor interface{ isActor() }

// Unexported, so no other package can build an actor without Authenticate.
type customer struct{ email CustomerEmail }

func (customer) isActor() {}

// fmt reads unexported fields by reflection without calling their String
// methods, so without these a formatted actor prints the customer's email.
func (customer) String() string   { return "customer" }
func (customer) GoString() string { return "customer" }

func Authenticate(ctx context.Context, verify VerifyCredential) (Actor, error) {
	claims, err := verify(ctx)
	if err != nil || claims.Customer.IsZero() {
		// Not wrapped: the adapter's error may describe the credential.
		return nil, ErrNotAuthenticated
	}
	return customer{email: claims.Customer}, nil
}

// "Any signed-in customer": the new order belongs to whoever starts it.
func MayStartOrder(a Actor) (CustomerEmail, bool) {
	switch a := a.(type) {
	case customer:
		return a.email, true
	}
	// A nil Actor: nobody was authenticated.
	return CustomerEmail{}, false
}

// The model gives AddItem, PlaceOrder and CancelOrder the same rule: the customer who owns the order.
func MayChangeOrder(a Actor, o Order) bool {
	switch a := a.(type) {
	case customer:
		return a.email == o.Customer()
	}
	return false
}
