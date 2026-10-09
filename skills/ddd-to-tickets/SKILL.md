---
name: ddd-to-tickets
description: "Turn an approved domain model into tickets: one per command, with the model's own rows as acceptance criteria, blocking edges from the state types, and a line saying whether the ticket needs a running dependency. Use after the model is approved, before implementation, and again when the model changes."
disable-model-invocation: true
---

# DDD to tickets

Turn the approved model in `docs/domain/` into tickets an agent can pick up one at a time. The model already holds the acceptance criteria: its Examples, Races, Use-case failures and matrix rows. A ticket points at those rows; it does not restate them.

Two things come out of this that a general ticket breakdown does not give:

- Every ticket says what it **runs with**. Most domain tickets run with nothing: no database, no broker, no container. Only tickets that write an adapter need a running dependency.
- `task-review` gets a task whose requirements are row numbers in the approved model, so "done" can be checked row by row.

## Before you start

1. If `docs/domain/` does not exist, this repository has not adopted the kit. Say so and stop.
2. Run `tools/check-model.sh` on each context file in scope. If it fails, or the status is `draft` or `derived from code, not confirmed`, stop and say which. Tickets are cut only from an approved model.
3. Note the commit the context file last changed in: `git log -1 --format=%h -- <file>`. Every ticket carries it. If the approved model is not committed yet, ask the user to commit it first.
4. Read [depth.md](../ddd-modelling/lifecycle/depth.md) and [code-style.md](../ddd-modelling/lifecycle/code-style.md). A missing `Depth:` means strict. Carry each ticket's effective depth into it, naming the strict scopes it touches.
5. In the repository's own code style, tickets describe the model's behaviour in the project's existing style; do not add a typed refactor to the work, and see **Without the cards** below.

## Scope

Ask what to cut tickets for, if the user did not say: a whole context, one aggregate, or the commands a model change touched (`git diff <commit>` on the context file, from the commit the existing tickets carry).

If the user gives a spec or a parent issue, read it. Behaviour the spec asks for and the model does not have is not a ticket: stop and offer `ddd-modelling`. Work in the spec that is not domain behaviour (screens, endpoints, reports, deployment) is out of scope here; see **With to-tickets**.

## How many tickets

A ticket is one commit, or one small pull request: small enough to review in one sitting, and done when its rows pass. Cut by size, not by rule:

- An aggregate with three commands or fewer and no adapter is **one ticket**: the tracer, with every command's rows in it.
- Otherwise use the kinds below, one ticket per command.

## Ticket kinds

Cut the tickets per aggregate, in the order of the model's `## The flow`.

### 1. Tracer

The first command of the aggregate, usually the one that starts from `()`, through every layer: primitives, state types, examples as tests, decision, workflow, boundary parsing, the real repository, and one entry point wired to it.

It also delivers the **repository contract test**: one suite, run against both the in-memory repository and the real one, covering load, save, "not found", and a save that fails when the version has changed. Every later ticket relies on the in-memory repository behaving like the real one, and this suite is what makes that true.

Runs with: the storage dependency.

One tracer per aggregate. It exists to find a wrong assumption about storage, transactions or versions on day one and not after the last command.

### 2. Command

One ticket per remaining command. It covers steps 1 to 4 of `ddd-implementation`'s order of work, plus boundary parsing for the command's input: the model's needed values and states in the chosen style, the Examples rows as tests, the decision, and the workflow against the in-memory repository. Real adapters, storage changes and the aggregate property test belong to their separate tickets. State that in **Out of scope** so implementation and review use the same completion boundary.

Runs with: nothing.

Blocked by: the tracer, and the ticket that first produces each state the command starts from. `CancelOrder : DraftOrder | PlacedOrder` is blocked by the ticket that introduces `PlacedOrder`. Commands that share no such edge can be worked in parallel.

Do not split a command across tickets, and do not merge two commands into one. A command with many example rows is still one decision.

### 3. Storage

When a command ticket introduces a state or field the real repository does not store yet, cut a storage ticket for it: the real repository stores and loads the new shape, and the contract test covers it.

Runs with: the storage dependency. Blocked by: the command ticket.

### 4. Adapter

One ticket per row of **Facts from outside**, and one per relationship in `context-map.md` that this context is downstream of. The command ticket already declared the contract and tested the workflow with a value passed in; this ticket implements the contract against the real source.

Runs with: the source, or a recorded stand-in for it when the source cannot be run locally. Say which. Blocked by: the command ticket that uses the fact.

### 5. Policy

One ticket per row of **Policies**: the event causes the command, the command is safe to deliver twice, and the row's "If the command fails" column is what happens when it fails.

Runs with: nothing when event and command are in one process; the delivery mechanism when they are not. Blocked by: the ticket of the command that emits the event and the ticket of the command it causes.

### 6. Property test

One per aggregate: random sequences of its commands, every invariant asserted after every step, and proof that the test fails when a rule is removed.

Runs with: nothing. Blocked by: every command ticket of the aggregate.

### Without the cards

The ticket kinds above assume the kit's structure: an in-memory repository beside the real one, and decisions that run with nothing. A model-only project keeps its own structure, so:

- The tracer has no repository contract test unless the project already has a repository abstraction with a stand-in.
- A command ticket runs with whatever the project's tests normally use, a test database included. Say which on its **Runs with** line.
- A storage ticket is cut only when the project separates storage from the command's code.
- A property-test ticket is cut only if the project already does property-based or stateful testing.

## Acceptance criteria

Take them from the model, by section and row number. Do not paraphrase a rule: a ticket that restates a rule in its own words is a second model, and the two will drift.

For a tracer or command ticket, list:

- Examples rows whose **Covers** column names the command, one of its failures, or an invariant it could break
- Use-case failures rows that name the command
- Races rows that name the command
- each `no:` cell in the command's column of the matrix: the workflow returns the named use-case failure for that state
- the command's **Issued by** row: a caller it does not allow is refused
- for each primitive the ticket introduces: lowest, highest, and one value outside each bound
- for each primitive marked sensitive: its value appears in no event, failure or log
- the project's applicable compile, lint and tests pass, and the approved model body has not changed

For a storage or adapter ticket, list:

- stored or received data goes through the same validation as any other untrusted input: size, then content, then format, then meaning
- a test for each: a value outside a primitive's bounds, a missing field, an unknown state, an oversized payload. Each is rejected with a named failure and none reaches the domain
- for an outside fact: the row's "Believed when" checks are each made, with a test for each one failing; "If not, or no answer" is the outcome of a failed check, a timeout and an unavailable source; and the "May it be stale?" column is honoured
- sensitive values do not appear in logs or failures
- the contract test passes against the real implementation

A row that no ticket lists is a gap. A row you cannot assign to a command is a finding about the model: report it, do not invent a ticket for it.

## Check coverage, then ask

Before showing anything, check that every command, Examples row, Races row, Use-case failure, Policies row and Facts from outside row in scope appears in at least one ticket. List what does not.

Then present the breakdown as a numbered list. For each ticket: title, kind, blocked by, runs with, and the rows it covers. When the breakdown is a single tracer ticket, skip the questions below and ask only whether to publish it. Otherwise ask:

- Is the tracer the right first command, or does another one carry more risk?
- Are the blocking edges right?
- Is there a dependency you cannot run locally, so its adapter ticket needs a stand-in?

Iterate until the user approves. Do not publish before that.

## Publish

If `docs/agents/issue-tracker.md` exists, follow it: publish one issue per ticket in dependency order so that blocking edges can use real identifiers, with the platform's native blocking link where it has one. Apply the `ready-for-agent` label if the repository uses it.

Otherwise write one file per ticket to `.scratch/<context>/issues/<NN>-<slug>.md`, numbered from `01` in dependency order.

Use the vocabulary of the glossary in titles and text. No code in a ticket, and no file paths except the model's on the **Model** line.

<ticket-template>

# <NN>: <Command or thing, in glossary terms>

**Kind:** tracer | command | storage | adapter | policy | property test

**Model:** `docs/domain/contexts/<context>.md`, at commit `<commit>`

**Depth:** standard | strict (name the strict commands whose strict scope this ticket touches)

**What to build:** one or two sentences, from the point of view of whoever issues the command, and the step of the model's flow it belongs to.

**Runs with:** nothing | <the dependency>

**Blocked by:** the tickets that gate this one, or "None (can start immediately)".

**Acceptance criteria**

- [ ] Examples rows <n, n, n> pass as table tests, each case named after its row
- [ ] Use-case failures: <names>
- [ ] Races: rows <n>
- [ ] Matrix: <State> returns <failure>
- [ ] Issued by: <who>; any other caller is refused
- [ ] Bounds: <primitives introduced here>
- [ ] Applicable compile, lint and tests pass; the approved model body is unchanged

**Out of scope:** what a reader might expect here and will find in another ticket, by number.

</ticket-template>

## When a ticket is picked up

The ticket says so itself, in one line under **Model**: if `git log -1 --format=%h -- <file>` no longer gives the commit in the ticket, the model changed since the ticket was cut. The implementer looks at what changed (`git diff <commit> -- <file>`) and at the rows this ticket lists. If none of them changed, the work goes on and the ticket gets the new commit. If one did, the ticket is updated first, as described below. Add that line to every ticket.

An implementer also reads the `## Amendments` and `## Pending` rows that name this ticket's command. A pending row blocks the ticket until `ddd-modelling` settles it.

## When the model changes

A model grows: amendments are folded in, a command is added, a rule changes. Do not cut a new set of tickets. Run this skill again on the change (`git diff <commit> -- <file>`, from the commit the tickets carry) and:

- update the open tickets whose rows changed, and give them the new commit
- cut tickets only for commands, facts and policies that are new
- for a ticket that is already done and whose rows changed, cut a small follow-up that lists only the changed rows
- leave every other ticket alone

Show the user the list of tickets touched and why, before publishing.

## With to-tickets

Matt Pocock's `to-tickets` cuts vertical slices from a spec. Use this skill for the domain behaviour in a spec and `to-tickets` for the rest: screens, endpoints beyond the tracer's one entry point, reports, deployment. Run this skill first and give `to-tickets` the published tickets as existing blockers, so a screen is blocked by the command it calls.

The templates match his, so `implement` and `task-review` read either kind. The differences are the **Kind**, **Model** and **Runs with** lines, and that only the tracer is a slice through every layer. The command tickets are deliberately not: after the tracer, the layers below the domain are known to work, and a command is finished when its rows pass.

## Do not

- Cut a ticket for behaviour the model does not have.
- Copy a rule, an example or a bound into a ticket. Point at the row.
- Give a command ticket a running dependency, when the project uses the cards. If it seems to need one, I/O has leaked into the decision or the workflow is being tested against the wrong repository.
- Build or run an image of the application in any ticket but the tracer.
- Change the model. A gap found while cutting tickets is handled as [gaps.md](../ddd-modelling/lifecycle/gaps.md) says: one that must stop goes to `ddd-modelling`; one the implementer may settle is listed in the affected ticket.
