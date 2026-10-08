---
name: secure-by-design-review
description: "Security review of code using the Secure by Design approach: domain primitives and bounds, validation order, sensitive data, failures, test coverage, and when relevant timeouts, secrets and logging. Use for any security-focused code review, in a fresh session."
disable-model-invocation: true
---

# Secure by Design review

Answer one question: does the design of this code make it hard to misuse? Report findings. Do not change the code unless the user asks.

Run this in a session that did not write the code. If you wrote the code under review in this session, say so at the top of the report.

## About the checklist

The items follow the structure of *Secure by Design* (Bergh Johnsson, Deogun, Sawano; Manning, 2019). `[SbD n]` after an item is the chapter it comes from, so a finding can cite it and the user can look it up. The wording is this skill's own, adapted from the book's class-based Java style to typed Go and TypeScript: where the book says entity, builder or setter, read state type, constructor or decision function.

## Scope

This skill does not check whether the code matches the domain model, whether states are modelled as types, whether transitions are legal, whether data is immutable, or whether each model failure and command has its test. Those belong to `ddd-review`. Do not report findings in those areas; the other review will.

This skill owns: the rules and bounds of domain primitives, constructor bypass, input at the boundary, sensitive data, authorisation, what errors carry, and boundary, invalid and extreme-input tests.

This review covers design and code. It does not replace dependency scanning, penetration testing or an incident process. [SbD 14]

## Pin what is reviewed

Follow [review-range.md](../ddd-modelling/lifecycle/review-range.md).

## Inputs

1. The pinned diff.
2. From `docs/domain/contexts/<context>.md`, if it exists: primitive rules, bounds, sensitivity, permitted issuers, outside-fact trust rules and amendments affecting those entries. Use an amendment's updated rule when comparing code; report conflicts rather than silently picking the older text.
3. Cards only if you need the reference form of a pattern, with the example from the directory of the language under review: 01 domain primitive, 02 value object, 07 parse at the boundary, 10 errors as values, 14 authorisation, 17 read-once secret.

Without a model you can still run this review. Say in the report that bounds and sensitivity were judged from the code alone.

## Decide what applies

Read the change first and decide which conditional sections it touches. Apply the core checklist, adapted to the setup choice below, and a conditional section only when the change touches that area. Name the skipped sections in the report.

**Code style.** Resolve it as [code-style.md](../ddd-modelling/lifecycle/code-style.md) says, and do not ask again. In model-only projects, check the security outcomes: validation before use, bounds, verified identity, authorisation, safe errors and sensitive-data handling. Do not require wrapper types, constructor-only creation, ORM-free domain types, or read-once wrappers solely to match the cards. Test bypass of the project's actual validation and authorisation boundaries. Other languages use their own tooling and idioms. A missing typed pattern alone is not a security finding.

## Core checklist

### Domain primitives

- No raw `string`, `int` or `number` crosses a domain function boundary. [SbD 5]
- Each primitive can only be created through a validating constructor or parser. [SbD 5]
- Bounds include an upper limit, and strings have a length limit and an allowed character set or format. [SbD 4, 5]
- A primitive's rules belong to one context. The same word in another context is another type with its own rules. [SbD 5]
- A primitive is a conceptual whole. An amount without its currency, or a measurement without its unit, is half a primitive. The missing half must not come from surrounding context or a default. [SbD 12]
- Money is never a float. [SbD 12]
- A function with several parameters of the same raw type (`string`, `int`, `number`) is a finding: the arguments can be swapped without any error. Two parameters of the same domain type are a finding only when swapping them is easy and changes the outcome without an error, such as `Transfer(from, to AccountID)`; there, a type per role or a value object (`DateRange`) fixes it. [SbD 12]
- Go: is each primitive's zero value either meaningful or detectably invalid, such as by an `IsZero` method? A zero value that is neither is a finding. A decision function that does not re-check a detectable zero value is not. A state type's zero value (`PlacedOrder{}` written in another package) is a limit of the language: note it once, not as a finding.
- TypeScript: is the brand applied only inside the parser?

### Valid from creation

- Every value is complete and valid from the moment it exists. No half-built value that is filled in later, and nothing that needs an `init` or `validate` call after creation. [SbD 6]
- Rules that span several fields are checked when the value is created, not left to callers. [SbD 6]
- Preconditions are checked first, before any work is done. [SbD 4]
- Persistence and serialisation do not bypass constructors. A decoder or ORM writing straight into a domain type is a finding. Go: struct tags such as `json` or `db` on a domain type are the signal. [SbD 6]
- Domain code that re-checks what a type should guarantee, such as repeated nil, empty or range checks deep inside the domain, means a primitive is missing upstream. Report the missing type, not the check. [SbD 12]

### Input at the boundary

- All external input is parsed into domain types before reaching the domain, including database rows and other services' responses. [SbD 4, 5]
- Validation order is origin, size, lexical content, syntax, semantics. Size is checked before any expensive parsing or regex. [SbD 4]
- Parsers that expand their input (XML entities, archives, deeply nested JSON) have explicit limits configured. [SbD 1]
- Bad input is rejected, never repaired. No trimming, stripping or "fixing" before validation. [SbD 9]
- Rejected input is never echoed back verbatim in a response, error or log line. [SbD 9]
- Unknown enum or status values are rejected, not defaulted. Unknown fields are rejected in requests from outside the system; in a message from another context, ignoring a field the consumer does not read is correct.
- Domain types are not the public API. Requests, responses, messages and database rows have their own types, mapped at the boundary. [SbD 5, 13]

### Sensitive data

- Secrets and personal data are not in events, errors, logs, or string representations (`String()`, `toString`, `toJSON`). [SbD 5, 9]
- A secret is a read-once value: it can be read a single time, cannot be serialised, and prints as a placeholder. A second read is an error, which makes accidental use visible. [SbD 5]
- Logging a whole object or struct is a finding, even when it holds nothing sensitive today. A field added later would leak without anyone touching the log line. [SbD 5, 12]
- Strings that have not been parsed are not logged. [SbD 12]
- Data that is harmless alone can become sensitive when combined. Check what a new event, response or log line adds to what is already exposed. [SbD 13]

### Authorisation

- For each command the change touches: who may issue it, on whose data, and where in the code is that checked?
- The check uses the caller's verified identity, not an identifier taken from the request body.
- The value that stands for the caller can only come from the code that verified the credential. If any other code can build one (an exported constructor, an object literal), the check can be satisfied without a credential.

### Failures

- Error values and exception payloads carry no input data and no sensitive data. [SbD 9]
- Error messages shown to users do not leak internals, and unknown errors map to a fixed message. [SbD 9]

### Tests

Agents usually test valid input and stop. For each primitive and each boundary parser, look for the three kinds that probe misuse. Tests of normal behaviour per command belong to `ddd-review`. [SbD 8]

- **Boundary**: the lowest and highest valid values, and one outside each.
- **Invalid**: wrong type, wrong format, empty, null, and input that is harmless here but harmful later, such as markup or query fragments that another system would interpret.
- **Extreme**: input far outside any realistic size, to confirm it is rejected cheaply and does not exhaust memory or time.

A test suite that only covers the happy path is a finding in its own right. [SbD 12]

## Conditional checklist

### Calls to other systems

- Every outbound call has an explicit timeout. [SbD 9]
- A failing dependency cannot take the whole service down: failures are contained, and repeated failures stop further calls for a while. [SbD 9]
- Work that the domain rules make expensive is limited per caller, so the business rules cannot be used to exhaust the service. [SbD 8]

### Configuration and secrets

- Environment-specific configuration is not in code. [SbD 10]
- No secret is in the repository, a resource file, a default value or a test fixture. [SbD 10]
- Configuration is parsed into typed values at start-up, and the service refuses to start on a missing or invalid value.
- Security-relevant defaults of frameworks and libraries are known and covered by a test, not assumed. [SbD 8]
- A feature toggle has tests for both positions, and a toggle that guards a security-relevant path is treated as one. [SbD 8]

### Logging

- Logs go to the platform's log stream, not to a file the service manages. [SbD 10]
- Log calls take domain types and let the logger decide what is safe to write, not pre-formatted strings. [SbD 13]
- Requests can be traced across services with a correlation identifier that is not itself sensitive. [SbD 13]

### Service boundaries

- A change to the meaning of a field in a published API or event is a breaking change, even when its type is unchanged. [SbD 13]
- Admin and maintenance operations go through the same authorisation and audit as ordinary commands. [SbD 10]

### Dependencies

- List any dependency added or upgraded in the change, so the user can decide whether it needs its own look. [SbD 14]

## Abuse attempts

For the primitives and commands the change touches, try a few misuses and record what stopped each one.

Run each attempt, clean up and record its outcome as [break-it.md](../ddd-modelling/lifecycle/break-it.md) says. **test** does not apply here.

| Attempt | Example |
|---|---|
| Primitive outside its bounds | quantity 0, quantity above the maximum, a string one character too long |
| Skip a constructor | struct or object literal, Go zero value, TypeScript cast, decoding straight into a domain type |
| Forge the caller | build the actor a workflow expects without verifying a credential |
| Print a sensitive value | format a state or event that holds one with `%+v`, `%#v`, `JSON.stringify` or string interpolation |
| Swap arguments | pass two same-typed arguments in the wrong order |
| Business-logic abuse | a negative quantity, a zero price, the same discount twice |
| Unknown external value | a status string the adapter has never seen |
| Oversized input | a body or field far beyond the limit |

## Report

Open and close the report as [review-range.md](../ddd-modelling/lifecycle/review-range.md) says. Between the verdict and the end come the findings, most severe first. For each one:

- location as `file:line`
- the rule it breaks, with its `[SbD n]` reference when it has one
- severity: **blocker** (sensitive data exposed, input reaches the domain unparsed, missing authorisation, abuse attempt not prevented), **should fix**, or **note**
- a concrete fix; show code changes as a diff

Then the abuse-attempt table.

What was not checked includes conditional sections skipped, steps you could not run, and that model conformance was not reviewed here.
