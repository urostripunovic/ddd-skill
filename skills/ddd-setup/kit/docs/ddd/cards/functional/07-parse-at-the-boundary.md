# Parse at the boundary

**Use when:** data enters the domain from outside: HTTP body, queue message, database row, config file, another service's response.

**Never:** let a DTO, `map[string]any`, `unknown` or `any` reach a domain function. Never validate inside the domain what should have been parsed at the edge.

## Rules

- The boundary turns untrusted input into domain types or rejects it. Inside the domain, values are trusted because their types prove they were parsed.
- Check in this order, cheapest first (Secure by Design):
  1. **Origin**: is the sender allowed to send this?
  2. **Size**: is it within the limit? Checked before any parsing.
  3. **Lexical content**: only allowed characters and encoding?
  4. **Syntax**: does it have the right format?
  5. **Semantics**: does it make sense in the domain (does the order exist, is the date in the future)?
- Reject unknown fields in requests from outside the system. Do not try to repair bad input.
- A message from another context, such as an event or a response, may gain fields its consumer does not read yet. Ignore unknown fields there, so the upstream can add one without breaking its consumers; a missing or invalid field the consumer reads is still rejected. An unknown event type or version is an error ([event versioning](20-event-versioning.md)).
- Database rows are also outside. Loading from storage goes through the same constructors.

## Enforced by

- Go: a separate boundary package holds the DTOs; domain packages do not import `encoding/json` or `net/http`.
- TypeScript: types do not exist at runtime, so every boundary needs a parser from `unknown`. A schema library such as Zod is fine if its output is mapped to branded types.

## Anti-pattern

```ts
const order = (await req.json()) as Order;
```

Examples: [Go](go/07-parse-at-the-boundary.md) · [TypeScript](ts/07-parse-at-the-boundary.md). Read only the one for your language.

## Corrections

<!-- Add a dated line each time an agent gets this pattern wrong. -->
