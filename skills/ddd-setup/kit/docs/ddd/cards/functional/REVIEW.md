# Reviewing code written with these cards

`ddd-review` checks code against the domain model and has no opinion on how the code is written. This file is the cards' own checklist. A reviewer applies it after its own checklist when the repository has this file, and tags these findings `[cards]`. For `secure-by-design-review` it is the sign that domain values are typed here, so its items on primitives apply as written.

Read the cards for the patterns the change uses, with each card's **Corrections** section, and the language README and examples only if installed. Do not load cards the change does not touch.

## Ways around the types

Search the diff and judge each one:

- Go: `default:` in a type switch or enum switch, `//nolint`, `interface{}` or `any` in domain code, `panic(` outside "cannot happen" branches
- TypeScript: ` as ` casts, `any`, `eslint-disable`, `@ts-ignore`, `@ts-expect-error`, non-null `!`, `throw` in domain code

## States and decisions

- One type per state. No status field with optional or nullable fields.
- Decision functions are pure: no I/O, no clock, no randomness, no hidden globals. A repository, client or callback passed into a decision function is I/O in disguise; outside data arrives as a value (card 13).
- A per-state decision function takes the specific state type and never checks the state at runtime. If it does, its parameter type is too wide.
- A command legal in several states takes exactly those states, not the whole sum type.
- Narrowing from the whole sum type happens in exactly one place per command: the workflow, or the `decide` function of a decider (card 11). `decide` checking the state is therefore correct, provided the business rule itself sits in a per-state function it dispatches to.
- "Wrong state" is a failure of that narrowing step, never of a per-state decision function.
- Switches over sum types list every variant.

## Immutability

- No setters or mutating methods on domain types.
- Go: slices and maps are cloned on the way in and out; value receivers.
- TypeScript: `readonly` on fields and arrays.

## Layering

- The domain does not import HTTP, JSON, database or framework packages.
- Repository and adapter contracts are declared in the domain, in domain types, and implemented outside it.
- Workflows only orchestrate: load, narrow, decide, persist, publish.

## Failures

- Expected business failures are returned as named values, in domain types. Exceptions and panics are for bugs.
- Domain errors and infrastructure errors are kept apart.

## Tests

- Each aggregate has a property test that runs random command sequences and asserts the model's invariants after every step, unless the ticket under review defers it to another ticket. Read its generator: a sequence that never reaches a limit, or never leaves the first state, proves nothing about what lies beyond.
- Tests of pure decision functions need no test doubles: needing one means I/O has leaked into that function.

## Break-it

In the reviewer's break-it pass, an illegal transition, a state built without its required data, a new state or event, and a mutation after creation are expected to fail at **compile** or **lint**. One that is only refused at run time is a finding, unless the model's "enforced by" column says a constructor or decision function enforces it. Some attempts cannot be stopped by the language, such as a TypeScript object literal for an unbranded state type: report these as known limits, with what compensates for them, not as blockers.

## Feeding the cards

If a finding is a pattern mistake likely to recur, suggest a one-line addition to the **Corrections** section of the relevant card.
