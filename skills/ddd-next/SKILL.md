---
name: ddd-next
description: "Say where this repository is in the DDD workflow (setup, modelling, review, approval, implementation, code review) and the one next step, with the prompt to type. Read-only. Use when the user asks what to do next with the domain model or DDD kit, where they are, what is left, or how to start."
---

# What next

Answer two questions: where does this repository stand, and what is the one next step? Change nothing, and do not start the step: the user decides when.

## Read the state

Run `tools/ddd-status.sh` from the repository root. It prints facts only; the decisions are below.

If `tools/ddd-status.sh` does not exist: with no `docs/domain/`, the kit is not set up, so the next step is `/ddd-setup`. With `docs/domain/`, the kit was installed before this tool existed; the next step is `/ddd-setup` again, which adds missing files and keeps every existing one.

If the user named a context, a command or a ticket, answer for that. Otherwise, with several contexts, prefer the one the current branch changes (`git diff --name-only <base>...HEAD`), then the first in the output that needs something.

## Pick the next step

Take the first row that applies to the chosen context. Use the context's file path and its command names in the prompt.

| # | When the status shows | Next step |
|---|---|---|
| 1 | `setup: not done` | `/ddd-setup` |
| 2 | `conventions: not recorded`, `cards: earlier layout` or `strategic cards: not installed` | `/ddd-setup`; it adds what is missing, moves earlier cards with the user's agreement, and keeps existing files |
| 3 | `contexts: none modelled yet` | `Use ddd-modelling at standard depth to model <the flow the user is about to build>.` Ask which flow if you cannot tell |
| 4 | `edited after approval` | `Use ddd-modelling to show what changed in <file> since approval, and approve it again.` |
| 5 | unconfirmed core, or any other model check problem | `Use ddd-modelling to settle the check problems in <file>.` Name the first problem |
| 6 | `pending gaps` above 0 | `Use ddd-modelling to settle the pending gaps in <file>.` Implementation is waiting for these |
| 7 | status `draft` or `derived from code`, with open questions | `Use ddd-modelling to continue <file>: answer the open questions.` |
| 8 | status `draft` or `derived from code`, depth strict or strict commands, and review `none` or of an earlier version | `/ddd-model-review <file>`, in a fresh session |
| 9 | status `draft` or `derived from code`, otherwise | Read the model's flow and its assumptions, then type `I approve <file>.` |
| 10 | approved, strict, review of an earlier version | `/ddd-model-review <file>`, in a fresh session, for the changed rows |
| 11 | `migration:` with a next step | `Use ddd-implementation for migration step <n> of <file>.` |
| 12 | example rows `without` a test | `Use ddd-implementation to implement <command> from <file>.` Take the first listed command in the order of the model's `## The flow`. Optional before the first command: `/ddd-to-tickets <file>` |
| 13 | branch ahead of its base, every example row has a test | Commit any uncommitted changes, then `/ddd-review-all Review this branch against <base>.` with the task if there is one |
| 14 | `amendments` above 0, nothing above applies | `Use ddd-modelling to fold the amendments in <file> into the model.` |
| 15 | nothing above applies | The context is done. Name the next context that needs something, or say that the whole repository is up to date |

A row about the model (4 to 10) comes before a row about code: code built on a model that is not approved is built on guesses.

The test column is a match on test names (`example 3`, `TestExamples3And4`). A row "without" a test may have one under another name. If the user says it is done, say once that naming the case `example <n>` lets the status see it, and move on to the next row.

## Report

At most five lines of state, in plain words, then the next step:

```
ordering: approved, strict, reviewed. 9 of 14 example rows have a test.
billing: draft, 2 open questions.
Branch feature/cancel, 3 commits ahead of main.

Next: implement CancelOrder in ordering.
  → Use ddd-implementation to implement CancelOrder from docs/domain/contexts/ordering.md.
```

Give one next step. If a second context also needs something, name it in the state lines; do not give a second prompt. Do not paste the status output, tables or check messages beyond the first problem.

Do not run the step, and do not edit any file, even if the fix looks small.
