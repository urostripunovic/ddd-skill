# Reference

Everything the [README](README.md) leaves out. The rules the skills themselves follow are in [`skills/ddd-modelling/lifecycle/`](skills/ddd-modelling/lifecycle/README.md); this page explains them for people and links there for the exact wording.

- [Install and setup](#install-and-setup)
- [Terms](#terms)
- [Modelling](#modelling)
- [Review and approval](#review-and-approval)
- [Implementation](#implementation)
- [Code review](#code-review)
- [When implementation finds a gap](#when-implementation-finds-a-gap)
- [The context file](#the-context-file)
- [Strategic and pattern cards](#strategic-and-pattern-cards)
- [Optional integrations](#optional-integrations)
- [Compatibility](#compatibility)
- [Developing the kit](#developing-the-kit)

## Install and setup

### Starting skills

`ddd-modelling`, `ddd-implementation` and `ddd-next` start when you ask for them in plain words. In a repository without `docs/domain/`, modelling and implementation stay out of the way, so the kit is opt-in per repository. The other seven (`ddd-setup`, `ddd-model-review`, `ddd-to-tickets`, `ddd-review`, `secure-by-design-review`, `task-review` and `ddd-review-all`) only start when you invoke them by name, so the agent never runs setup or a review on its own.

| Agent | Invoke a skill by name |
|---|---|
| Claude Code | `/ddd-setup`, followed by any instructions on the same line |
| OpenCode | `@ddd-setup` in your message |

### Setup options

`/ddd-setup` asks how much of the kit to install. This is separate from modelling depth: any option can use a standard or strict model.

| Option | What you get | How `ddd-implementation` writes code |
|---|---|---|
| Full | Model templates, checker, strategic cards, pattern cards, and Go or TypeScript examples and lint rules | Follows the kit's functional patterns and the supplied language examples |
| Cards without examples | Model templates, checker, strategic cards and pattern cards | Adapts the cards to your language's idioms, best effort. No language examples or lint rules |
| Model only | Model templates, checker and strategic cards. Recommended when your project already has a consistent code style | Follows your existing style, using the model's rules and examples, and your project's own checks |

Setup copies the files, records your code style and code and test locations under `## Domain code` in `CLAUDE.md` or `AGENTS.md`, and merges the lint rules into your configs. It never overwrites a file, installs no programs or dependencies, and reports missing tools.

### What setup installs

```text
docs/domain/         Context map, model template and your context files
docs/ddd/strategic/  10 strategic cards, quoted from Evans' DDD Reference and the DDD Crew
docs/ddd/cards/      Pattern cards per code style; functional/ holds 20, with Go and TypeScript examples
tools/               Model checker, approval stamping, workflow status, card checks and lint configs
```

Modelling creates `GLOSSARY.md`, the glossary, when the first term is agreed. Several contexts share it, with a heading each, until a word means different things in two of them; then each context gets its own `GLOSSARY.md` and a root `GLOSSARY-MAP.md` links them.

### Prerequisites

The kit works without other skills. You need a coding agent that can read skills, edit project files and run shell commands.

| Use | Requirements |
|---|---|
| Setup, modelling and approval | A Git repository, Git, Bash and Python 3. The model checker uses Python; approval hashing uses Git |
| Go implementation with the supplied rules | Go and `golangci-lint`; the reference lint config uses v2 format. Checking the card examples needs Go 1.24 or later and `golangci-lint` v2 |
| TypeScript implementation with the supplied rules | Node.js, TypeScript, ESLint and `typescript-eslint`, plus your project's test tooling. The reference ESLint config uses flat config and type-aware rules |
| Model only, or another language | Your project's compiler or runtime, lint and test tools |
| Combined code review | An agent that can start subagents, and the project's build and test dependencies. Without subagents, run the review skills one by one in fresh sessions |

`tools/check-cards.sh` is only needed after editing a card example. Its TypeScript checks need npm and download their own tooling into `.cards-check/`.

### Manual setup

Instead of `/ddd-setup`, run the installer from a clone of this repository. The target must be the root of a Git repository.

```sh
skills/ddd-setup/install.sh --lang go,ts /path/to/your-project   # full kit; or --lang go, --lang ts
skills/ddd-setup/install.sh --lang none /path/to/your-project    # cards without examples
skills/ddd-setup/install.sh --model-only /path/to/your-project   # model only
```

Without flags, the script detects languages from `go.mod` and `tsconfig.json`; for an empty project, name them. It copies the files and, with cards, adds `.cards-check/` to `.gitignore`. The rest is yours to do: record the code style and code and test locations under `## Domain code` in your agent instructions, merge the rules from `tools/lint/` into your own configs, and set their `DOMAIN-PATHS` placeholders to your domain directories. Leave the copies in `tools/lint/` unchanged: `tools/check-cards.sh` uses them.

## Terms

| Term | Meaning |
|---|---|
| Domain | The business area whose rules the software handles, such as library lending |
| Flow | A sequence of business actions, such as choosing items and placing an order |
| Bounded context | A part of the domain with its own consistent terminology and rules. A **context file** is its Markdown model |
| Subdomain kind | How important a context is to the success of the organisation, in the DDD Crew's words: **core** (a key strategic initiative), **supporting** (necessary but not a differentiator) or **generic** (a common capability found in many domains) |
| Relationship pattern | How two contexts and their teams relate, such as **conformist** (adhere to the upstream team's model) or **anticorruption layer** (an isolating layer that translates between the two models). See [Strategic and pattern cards](#strategic-and-pattern-cards) |
| Command | A requested business action, such as `PlaceOrder` |
| State | A stage in something's lifecycle, such as a draft or placed order |
| Event | A business fact that has happened, such as `OrderPlaced` |
| Invariant | A rule that must always hold, such as a placed order having at least one item |
| Aggregate | Related domain data whose rules must be enforced together, such as an order and its items. Its **boundary** decides what belongs in that unit |
| Pure decision function | A function that decides an outcome from its inputs without performing I/O or changing external state |

## Modelling

### Choose the scope

You can start with a specific flow, a business area, a whole domain, or a change to an existing model. You don't need to know the context or aggregate boundaries in advance; the agent helps find them through questions. You can point to requirements, tickets, API specifications or code in any prompt.

**A specific flow:** name its start and end, and any exclusions.

```text
Use ddd-modelling at standard depth to model the ordering flow,
from adding the first item to placing or cancelling the order.
Leave delivery and returns for later.
```

**A broader domain:** describe the business and ask to identify its parts first.

```text
Use ddd-modelling at standard depth for a library lending domain:
borrowing, reservations and returns. Help identify the bounded
contexts, then start with borrowing a book.
```

**An existing model:** name the context and the behaviour to change.

```text
Use ddd-modelling to update docs/domain/contexts/ordering.md
so customers can cancel a placed order until picking starts.
```

The agent writes as the conversation goes: the glossary in `GLOSSARY.md`, the contexts and how they relate in `docs/domain/context-map.md`, and a model per context in `docs/domain/contexts/<context>.md`. It runs `tools/check-model.sh` on the structure. You decide whether the business rules are right.

### Choose a depth

Depth controls how much you confirm before coding. It is a sentence in your prompt, not a flag. If you leave it out, the agent picks one (standard, or strict for money, credentials, authorisation, personal data or anything that cannot be undone) and says so in one line, so you can change it. The exact rules are in [lifecycle/depth.md](skills/ddd-modelling/lifecycle/depth.md).

| Depth | What you confirm |
|---|---|
| `standard` | The usual choice. You confirm the **core**: states, commands, who may issue them, what makes callers and outside data trusted, invariants, aggregate boundaries and terms. The agent proposes the rest, such as limits and edge cases, marks it `(assumed)` and shows one list to correct. Who may issue a command and the invariants are never assumed: the checker rejects them until you answer. About three interview rounds; review is optional |
| `strict` | The details too: limits, failures, concurrent actions that conflict, worked examples. A review in a fresh session before approval. Recommended for money, credentials, authorisation, personal data and anything hard to undo |
| `none` | Postpone modelling for a prototype. The scope is recorded under `## Prototypes` in the context map, and no model is written. Ask your agent separately to write the prototype; it can be adopted into a model later |

Make single commands strict inside a standard context:

```text
Use ddd-modelling at standard depth for ordering, but treat
ChargePayment and RefundPayment as strict.
```

The context file records `Depth: standard` and `Strict commands: ChargePayment, RefundPayment`. Each strict command's **strict scope** (the command, its failures, the rows that name it and the value types it touches) stays strict through review, tickets and implementation; `tools/check-model.sh` prints it. Later sessions reuse these choices.

### The context map

When the model has more than one context, or depends on another system, the agent asks two questions for `docs/domain/context-map.md`: how important each context is to the organisation (its **Kind**: core, supporting or generic), and which **Pattern** describes each relationship between contexts. At standard depth, when one person or team owns both sides, the agent proposes the pattern as an assumption instead of asking. Describe how the teams actually work today; the strategic cards quote Evans: "Map the existing terrain. Take up transformations later."

### Start from existing code

Ask for a draft derived from the code you're working on:

```text
Use ddd-modelling to derive a draft from src/ordering at standard
depth. Start with orders and their items; help identify the
aggregate boundary.
```

The agent records what the code does, with a file and line for each item, checks it with you, and writes a numbered `## Migration` plan. You decide where the current behaviour is wrong. It works one aggregate at a time. With cards, migration moves the code to the functional style; model-only projects keep their representations and change only what the model requires. Renaming code to the glossary's names is a step of its own.

Then ask for one step at a time, for example `Use ddd-implementation for migration step 2 of docs/domain/contexts/ordering.md.` Each finished step is marked done, so a later session continues from the next one.

If you tried the technology first in a prototype on another branch, name the branch: the agent uses what it showed about APIs and other systems, not its structure.

## Review and approval

Modelling stops at the model. Approval is a separate step, and only you can give it. The exact rules are in [lifecycle/approval.md](skills/ddd-modelling/lifecycle/approval.md).

For a strict model, or one with strict commands, review it in a **fresh session** in the same project, so the reviewer did not write it. At standard depth, review is optional.

```text
/ddd-model-review docs/domain/contexts/ordering.md
```

The reviewer reports findings; it does not change or approve the model. Take them back to modelling:

```text
Use ddd-modelling to address these review findings in
docs/domain/contexts/ordering.md: [paste the findings].
```

If the review found blockers, return to the review session to check the fixes; a review with no blockers needs no further round. The agent then records the review on the `Status:` line as `reviewed <date>`, with the hash it reviewed in the line's comment. If the model changes later, that review is out of date, and only the changed rows need reviewing again. With strict commands, the review also records each strict scope, and approval is refused after a change inside one until it is reviewed again.

When you have read the model and are satisfied:

```text
I approve docs/domain/contexts/ordering.md.
```

Setup records who may approve (`Approvers:` in `CLAUDE.md`). With more than one name there, add `Approver: <your name>`.

The agent stamps it with `tools/stamp-model.sh`: `Status: approved by <name> on <date>`, with the model-hash in a comment at the end of the line. The script refuses while the model fails its check. At standard depth, approval also accepts the listed assumptions you did not correct.

## Implementation

Optionally, turn the approved model into tickets first, with its examples and rules as acceptance criteria. There is usually one ticket per command, or one for a small aggregate:

```text
/ddd-to-tickets docs/domain/contexts/ordering.md
```

Then name the command and the model:

```text
Use ddd-implementation to implement PlaceOrder from
docs/domain/contexts/ordering.md.
```

Implementation works one command at a time. It writes the model's examples as tests first, naming each case `example <n>` after its row, then the types, decision and surrounding code in the style chosen at setup, and runs compile, lint and tests. A draft model, or one changed since approval, stops it until you approve.

Code in an area with no model is not blocked: the agent makes the change in the surrounding style and mentions that the area can be modelled. Modelling is needed when a change adds a new context, aggregate or lifecycle.

## Code review

Work on a branch, commit the changes, and ask:

```text
/ddd-review-all Review this branch against main.
The task is: [link or path to the original task].
```

Only committed changes are reviewed. Without a base branch, the reviewer uses the point where your branch left the default branch. `ddd-review-all` reviews in separate subagents and temporary Git worktrees. The full review runs three: `ddd-review` (code against the model), `secure-by-design-review` (security) and `task-review` (code against the task; skipped if you have no task). It runs when a context is strict, has no `Depth:` line, or the change names a strict command, or when you ask: `/ddd-review-all full`. Otherwise, at standard depth, one reviewer runs `ddd-review` and the Secure by Design sections on authorisation, sensitive data and input at the boundary; it does not ask for a task. Without subagents, run the review skills one by one in fresh sessions.

With Matt Pocock's skills, review domain code with `ddd-review-all` and the rest of a branch (screens, endpoints, reports) with his `code-review`, which checks the repository's documented standards and common code smells. When his `implement` or `implement-spec` built domain code, `ddd-review-all` takes the place of their `/code-review` step.

The combined report ends with the next step:

- **No blockers:** merge. Fix should-fix findings without another round, or turn them into tickets.
- **Blockers:** fix and commit, then run `/ddd-review-all` again. Only the reviewers that found blockers run, and each checks just the fix commits.
- **A gap in the model:** take it to `ddd-modelling`, not to the code.

## When implementation finds a gap

Implementation always learns something the model did not say. The exact rules are in [lifecycle/gaps.md](skills/ddd-modelling/lifecycle/gaps.md).

| The gap | What happens |
|---|---|
| In the core (a missing state, command, invariant, permission, trust rule, boundary, or two rules that contradict), at any depth | Implementation stops and writes the question under `## Pending` in the context file |
| Anything, at strict depth or in a strict scope | The same |
| A guess that could lose money or data, expose something or be hard to undo, or a confirmed example that does not hold | The same |
| Anything else, at standard depth | The agent decides, tests it, and records it under `## Amendments`; work goes on |

To settle pending questions and fold amendments back into the model:

```text
Use ddd-modelling to settle the pending gaps and fold the
amendments in docs/domain/contexts/ordering.md.
```

You approve the updated model once.

## The context file

A context file follows `docs/domain/contexts/_template.md`. `tools/check-model.sh` requires every section (write `None.` where there is nothing) and checks the structure, but not whether the business rules are right; [lifecycle/checker.md](skills/ddd-modelling/lifecycle/checker.md) lists what it checks and what it does not. Example row numbers are permanent, because tests and tickets refer to them.

The `Status:` line is always written by `tools/stamp-model.sh`. The approval hash covers the whole file except the `Status:` line and the **notes tail**: `## Migration`, `## Amendments` and `## Pending`, in that order, at the end. Writing to the tail never undoes an approval; every other edit does. That is why, at standard depth, a change to the rest of an approved model (a bound, a payload, an edge case) is written as an `## Amendments` row and the approval stands, while a change to the core sets the model back to draft. A model section placed after the tail is an error. The hash does not cover the glossary or the context map: when a change there alters what an approved rule means, the agent shows the affected contexts and asks for approval again. See [lifecycle/notes-tail.md](skills/ddd-modelling/lifecycle/notes-tail.md).

## Strategic and pattern cards

**Strategic cards** (`docs/ddd/strategic/`) cover how much each context matters and how contexts relate: partnership, shared kernel, customer/supplier, conformist, anticorruption layer, open-host service, published language, separate ways and big ball of mud. They quote Eric Evans' *Domain-Driven Design Reference* and the DDD Crew's *Context Mapping* and *Bounded Context Canvas* (all CC BY 4.0) and add no rules of their own. They are installed with every setup option.

**Pattern cards** (`docs/ddd/cards/`) cover how domain code is written, one directory per style. `functional/` holds 20 cards in the style of Scott Wlaschin's *Domain Modeling Made Functional*, each with a rule, what enforces it, an anti-pattern, and an example per language. Each card has a **Corrections** section: when an agent gets a pattern wrong, a dated line goes there, and later sessions read it. See [the cards' README](skills/ddd-setup/kit/docs/ddd/cards/README.md) for adding a pattern, a language or a style.

## Optional integrations

With [Matt Pocock's skills](https://github.com/mattpocock/skills) installed, the kit uses `grilling` for interviews, `domain-modeling` for challenging terms while modelling, `tdd` for the failing-test-to-passing-code loop, `to-tickets` for the work around the domain, and `code-review` for the rest of a branch. None is required: without them, the kit's skills carry their own rules for the same work. The glossary is his `GLOSSARY.md`, in his format, so his `domain-modeling`, `tdd` and other skills read and extend the same terms. Domain decisions go in the context file's `## Decisions`, under the approval hash; technical ones are his ADRs in `docs/adr/`.

## Compatibility

- A model with no `Depth:` line is treated as strict.
- A glossary under its earlier name, `CONTEXT.md` or `CONTEXT-MAP.md` (Matt Pocock's skills before 1.3), is still read, with a warning. `/ddd-setup` renames it to `GLOSSARY.md` with your agreement. Once a `GLOSSARY.md` exists, a `CONTEXT.md` beside it is no longer read, and the check says so.
- An approval recorded without a hash is accepted with a warning and cannot be verified.
- Cards installed before the style directories sit directly under `docs/ddd/cards/`. `/ddd-setup` reports them and, with your agreement, moves them into `docs/ddd/cards/functional/`, keeping their Corrections.

## Developing the kit

`evals/` and `tests/` test the kit itself; don't copy them into your project. `tests/` checks the scripts (`python3 -m unittest discover -s tests`). `evals/` measures whether the skills do what they claim, against fixed fixtures and answer keys; see [evals/README.md](evals/README.md).
