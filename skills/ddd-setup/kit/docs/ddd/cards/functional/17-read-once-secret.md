# Read-once secret

**Use when:** a value is marked sensitive in the model and must be used exactly once: a password, an API key, a one-time token.

**Never:** keep a secret in a `string` field, a plain domain primitive, an event or an error. Any of those can be logged, serialised or compared by accident.

## Rules

- The value can be read once. A second read fails, which makes an unintended use visible in tests instead of silent in production.
- It prints as a placeholder everywhere: string conversion, debug formatting and structured logging.
- It cannot be serialised. Serialising is an error, not a placeholder, so a secret never ends up stored as the text "[secret]".
- It has bounds like any primitive, checked when it is created.
- This is the one deliberately mutable domain type, because "already read" is state. It is therefore never part of an aggregate or an event; a workflow receives it and hands it to the adapter that needs it.
- Personal data that is read many times (an email address) is not this pattern. Mark it sensitive in the model and keep it out of events, errors and logs.

## Enforced by

- Go: unexported fields and a pointer type; `String`, `GoString`, `LogValue` and `MarshalJSON` are overridden.
- TypeScript: the value lives in a closure, so no property holds it; `toString` and `toJSON` are overridden.

## Anti-pattern

```go
type Credentials struct {
	Username string
	Password string // logged by the first fmt.Printf("%+v", creds)
}
```

## Example

One file per language: [Go](go/17-read-once-secret.md), [TypeScript](ts/17-read-once-secret.md). Read only the one for the language you are writing.

## Corrections

<!-- Add a dated line each time an agent gets this pattern wrong. -->
