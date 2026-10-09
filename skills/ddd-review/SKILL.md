---
name: ddd-review
description: "Review code against the approved domain model: every model element traced to code and tests, glossary names, legal transitions, context boundaries, plus a break-it pass. Use after implementing domain or business-logic code, in a fresh session. Security is covered by secure-by-design-review."
disable-model-invocation: true
---

# DDD review

Answer one question: does this code implement the approved domain model? Review what the code does, not how it is written: classes or functions, exceptions or values, a type or a run-time check are the project's business, and none is a finding here. Report findings. Do not change the code unless the user asks.

Run this in a session that did not write the code. An author reviewing its own work tends to approve it. If you wrote the code under review in this session, say so at the top of the report.

## Scope

This skill checks the code against the model. It does not check:

- whether the model itself is right: `ddd-model-review`
- whether the change does what the task asked: `task-review`
- security: `secure-by-design-review` owns the rules and bounds of domain primitives, constructor bypass, input parsing, sensitive data, what errors carry, boundary and invalid-input tests, timeouts, secrets and logging

Do not load or apply those checklists here, and do not report findings in those areas; the other review will. If you notice a serious security problem in passing, mention it in one line under notes.

## One part at a time

If the user names a part (`/ddd-review PlaceOrder`, `/ddd-review the Order aggregate`, `/ddd-review step 3`), review only that part of the pinned diff: the command or aggregate, the files that implement it, and the model rows that name it. The tracing tables and the break-it pass cover that part only. Say at the top what was left out.

For a diff that touches more than about six commands, propose going through it in the order of the model's `## The flow`, one step at a time, before reviewing all of it at once.

## Pin what is reviewed

Follow [review-range.md](../ddd-modelling/lifecycle/review-range.md). In a re-review, do not fill the tracing tables again either.

## Inputs

1. The pinned diff.
   If an original task or ticket is supplied, read its scope and explicitly deferred work so this review uses the same completion boundary. Full requirement-by-requirement task review remains `task-review`'s job.
2. The model: the glossary (`GLOSSARY.md` at the root, or the ones `GLOSSARY-MAP.md` links to), `docs/domain/context-map.md`, and only the `docs/domain/contexts/<context>.md` files the change touches.
3. `docs/ddd/cards/functional/REVIEW.md`, if the repository has it and its agent instructions do not say the code style is the repository's own. It is the checklist of the pattern cards the repository installed: apply it after this file's checklist, as it says, and tag its findings `[cards]`. Without that file, skip this.

If there is no model for the code under review, stop and say so. Without it this review has nothing to compare the code with.

## Check the approval

For each context file you use, read its `Status:` line.

- Not approved (`draft`, or `derived from code, not confirmed`): say so at the top of the report. You can still review, but every "matches the model" finding is provisional.
- Approved: run `tools/check-model.sh <file>`. A problem it reports is a blocker; name the file. Then look at what the pinned range did to the file: `git diff <base>...HEAD -- <file>`. Rows changed above the notes tail while the Status line stayed as it was mean the model changed without being approved again: a blocker, with the changed rows quoted. The user approves the change or reverts it before the review result means anything.

Rows under the context file's `## Amendments` are part of the model for this review: where a row says what the code does, trace the code against the row and not against the text it amends. Code that matches neither is a finding. An element marked `(assumed)` is traced like any other.

An amendment inside a strict scope (as `tools/check-model.sh` prints it), or in a context at strict depth, should have been a `## Pending` row and a reapproval, so it is a finding. A missing `Depth:` means strict. Depth does not relax conformance to rules already written. Flag a changed glossary definition or context-map relationship that changes an approved rule's meaning; the Status line does not cover them.

## Mechanical checks

Run these first. They are cheap and they are where agents cut corners.

- Compile, lint and tests, with the project's own commands.
- Search the diff for checks switched off in passing (a lint or type-check suppression comment, a skipped test) and judge each one.
- Check that lint configs were not loosened in the same change: a rule removed, a domain path narrowed so the domain rules no longer reach the code, a test exemption widened.

## Trace the model to the code

Fill in two tables before the checklist. A sentence saying "everything in the model is in the code" can be written without looking; a row per element cannot.

**Model to code.** One row for every state, command, event, failure, use-case failure, primitive, invariant, example and race in the context files the change touches. For a small change, limit it to the elements the diff touches and the ones the model gained or changed in the range.

| Model element | Kind | Code | Test | Verdict |
|---|---|---|---|---|
| PlacedOrder | state | `order.go:74`, as `SubmittedOrder` | | wrong name |
| EmptyOrder | failure | missing | missing | missing |
| Invariant 1 | invariant | `handler.go:42` | none | wrong place: the model says decision function PlaceOrder |
| Example 4 | example | | `order_test.go:31` | ok |

Fill in every row, including the ones that turn out ok: that is what makes the check real. The report prints only the rows that are not ok (see **Report**).

The verdict is one of **ok**, **wrong name**, **wrong place**, **differs** (say how) or **missing**. An example is **ok** only when a test uses that row's values and asserts that row's result. Every verdict other than ok is a finding.

**Code to model.** Every exported type and function in the domain packages of the diff that has no row above. Each either serves an element in the first table (say which) or is **not in the model**, which is a finding: report it as a gap in the model, not only in the code.

## Checklist

### Matches the model

- Names in code are the model's and the glossary's names. No synonyms, no technical renames. Search the diff for every word listed under `_Avoid_`. A word that existing code already used, in an area whose `## Migration` plan has a rename step not yet done, is a note, not a finding; new code must use the glossary's name.
- Code respects context boundaries: no reaching into another context's types.
- A concept the code relies on but the model never names is a finding. Report it as a gap in the model, not only in the code.
- One domain idea is expressed in one place. Two pieces of code that merely look alike but express different ideas stay separate.
- Every state in the model can be told apart in the code, and a command in a state the matrix says `no` for is refused with the failure the model names.
- Each invariant is enforced where the model says, in one place. A business rule that sits in a handler, a query or a screen instead is a finding.
- Aggregates are the model's: they reference each other by ID, and one transaction changes one aggregate.
- Other systems' types and status strings stay inside the adapter the context map implies, and do not reach the domain's rules.

### Failures

- Every failure in the model exists in code under its name, and carries the data the model lists for it.

### Tests

- Every row of the model's Examples table has a test case with that row's values. The tracing table shows which.
- Every row of the Races table has a test at some level (unit, integration or end-to-end) in which the second command is judged against what the first one left. A row covered only by a test that needs a deployed system is fine; a row covered by nothing is a finding.
- Where the aggregate has a property test, read its generator: a sequence that never reaches a limit, or never leaves the first state, proves nothing about what lies beyond. Expect one only where the task asks for it or the project already does property-based or stateful testing.
- For a command or other partial ticket, limit coverage to its acceptance criteria. If adapters, storage or the aggregate property test are explicitly deferred to other tickets, list them as pending rather than rejecting this ticket for their absence. Require them when reviewing aggregate completion.
- Judge tests by observable behaviour, using the repository's testing conventions, the kind of double included.

## Break-it pass

Reading code tells you what it claims. Trying to break it tells you what it enforces.

Run each attempt, clean up and record its outcome as [break-it.md](../ddd-modelling/lifecycle/break-it.md) says.

### What to attempt

Derive the concrete attempts from the model, one or more per kind:

| Attempt | Example |
|---|---|
| Illegal transition | call a command with a state the matrix says `no` for |
| State without its required data | build a placed order with no time of placing, from outside the domain package |
| Add a new state or event | add a variant and see which code is forced to change |
| Mutate after creation | change a slice or array taken from an aggregate |
| Remove a rule | delete the check behind one invariant in a decision function, run the tests, and restore the file |

The first four ask what stops a wrong use, and the model's "enforced by" column says what should: the type, a constructor, a decision function. An illegal transition refused at run time with the model's failure counts as prevented, unless the model says the type enforces it. The last asks whether the tests would notice a rule going missing: the outcome is **test** when one fails, and **not prevented** when all still pass. Do it for each invariant the model says a decision function enforces. Rules that can only fail at runtime are the job of the example tests, checked above; do not repeat them here.

Attempts on primitives, bounds and constructor bypass belong to `secure-by-design-review`.

Compare each outcome with the model's "enforced by" column. A rule the model says is enforced by the type but that only fails at runtime is a finding. **Not prevented** for a model invariant is a blocker.

For a small change, limit the pass to the states and commands the change touches.

## Report

Open and close the report as [review-range.md](../ddd-modelling/lifecycle/review-range.md) says. Between the verdict and the end come the findings, most severe first. For each one:

- location as `file:line`
- which part of the model it breaks
- severity: **blocker** (model violated, invariant not enforced, check suppressed, model changed without approval), **should fix**, or **note**
- a concrete fix; show code changes as a diff

After the findings:

- **Tracing**: one line of counts per table ("Model to code: 41 elements, 36 ok"), then only the rows whose verdict is not ok. A reader looking for problems should not have to scan past the rows that have none.
- **Break-it**: the whole table: attempt, outcome, and what the model expected. It is short, and an attempt that was stopped is evidence too.

Write both tracing tables in full to a file outside the repository, `ddd-review-<first 12 characters of the head hash>.md` in the system's temporary directory, and give its path. If you were told where to write it, write it there.

What was not checked includes, for example, "lint not run: no config in the repository", and that security was not reviewed here.
