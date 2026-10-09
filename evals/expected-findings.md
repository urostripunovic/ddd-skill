# Expected findings for the seeded fixture

The head commit of the seeded fixture repository (`make-fixture-repo.sh <dir> seeded`) contains these seeded violations. A reviewer run is scored by how many it reports, and by whether it flags either control. For the clean fixture, see the end of this file.

Score a seeded violation as **caught** when the report names the same problem at the same place, in any wording. Severity is not scored.

## ddd-review

| ID | Where | Seeded violation |
|---|---|---|
| D1 | `docs/domain/contexts/ordering.md` | Model changed without a new approval: the range edits the Quantity bound and leaves the Status line as it was |
| D2 | `internal/ordering/order.go` | `SubmittedOrder` is not the model's name; the model says `PlacedOrder` |
| D3 | `internal/ordering/order.go` | No `CancelledOrder` type: cancellation is a `Cancelled` flag and an optional reason on another state |
| D4 | `internal/ordering/order.go` `Place` | Reads the clock (`time.Now`) inside a decision function |
| D5 | `internal/ordering/order.go` `Place`, `internal/httpapi/handler.go` | Invariant 1 (placed order has a line) is not enforced by `Place`; the rule sits in the HTTP handler |
| D6 | `internal/ordering/order.go` `Cancel` | Takes the whole `Order` and checks the state at runtime; returns a wrong-state failure from a decision function |
| D7 | `internal/ordering/order.go` `Cancel` | A draft order cannot be cancelled, but the model says it can |
| D8 | `internal/ordering/order.go` `Cancel` | `default:` in a type switch over a sum type; the lint fails |
| D9 | `internal/ordering/order.go` `Load` | The domain package imports `database/sql` and does its own persistence |
| D10 | `internal/ordering/order.go` `AddItem`, `Place` | Slices are shared instead of cloned |
| D11 | `internal/ordering/order.go` | The command `StartOrder`, the events `OrderPlaced` and `OrderCancelled`, and the failures `EmptyOrder`, `QuoteExpired` and `TooManyItems` from the model do not exist in code; the 100-item limit (invariant 6) is not enforced |
| D12 | `internal/ordering/order_test.go` | Of the model's ten examples only the plain `PlaceOrder` one has a test; nothing covers a failure or `Cancel`, and no race has a workflow test |
| D13 | `src/ordering/order.ts` | One `Order` type with a status field and optional fields |
| D14 | `src/ordering/order.ts` `addItem`, `place` | Mutation of the order; no `readonly` |
| D15 | `src/ordering/order.ts` `place` | Runtime state check, `throw` for business outcomes, and `new Date()` in the decision |
| D16 | `src/ordering/order.ts` `describe` | `default` swallows states, and the exhaustiveness rule is disabled with a comment |
| D17 | `internal/ordering/order_test.go` | No property test over command sequences for the Order aggregate |

## secure-by-design-review

| ID | Where | Seeded violation |
|---|---|---|
| S1 | `internal/ordering/order.go` `NewQuantity` | No upper bound; the model says 1..1000 |
| S2 | `internal/ordering/order.go` `NewSKU` | The regex runs before the length check |
| S3 | `internal/ordering/order.go` `NewSKU`, `internal/httpapi/handler.go` | Rejected input is echoed in the error, and `err.Error()` is returned to the client |
| S4 | `internal/ordering/order.go` `AddItem`, `Cancel`, `DraftOrder` | Raw `string`, `int` and `float64` cross domain function boundaries; `CustomerEmail` and the cancellation reason are plain strings |
| S5 | `internal/ordering/order.go` `Item`, `internal/pricing/client.go`, `src/ordering/order.ts` | Money as a float |
| S6 | `internal/ordering/order.go` `Place` | Logs the whole order with `%+v`, including the customer's email |
| S7 | `internal/ordering/order.go` `SubmittedOrder`, `internal/httpapi/handler.go` | JSON tags on a domain type, and the domain type is encoded straight into the response |
| S8 | `internal/httpapi/handler.go` | Request body decoded with no size limit, and unknown fields are accepted |
| S9 | `internal/httpapi/handler.go` | No authorisation: nothing checks that the caller owns the order |
| S10 | `internal/pricing/client.go` | Outbound call with no timeout |
| S11 | `internal/pricing/client.go` | Secret in source code, and sent in the URL |
| S12 | `internal/ordering/order_test.go` | Only valid input is tested: no boundary, invalid or extreme cases |
| S13 | `src/ordering/order.ts` `parseSku` | Input is repaired (trimmed, upper-cased) before validation |
| S14 | `src/ordering/order.ts` `parseSku` | Throws for bad input and echoes the raw value |
| S15 | `src/http/handler.ts` | `any` request body, the brand is cast outside the parser, and quantity and price are never parsed |
| S16 | `src/http/handler.ts` | Logs the whole request body |

The linters now report some of these on their own: D4, D8 and D9, the logging in S6, and the `throw` and `new Date()` in D15. A seed still counts as caught only when the reviewer's report names it.

## Controls: must not be reported

| ID | Where | Why it is correct |
|---|---|---|
| C1 | `internal/ordering/order.go` `NewOrderID` | Length is checked before the regex, and the error does not echo the input |
| C2 | `src/ordering/order.ts` `parseSku`, the `as Sku` line | The one permitted cast: inside the parser, with a comment. The other problems in `parseSku` are seeded; the cast itself is not one |

## The clean fixtures

`make-fixture-repo.sh <dir> clean` builds the same base commit, and a head commit with a Go implementation that follows the model: `internal/ordering` (primitives, states, decisions, actor, repository contract) and `internal/app` (one function per use case), with tests for every bound, every example, every race, and a property test. `tools/check-model.sh`, `go vet`, `go test` and `golangci-lint` all pass on it.

Neither has seeds. Score a run by what it reports:

- every **blocker** and every **should fix** is a candidate false positive
- look at each one: if it is a real problem in the fixture, fix the fixture and note it in the results; if it is not, it counts against the reviewer, and the skill needs a change
- **notes** are not scored

`make-fixture-repo.sh <dir> clean-ts` builds the same thing in TypeScript, in a repository with no Go: `src/ordering` (primitives, states, decisions, actor, repository contract), `src/app` (one function per use case) and `test/`, with the same tests. `tools/check-model.sh`, `tsc`, ESLint with the domain rules on `src/ordering`, and `npm test` all pass on it.

Known and deliberate, so not a finding:

- Go: state types can be written as zero values from another package (`ordering.DraftOrder{}` in `internal/app`), which the kit names as a limit of the language.
- Go: decision functions do not re-check primitives for zero values. Each primitive's zero value is either detectable (`IsZero`, tested in `TestZeroValuesAreDetectable`) or meaningful (a zero `Price` is nothing to pay), which is what card 01 and `secure-by-design-review` ask for.
- TypeScript: a state or an event is a plain object type, so any code can write one as an object literal (`{ kind: "placed", ... }`) without going through a decision function. The primitives inside it still have to come from their parsers. The kit names this as a limit of the language.
- TypeScript: times are a `Timestamp` primitive (milliseconds since the epoch) and not a `Date` as in the cards, because a `Date` can be changed by whoever holds it. The tests are in `test/` and not beside the code, because the domain lint rules apply to every file under `src/ordering` and a test needs `node:test`.
- TypeScript: `Actor` has one variant, so the two authorisation functions do not switch on its kind.
- Both: there is no HTTP layer, no storage implementation and no pricing adapter, so nothing can be said about those.
