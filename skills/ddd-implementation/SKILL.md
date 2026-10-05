---
name: ddd-implementation
description: "Implement an approved domain model and its examples as tests. Use the installed typed DDD cards when present, otherwise the project's existing style. Use when writing or changing domain or business-logic code in a repository that has docs/domain/."
---

# DDD implementation

Turn the approved model in `docs/domain/` into code and tests. Installed pattern cards mean the project chose the kit's typed style; without them, use the project's existing style. Do not ask the user to choose again.

## Is this repository using the kit?

If `docs/domain/` does not exist, this repository has not adopted the kit. Do the work in the repository's own style without this skill, and say in one line that `ddd-setup` and `ddd-modelling` exist. Do not stop the work to offer them.

## Before writing code

1. Read the glossary (`GLOSSARY.md` at the root, or the one `GLOSSARY-MAP.md` links to for this context), `docs/domain/context-map.md` and the file for the context you are working in, including its `## Amendments`: those rows are part of what the code must do. Read the repository's agent instructions (`CLAUDE.md`, `AGENTS.md`) for where domain code, use cases, adapters and tests go; follow them, and if they say nothing and this is the first domain code, ask once and offer to write the answer there.
2. Decide which case you are in (see **Which case applies**) and follow it.
3. Resolve the code style below before loading cards. When using cards, read `docs/ddd/cards/README.md` and the language directory's `README.md` if installed. It holds the language's idioms and check commands.
4. Load only the cards the task needs. A card holds the rules; its example, when installed, is the file of the same name in the language directory. Do not read the other language's examples.

| Task | Cards |
|---|---|
| A value with rules | 01 domain primitive, 02 value object |
| Something with a lifecycle | 03 states as types |
| A command or business rule | 04 aggregate as decision functions, 05 domain event, 10 errors as values |
| A use case end to end | 06 workflow as function, 08 repository |
| Input from HTTP, queue, database, config | 07 parse at the boundary |
| Another system or context, and each row of Facts from outside (a sign-in token, a price, a webhook) | 09 anti-corruption layer, with 07 and 14 |
| An event-sourced aggregate | 11 decider, 12 event stream repository, with 04 and 05 |
| A decision that needs outside data (a price, stock, uniqueness) | 13 facts from outside the aggregate |
| A command with an "Issued by" rule | 14 authorisation |
| A command that crosses a network | 15 idempotent command |
| An event that must cause a command elsewhere | 16 policy, with 15 |
| A password, key or token | 17 read-once secret |
| An "at least one" invariant | 18 non-empty collection |
| A list, screen, report or search | 19 read model, with 14 |
| A stored event that changes shape | 20 event versioning |

Read each card's **Corrections** section. Those are mistakes already made in this codebase.

**Code style.** Use the setup choice recorded in the agent instructions. If none is recorded, installed cards mean the kit's style; no cards means the repository's own style. In the latter case, read **Without the cards** below and skip the card table, core rules and language section. If cards are installed but your language's examples are not, follow the cards in that language's idioms, best effort, and use the project's own compile, lint and test commands. Missing kit examples or lint rules are expected in that mode.

**Depth.** Read `Depth:` and the optional `Strict commands:` line. A missing `Depth:` means strict. The strict scope is what `tools/check-model.sh` prints for each strict command: the command, its failures, the rows that name it (examples, invariants, races, facts from outside, policies) and the primitives of the data it adds. Work in that scope uses strict depth; everything else uses the context's depth. Apply this when deciding whether a gap can become an amendment.

If the task needs a pattern that no card covers, say so before writing it, and add a row to the **Wanted** table in `docs/ddd/cards/README.md`. Implement it from the core rules. Do not write the card yourself at this point: a card is made from code that has been reviewed and merged, as that README describes.

## Which case applies

**The code belongs to a context with an approved model.** Follow the model. Run `tools/check-model.sh <file>` first. A changed approved body or a structural error needs correction before implementation. The hash does not cover the glossary or context map: if their definitions or relationships conflict with the approved rules, show the discrepancy and ask for a model update and reapproval. The checker cannot detect changed business meaning.

**The model exists but is a draft, or derived from code and not confirmed.** Stop and say so, and say what is needed: the user's approval. At `standard` depth that means they confirm the core and have seen the assumptions; a review first is optional. At `strict` depth, or with strict commands, offer `ddd-model-review` in a fresh session first, unless the Status line already says `reviewed`. The approval is the user's act. Never write the approved status yourself on the strength of "go ahead" or "allow everything": ask for the word "approve", then stamp it.

**A recorded prototype with no model.** If the user chose depth none for this scope, as recorded under `## Prototypes` in the context map or agent instructions, implement within that scope without requiring a model. Follow the project's chosen code style and checks. An exemption never overrides an existing model; adoption removes or narrows it when a draft is created.

**A step from the migration plan.** The task is a step under the context file's `## Migration` (the user names it, or a ticket points at it), and the model is approved. Do that step and nothing else, in the order the plan gives, instead of the per-command order below: a step that adds characterisation tests adds only tests, and a rename step only renames. When it is done, add `(done <date>)` to the end of the step. The Migration section is outside the model-hash, so this does not affect the approval, and the next session starts at the first step not marked done.

**A new aggregate or context with no model or prototype exemption.** A new context, a new aggregate, or a new lifecycle, and nothing in `docs/domain/` for it: stop and offer `ddd-modelling`. Do not invent the model while coding. A new state, command or rule in a context that has a model is a gap in the core: see **When the model does not fit**.

**Existing code in an area that has no model.** Do not block. Most of an existing repository will be in this case, and that includes adding or changing a rule in that code.

- Make the requested change in the style the surrounding code already uses. Do not restructure it into typed DDD as a side effect.
- When using cards, apply their core rules to genuinely new code where they do not force changes to existing callers.
- Say in your summary that this area is unmodelled, and that `ddd-modelling` can model it, optionally starting from a draft derived from the code.

When unsure which case applies, ask.

## Without the cards

Write the code the way the surrounding code is written: its classes or functions, its way of reporting failures, its layout. From the model, these still hold, in whatever form that style gives them:

- Names in code are the model's and the glossary's names. A word under `_Avoid_` never appears in new code. Existing code in an adopted area may still use such a word until the rename step of its `## Migration` plan is done: do not rename it as part of another change.
- Every state, command, failure and event in the model exists in the code under its name, and nothing the model does not have is added.
- A command in a state the matrix says `no` for is refused, with the failure the model names. Whether a type or a runtime check refuses it is the style's business.
- Each invariant is enforced where the model says, in one place.
- Each row of the Examples table is a test with that row's values.
- A value with rules is checked against its bounds before it is used, and input from outside is checked before the rules run.
- Values the model marks sensitive do not appear in logs, errors or events.
- Each row of Facts from outside is checked as its "Believed when" column says.

"Done means" is then the repository's own compile, lint and test commands. The order of work is the same: one command at a time, examples as tests first.

## Core rules

- Names in code are the model's and the glossary's names, exactly. A word under `_Avoid_` never appears in new code; existing code keeps such a word until its migration plan's rename step, as above.
- No raw `string`, `int` or `number` crosses a domain function boundary. Use domain primitives built by a validating constructor.
- One type per state. No status field with optional fields.
- A command is a pure function from a specific state type to a new state, events, or a named failure. No I/O, clock or randomness inside; time and IDs are parameters.
- A command legal in several states takes exactly those states, as a narrower sum type, never the whole one.
- A repository returns the whole sum type. Narrowing to the state a command needs happens in one place: the workflow, or the `decide` function of a decider (card 11). That step returns the named "wrong state" failure. A per-state decision function never checks the state at runtime.
- When a decision needs data from outside the aggregate, the workflow fetches it and passes it in as a value. Never pass a repository, client or callback into a decision function (card 13).
- Data is immutable. Operations return new values.
- Untrusted input is parsed into domain types at the boundary, checking size before content before format before meaning. Database rows count as untrusted.
- Expected business failures are returned as values. Exceptions and panics are for bugs.
- Sensitive values never appear in events, errors or logs.
- The domain does not import infrastructure. Repository and adapter contracts are declared in the domain and implemented outside it.

## Languages

The model and the rules above are the same in every language. The idioms are not, and they live in one directory per language under `docs/ddd/cards/`. Write each language in its own idioms; do not translate one into the other.

## Order of work

Work within the requested command or ticket. A ticket's kind, acceptance criteria and out-of-scope list determine which steps below apply: a command ticket can use an in-memory repository while storage, real adapters and aggregate property tests are separate tickets. Do not pull that deferred work into this ticket. Without tickets, work one command at a time, from the model's examples to passing tests, before starting the next command.

For each command, in the order of the model's timeline (in model-only projects, use the existing representations, validation mechanisms and request handling in these steps; steps 3 and 4 are then wherever the project already puts that logic):

1. The primitives and state types it needs that do not exist yet, with tests on their limits: lowest, highest, one outside each.
2. Its rows of the model's Examples table, as a table test, written before the decision function and from the model alone. The row's Given, When and Then are the test's setup, call and assertion; name each case after the row number (row numbers are permanent, so the name stays true). A row that cannot be written as a test is a gap in the model: handle it as described under **When the model does not fit**.
3. The decision function, until those tests pass.
4. The workflow: load, authorise, narrow, decide, save. Test each use-case failure. Each row of the model's Races table needs a test at some level, and which level is the repository's choice: a unit test where a stand-in repository refuses a save when the version has changed, or an integration test against the real store. Not everything fits in a unit test. If a race is left to integration or end-to-end tests that do not exist yet, say so in your summary and name the rows, so the gap is known and not silent.
5. The boundary parser and the adapters the command needs.

For aggregate completion, add one property test: generate random sequences of its commands, apply each where the state allows it, and after every step assert every invariant in the model. If a separate property-test ticket exists, leave it to that ticket and name it in the summary. The example tests cover the cases somebody thought of; this covers the orders nobody did. In model-only projects, add one only if the project already does property-based or stateful testing; otherwise say in the summary that the invariants are covered by the example tests alone.

- Use the repository's property-testing library if it has one (`pgregory.net/rapid`, `fast-check`). Ask before adding a dependency; without one, a seeded random loop that prints the failing seed is enough.
- Make sure it can fail: remove one rule from a decision function, watch the test fail, and put the rule back. A sequence generator that never reaches a limit proves nothing about that limit.

Tests come first, and the model's Examples table is where they come from. If a skill named `tdd` is available, use it for the loop of one failing test, then the code that passes it; this skill supplies which test is next.

Tests of decision functions need no mocks, stubs or fakes, because a decision does no I/O. If one needs them, I/O has leaked into the domain. How workflow tests stand in for their dependencies is the repository's choice: follow its conventions and the tests already there.

## Done means

All of these pass, run by you, before you report the work as finished:

- compile, with the project's commands and the language's `README.md` when installed
- lint, with the project's rules and the kit's rules when that setup supplies them
- tests, covering the examples and acceptance criteria for this command or ticket; aggregate completion also needs the property test, where the setup calls for one (above)

If an expected linter or config is not set up, say so instead of skipping it silently. Model-only and cards-without-examples modes use the project's own checks and need no kit lint config. If you created a new domain directory and the project uses the kit's domain lint rules, add it to their domain paths, so the rules apply to it: for Go, in both places marked `DOMAIN-PATHS` (the `depguard` file globs and the `path-except` expression for `forbidigo`); for TypeScript, the `files` of the domain block. In the summary, distinguish this ticket's completion from any remaining storage, adapter, race-test or property-test work.

Never make a check pass by weakening it:

- follow the "Never, to make a check pass" list in the language's `README.md` when installed, including its documented exceptions; no escape from the type checker or unexplained suppression
- no rule turned off in a config, and no domain path narrowed

In your final summary, list every suppression comment you added and why. Then remind the user to run `ddd-review-all`, which runs the reviews in isolated sub-agents; do not review your own work here.

## When the model does not fit

Implementation always learns something the model did not say. What you do depends on what it is and the effective depth described above, including strict-command overrides.

**A gap in the core**: a missing state, command or invariant, who may issue a command, an aggregate boundary, or a contradiction between two rules. Stop. Describe the gap, propose the change to the model, and wait. Once the user agrees, make the change with `ddd-modelling` (the same session is fine): it updates the affected sections, runs the checker, and asks for approval again. Then continue. This holds at every depth.

**A gap in the rest**, at standard effective depth: a bound, what a failure or an event carries, a race nobody listed, an edge case, an example marked `(assumed)` that turns out not to hold when run. An example the user confirmed (one not marked `(assumed)`) is not a gap in the rest: if it does not hold, stop and ask. If a wrong guess could lose money or data, expose something, or be hard to undo, stop and ask. Otherwise:

1. Decide the least surprising behaviour, consistent with the rules the model does state.
2. Implement it, with a test.
3. Add a row under `## Amendments` in the context file: the section, what the model said (or "nothing"), what you learned, and what the code now does. Do not edit the model above that heading. The model-hash leaves Amendments out, so the approval stands.
4. Carry on.

At strict effective depth, a gap in the rest also stops the work. Ask the user, update the affected model sections through `ddd-modelling`, and get reapproval before implementing the decision. Such a change needs a review of the changed rows only, not a new review of the whole model; `ddd-modelling` says how.

Something marked `(assumed)` in the model is implemented as written. If implementing it shows the assumption cannot hold, that is a gap in the rest.

In your final summary, list every amendment you recorded, and say that `ddd-modelling` can fold them into the model. The code and the model must not drift apart silently; an amendment is how they move together without stopping the work.

## When the user corrects you

If the user points out a pattern mistake, fix it and add a dated line to the **Corrections** section of the relevant card, describing the mistake and the right form. Show that edit as a diff.
