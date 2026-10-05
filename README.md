# Typed DDD skills

Skills for working through business rules with a coding agent before implementing them. The agent asks questions, records a domain model in Markdown, and uses its worked examples as test cases once you approve it.

The code patterns use domain-driven design (DDD) with named types for domain values, a type for each state, and pure functions for business decisions. There are examples and lint configs for Go and TypeScript. You can also use just the modelling workflow with your existing code style.

## Install

Installation has two steps: make the skills available to your coding agent, then set up the project files.

### 1. Install the skills

Clone this repository. From the clone's root, copy the skills into the project that will use them:

```sh
mkdir -p /path/to/your-project/.claude/skills
cp -r skills/. /path/to/your-project/.claude/skills/
```

For all your projects, use `~/.claude/skills/` as the destination instead. Claude Code and OpenCode both read these locations.

### How to start a skill

`ddd-modelling` and `ddd-implementation` start when you ask for them in plain words, as in the examples below. In a repository without `docs/domain/` they stay out of the way, so the kit is opt-in per repository. The other seven (`ddd-setup`, `ddd-model-review`, `ddd-to-tickets`, `ddd-review`, `secure-by-design-review`, `task-review` and `ddd-review-all`) only start when you invoke them by name, so the agent never runs setup or a review on its own:

| Agent | Invoke a skill by name |
|---|---|
| Claude Code | `/ddd-setup`, followed by any instructions on the same line |
| OpenCode | `@ddd-setup` in your message |

The examples below use the Claude Code form; in OpenCode, write `@` instead of `/`.

### 2. Set up your project

Start a Claude Code or OpenCode session in your target project's root and run:

```text
/ddd-setup
```

Setup copies the templates and tools, records your code style and code/test locations in `CLAUDE.md` or `AGENTS.md`, and merges the relevant lint rules into your configs. The project-file copy script preserves existing files. Setup doesn't install programs or dependencies; it reports missing tools.

### Setup options

Setup asks how much of the kit to install. This is separate from modelling depth: any of these options can use a standard or strict model.

| Option | What you get | How `ddd-implementation` writes code |
|---|---|---|
| Full | Model templates, checker, pattern cards, and Go or TypeScript examples and lint rules. | Follows the kit's typed DDD patterns and the supplied language examples. |
| Cards without examples | Model templates, checker, and pattern cards: short guides to when and how to use each code pattern. | Adapts the cards to your language's idioms, best effort. No language-specific examples or lint rules are supplied. |
| Model only | Model templates and checker. Recommended when your project already has a consistent code style. | Follows your existing style in your language, using the model's rules and examples. Runs your project's own checks. |

### Prerequisites

The kit works without other skills. You need a coding agent that can read skills, edit project files and run shell commands.

| Use | Requirements |
|---|---|
| Setup, modelling and approval | A Git repository, Git, Bash and Python 3. The model checker uses Python; approval hashing uses Git. |
| Go implementation with the supplied rules | Go and `golangci-lint`; the reference lint config uses v2 format. Checking the supplied card examples requires Go 1.24 or later and `golangci-lint` v2. |
| TypeScript implementation with the supplied rules | Node.js, TypeScript, ESLint and `typescript-eslint`, plus your project's test tooling. The reference ESLint config uses flat config and type-aware rules. |
| Model-only or another language | Your project's compiler or runtime, lint and test tools. |
| Combined code review | An agent with subagent support (separate agent sessions) and the project's build/test dependencies. Without it, run the three review skills individually in fresh sessions. |

Setup reports missing tools and any checks it could not run; install the needed tools before implementation. `tools/check-cards.sh` is only needed after editing card examples. Its TypeScript checks also require npm and download their own tooling into `.cards-check/`.

## Start modelling: choose the scope

You can start with a specific flow, a business area, a whole domain, or a change to an existing model. Describe what people do and where you want to start; you don't need to know the context or aggregate boundaries in advance. The agent helps find those through questions.

**A specific flow:** name its start and end, and any exclusions.

```text
Use ddd-modelling at standard depth to model the ordering flow,
from adding the first item to placing or cancelling the order.
Leave delivery and returns for later.
```

**A broader domain:** describe the business and ask to identify its parts before choosing a starting flow.

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

You can point to requirements, tickets, API specifications or relevant code in any of these prompts. A flow can cross several contexts; the model records their responsibilities and interactions. You can work on one part without modelling the entire repository.

You can also invoke the skill by name (`@ddd-modelling` in OpenCode):

```text
/ddd-modelling Model the ordering flow at standard depth.
```

The agent writes the model as the conversation progresses: a business glossary in `GLOSSARY.md`, a map of the business areas in `docs/domain/context-map.md`, and a model for each area in `docs/domain/contexts/<context>.md`. It runs `tools/check-model.sh` to check the model's structure and consistency. You decide whether the business rules are right.

### Terms used in the workflow

| Term | Meaning |
|---|---|
| Domain | The business area whose rules the software handles, such as library lending. |
| Flow | A sequence of business actions, such as choosing items and placing an order. |
| Bounded context | A part of the domain with its own consistent terminology and rules. A **context file** is its Markdown model. |
| Command | A requested business action, such as `PlaceOrder`. |
| State | A stage in something's lifecycle, such as a draft or placed order. |
| Event | A business fact that has happened, such as `OrderPlaced`. |
| Invariant | A rule that must always hold, such as a placed order having at least one item. |
| Aggregate | Related domain data whose rules must be enforced together, such as an order and its items. Its **boundary** determines what belongs in that unit. |
| Pure decision function | A function that decides an outcome from its inputs without performing I/O or changing external state. |

### Choose a depth

Depth controls how much you confirm before coding. It is a natural-language instruction, not a CLI flag. If you omit it, the agent asks and recommends a depth.

| Depth | What you confirm |
|---|---|
| `standard` | The usual choice. Confirm the core: states, commands, permissions, invariants, aggregate boundaries and terminology. The agent proposes details such as limits and edge cases, marks them `(assumed)`, and shows one list for you to correct. Model review is optional. |
| `strict` | Confirm the details too: limits, failures, concurrent actions that can conflict, and worked examples. Review in a fresh session before approval. Recommended for money, credentials, authorisation, personal data and behaviour that's hard to undo. |
| `none` | Postpone modelling for a prototype. The skill records its scope in the context map (or agent instructions if there is no map), then stops without producing a model. Ask your coding agent separately to write the prototype. Later sessions honour that exemption until you start adopting it. |

Standard depth aims for about three interview rounds. If the core is still unclear, the agent asks whether to continue. Strict depth has no fixed round target: it works through the detailed rules and examples, leaving unanswered questions visible for review.

You can make specific commands strict within a standard context:

```text
Use ddd-modelling at standard depth for ordering, but treat
ChargePayment and RefundPayment as strict.
```

For a mixed-depth model, ask for a strict review of the strict commands' scope in a fresh session before approval.

The chosen depth is saved as `Depth: standard` or `Depth: strict` in the context file. Command-specific exceptions use `Strict commands: ChargePayment, RefundPayment` below it. Each strict command's **strict scope** is the command, its failures, the model rows that name it (examples, invariants, races, facts from outside, policies) and the value types of the data it adds. `tools/check-model.sh` prints that scope, so you can see exactly what stays strict through review, tickets and implementation. Later sessions reuse these choices; you don't need to repeat them.

### Start from existing code

Ask the skill to derive a draft from the area you're working on. Use your actual code path:

```text
Use ddd-modelling to derive a draft from src/ordering at standard
depth. Start with orders and their items; help identify the
aggregate boundary.
```

The agent records what the code does, checks it with you, and writes a numbered migration plan. You decide where the current behaviour is wrong. This works one aggregate at a time. With cards, migration follows the chosen typed style; model-only projects keep their existing representations and change only what the model requires. Renaming code to the glossary's names is a step of its own; until it is done, existing code keeps its old names. Review is optional for standard scope; for strict scope the agent asks you to run it before approval.

Then ask for one step at a time, for example `Use ddd-implementation for migration step 2 of docs/domain/contexts/ordering.md.` The agent marks each step done in the plan, so a later session continues from the next one.

If you're building from a prototype on another branch, name the branch. The agent can use what the prototype established about APIs and other systems when building the model.

## From model to code

Modelling stops after the model; implementation is a separate request.

### 1. Review and approve

For a strict model, start a **fresh agent session in the same project** so the reviewer has not participated in writing it. Review is optional for standard models.

```text
/ddd-model-review docs/domain/contexts/ordering.md
```

The reviewer reports findings; it does not automatically rewrite or approve the model. Bring its findings back to your modelling session:

```text
Use ddd-modelling to address these review findings in
docs/domain/contexts/ordering.md: [paste the findings].
```

Answer any outstanding business questions. If review found blockers, return to the review session to check the fixes; a review with no blockers needs no further round. Once no blockers are left, the agent adds `reviewed <date>` to the `Status:` line, so later sessions don't ask for the review again. A later change inside a strict scope needs a review of the changed rows only, not of the whole model. When you have read the resulting model and are satisfied, tell the modelling agent:

```text
I approve docs/domain/contexts/ordering.md.
```

You can resume with `ddd-modelling` in a new session if the original session is no longer available. Approval is yours; the agent records it in the context file's `Status:` line with a date and hash. At standard depth, approval includes accepting the listed assumptions you have not corrected.

### 2. Implement

Optionally run `/ddd-to-tickets` to turn the approved model into tickets, with its examples and rules as acceptance criteria. It generally creates one per command, or one for a small aggregate. Tickets are not required to start coding. In model-only projects, tickets follow your project's existing structure and test setup.

In the same or a new project session, name the command and model:

```text
Use ddd-implementation to implement PlaceOrder from
docs/domain/contexts/ordering.md.
```

Implementation works one command at a time, writes tests from the model's examples, then implements the types, decisions and surrounding code in the style chosen during setup. Installing cards selects their typed style; model-only projects keep their own style. Later skills reuse that choice. It runs compile, lint and tests using the applicable project tooling. When working from a ticket, separate adapter, storage and property-test tickets remain separate. A draft or changed model needs approval before implementation proceeds.

Code in an area that has no model is not blocked: the agent makes the change in the surrounding style and mentions that the area can be modelled. Modelling starts when you ask for it, or when a change adds a new context, aggregate or lifecycle.

### 3. Review the code

Work on a branch and commit the changes to review, then ask:

```text
/ddd-review-all Review this branch against main.
The task is: [link or path to the original task].
```

Replace `main` with your base branch. With no preferred base, the reviewer uses the point where your branch diverged from the default branch. Only committed changes are reviewed. The task review needs the original task; it is skipped if you have none.

`ddd-review-all` runs `ddd-review`, `secure-by-design-review` and `task-review` in separate subagents and temporary Git worktrees, with the project's dependencies installed there. If your agent cannot start subagents, run those skills individually (`/ddd-review`, `/secure-by-design-review`, `/task-review`), each in a fresh session, giving them the same base branch and task.

The combined report ends with the next step:

- **No blockers:** merge. Fix should-fix findings and notes without another review round, or turn them into tickets. Then move on to the next ticket or command.
- **Blockers:** fix and commit, then run `/ddd-review-all` again. It starts only the reviewers that found blockers, and each checks just the fix commits against its earlier report instead of reviewing everything again.
- **A gap in the model:** take it to `ddd-modelling` rather than fixing it in code.

### When implementation finds a gap

At standard depth, the agent can resolve smaller gaps, test the decision, and record it under `## Amendments` in the context file. A missing state, command, invariant or permission rule still needs your input, as does a guess that could lose money or data, expose something, or be hard to undo. At strict depth, including strict commands inside a standard context, smaller gaps also stop for clarification and model reapproval before implementation.

To fold those amendments into the model later:

```text
Use ddd-modelling to fold the ordering amendments into the model.
```

You'll approve the updated model once the changes are incorporated. Changes to the approved model require reapproval; implementation stops if its recorded hash no longer matches. That check needs the hash in the `Status:` line; an approval recorded without one is accepted with a warning and cannot be verified. The `Status:` line and the trailing `## Amendments` / `## Migration` sections are excluded from the hash, so recording implementation findings or updating the migration plan does not invalidate approval. Implementation reads amendments alongside the approved rules.

All model sections must precede that notes tail; the tools reject a `#` or `##` heading placed after it. The hash does not cover the glossary or context map. When a shared definition or relationship changes the meaning of an approved rule, the agent shows the impact, updates the affected context and asks for reapproval.

The checker requires every section of the template (write `None.` where a section has nothing) and covers selected structural references, matrix agreement, unique example numbers and command/decision-failure example mentions. Example numbers are permanent, because tests and tickets refer to them. It does not prove reachability from creation, validate payloads or outside-fact trust rules, cover use-case failures or every glossary term, or judge whether examples follow the rules. Those remain agent review and business judgment, at the chosen depth.

## Optional integrations

If you have [Matt Pocock's skills](https://github.com/mattpocock/skills) installed, the kit uses `grilling` for interviews and `tdd` for the failing-test-to-passing-code loop. Neither is required. The glossary uses a shared `GLOSSARY.md` format so other skills can read and extend the same business terminology.

## Manual setup and compatibility

After installing the skills, you can copy project files manually instead of running `/ddd-setup`. From this clone, choose one command (the target must already be a Git repository):

```sh
skills/ddd-setup/install.sh --lang go,ts /path/to/your-project
skills/ddd-setup/install.sh --lang none /path/to/your-project
skills/ddd-setup/install.sh --model-only /path/to/your-project
```

The first installs the full kit for both languages; use `--lang go` or `--lang ts` for one. The second installs cards without examples, and the third installs only the model templates and tools. Without flags, the script detects languages from `go.mod` and `tsconfig.json`; for an empty project, select them explicitly.

The script copies the resources and, when installing cards, adds `.cards-check/` to `.gitignore`. You still need to record the code style and code/test locations in your project's agent instructions. If installing lint configs, merge the rules from the target repository's `tools/lint/` into your own configs and set the `DOMAIN-PATHS` placeholders there to your domain directories. Leave the copies in `tools/lint/` unchanged: `tools/check-cards.sh` uses them to check the card examples.

Older models without a `Depth:` line are treated as strict during implementation and model review.

## What's included

| Skill | Purpose |
|---|---|
| [`ddd-setup`](skills/ddd-setup/SKILL.md) | Install templates, pattern cards, tools and lint configs. |
| [`ddd-modelling`](skills/ddd-modelling/SKILL.md) | Build a model through questions, or derive one from existing code. |
| [`ddd-model-review`](skills/ddd-model-review/SKILL.md) | Check the model for missing rules, contradictions and possible abuse. |
| [`ddd-to-tickets`](skills/ddd-to-tickets/SKILL.md) | Turn an approved model into implementation tickets. |
| [`ddd-implementation`](skills/ddd-implementation/SKILL.md) | Implement the model and its tests. |
| [`ddd-review`](skills/ddd-review/SKILL.md) | Check code against the model. |
| [`secure-by-design-review`](skills/secure-by-design-review/SKILL.md) | Review domain code using the Secure by Design checklist. |
| [`task-review`](skills/task-review/SKILL.md) | Check code against the requested task. |
| [`ddd-review-all`](skills/ddd-review-all/SKILL.md) | Run all three code reviews in isolated subagents. |

The full setup supplies these resources; modelling fills in the context files:

```text
docs/domain/         Context map, model template and your context files
docs/ddd/cards/      20 pattern cards, with example directories for selected languages
tools/               Model checker, approval hashing, card checks and lint configs
```

Modelling creates `GLOSSARY.md` when the first term is agreed. Projects with multiple glossaries use a root `GLOSSARY-MAP.md` to link them.

## Developing the kit

`evals/` and `tests/` are for testing the kit itself, not for using it. Don't copy them into your project. `tests/` checks the scripts (`python3 -m unittest discover -s tests`), and `evals/` measures whether the skills do what they claim, against fixed fixtures and answer keys; see [evals/README.md](evals/README.md).
