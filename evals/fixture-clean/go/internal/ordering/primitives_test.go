package ordering

import (
	"encoding/json"
	"errors"
	"fmt"
	"strings"
	"testing"
)

func TestQuantityBounds(t *testing.T) {
	for _, tc := range []struct {
		in    int
		valid bool
	}{{-1, false}, {0, false}, {1, true}, {1000, true}, {1001, false}, {1 << 40, false}} {
		q, err := NewQuantity(tc.in)
		if tc.valid && (err != nil || q.Int() != tc.in) {
			t.Errorf("NewQuantity(%d) = %v, %v; want it accepted", tc.in, q, err)
		}
		if !tc.valid && !errors.Is(err, ErrInvalidQuantity) {
			t.Errorf("NewQuantity(%d) = %v; want ErrInvalidQuantity", tc.in, err)
		}
	}
}

func TestPriceBounds(t *testing.T) {
	for _, tc := range []struct {
		in    int64
		valid bool
	}{{-1, false}, {0, true}, {100_000_000, true}, {100_000_001, false}} {
		_, err := NewPrice(tc.in)
		if (err == nil) != tc.valid {
			t.Errorf("NewPrice(%d) error = %v; valid = %v", tc.in, err, tc.valid)
		}
	}
}

func TestSKU(t *testing.T) {
	for _, tc := range []struct {
		name  string
		in    string
		valid bool
	}{
		{"shortest", "AB1", true},
		{"longest", strings.Repeat("A", 32), true},
		{"with hyphen", "ABC-1", true},
		{"too short", "AB", false},
		{"too long", strings.Repeat("A", 33), false},
		{"empty", "", false},
		{"lower case is not repaired", "abc-1", false},
		{"surrounding space is not trimmed", " ABC-1 ", false},
		{"query fragment", "ABC&key=1", false},
		{"markup", "<b>ABC</b>", false},
		{"non-ASCII letter", "ÅBC-1", false},
		{"far too large", strings.Repeat("A", 1<<20), false},
	} {
		t.Run(tc.name, func(t *testing.T) {
			_, err := NewSKU(tc.in)
			if (err == nil) != tc.valid {
				t.Fatalf("error = %v; valid = %v", err, tc.valid)
			}
			if err != nil && len(tc.in) > 0 && strings.Contains(err.Error(), tc.in) {
				t.Fatal("the error repeats the rejected input")
			}
		})
	}
}

func TestOrderID(t *testing.T) {
	const good = "123e4567-e89b-12d3-a456-426614174000"
	for _, tc := range []struct {
		name  string
		in    string
		valid bool
	}{
		{"uuid", good, true},
		{"one short", good[:35], false},
		{"one long", good + "0", false},
		{"upper case", strings.ToUpper(good), false},
		{"right length, wrong shape", strings.Repeat("-", 36), false},
		{"empty", "", false},
		{"far too large", strings.Repeat("a", 1<<20), false},
	} {
		t.Run(tc.name, func(t *testing.T) {
			if _, err := NewOrderID(tc.in); (err == nil) != tc.valid {
				t.Fatalf("error = %v; valid = %v", err, tc.valid)
			}
		})
	}
}

func TestCustomerEmail(t *testing.T) {
	longest := strings.Repeat("a", 242) + "@example.com"
	for _, tc := range []struct {
		name  string
		in    string
		valid bool
	}{
		{"ordinary", "a@example.com", true},
		{"254 characters", longest, true},
		{"255 characters", "a" + longest, false},
		{"no @", "example.com", false},
		{"two @", "a@b@example.com", false},
		{"empty", "", false},
		{"far too large", strings.Repeat("a", 1<<20) + "@example.com", false},
	} {
		t.Run(tc.name, func(t *testing.T) {
			if _, err := NewCustomerEmail(tc.in); (err == nil) != tc.valid {
				t.Fatalf("error = %v; valid = %v", err, tc.valid)
			}
		})
	}
}

func TestCustomerEmailIsNeverPrinted(t *testing.T) {
	const raw = "private@example.com"
	email, err := NewCustomerEmail(raw)
	if err != nil {
		t.Fatal(err)
	}
	order := StartOrder(OrderID{v: "123e4567-e89b-12d3-a456-426614174000"}, email)
	encoded, err := json.Marshal(email)
	if err != nil {
		t.Fatal(err)
	}
	for _, printed := range []string{
		fmt.Sprint(email), fmt.Sprintf("%v", email), fmt.Sprintf("%+v", email), fmt.Sprintf("%#v", email),
		fmt.Sprintf("%+v", order), fmt.Sprintf("%#v", order), string(encoded),
	} {
		if strings.Contains(printed, "private") {
			t.Errorf("the address leaked: %s", printed)
		}
	}
	if email.Reveal() != raw {
		t.Error("Reveal does not return the address")
	}
}

func TestCancellationReason(t *testing.T) {
	for _, tc := range []struct {
		name  string
		in    string
		valid bool
	}{
		{"one character", "x", true},
		{"200 characters", strings.Repeat("x", 200), true},
		{"200 characters of several bytes each", strings.Repeat("å", 200), true},
		{"201 characters", strings.Repeat("x", 201), false},
		{"201 characters of several bytes each", strings.Repeat("å", 201), false},
		{"empty", "", false},
		{"not valid UTF-8", "\xff\xfe", false},
		{"far too large", strings.Repeat("x", 1<<20), false},
	} {
		t.Run(tc.name, func(t *testing.T) {
			if _, err := NewCancellationReason(tc.in); (err == nil) != tc.valid {
				t.Fatalf("error = %v; valid = %v", err, tc.valid)
			}
		})
	}
}

func TestZeroValuesAreDetectable(t *testing.T) {
	if !(OrderID{}).IsZero() || !(SKU{}).IsZero() || !(Quantity{}).IsZero() || !(CustomerEmail{}).IsZero() || !(CancellationReason{}).IsZero() {
		t.Fatal("a zero value that skipped its constructor is not detectable")
	}
}
