# Go

How the kit's patterns are written in Go. Read this once before writing Go domain code, then the example files in this directory for the cards the task needs.

## Idioms

- Domain primitive: struct with an unexported field and a `New...` constructor returning `(T, error)`.
- The zero value bypasses the constructor. Make it either meaningful or detectably invalid.
- State types have unexported fields and accessors, so only the domain package can build a state with contents. Another package can still write the zero value (`PlacedOrder{}`); Go cannot prevent that.
- `fmt` prints unexported fields by reflection and does not call their `String` methods. A state that holds a sensitive value needs its own `String` and `GoString`, or `%+v` of the state prints the value.
- Sum type: sealed interface with an unexported marker method and `//sumtype:decl` above it.
- Enum: named constants starting at `iota + 1`, so zero is not a real value.
- Plain `(T, error)` returns, `errors.Is` and `errors.As`. No Result types, no pipeline combinators.
- Immutability is by convention: value receivers, no setters, clone slices and maps on the way in and out.

## Checks

- Compile: `go build ./...` and `go vet ./...`
- Lint: `golangci-lint run`, with the rules of `tools/lint/.golangci.yml` in the repository's config: exhaustive sum types; no infrastructure imports, clock, randomness or logging in the domain packages; every `//nolint` explained.
- Property tests: `pgregory.net/rapid` if the repository has it.

## Never, to make a check pass

- `default:` in a type switch or enum switch over a sum type
- `//nolint`
- `interface{}` or `any` in domain code
