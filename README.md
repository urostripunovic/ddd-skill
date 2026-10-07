# Typed DDD skills

Skills for working out business rules with a coding agent before writing the code. The agent interviews you, writes a domain model in Markdown, and once you approve it, turns the model's worked examples into tests.

The code follows domain-driven design (DDD) in the functional style of Scott Wlaschin's *Domain Modeling Made Functional*: named types for domain values, a type for each state, and pure functions for business decisions, with examples and lint rules for Go and TypeScript. You can also keep your own code style and use only the modelling workflow.

Everything not on this page is in the [reference](REFERENCE.md).

## Quickstart

**1. Install the skills.** Clone this repository, and from its root copy the skills into your project, or into `~/.claude/skills/` for all your projects. Claude Code and OpenCode both read these locations.

```sh
mkdir -p /path/to/your-project/.claude/skills
cp -r skills/. /path/to/your-project/.claude/skills/
```

**2. Set up your project.** In a session at your project's root:

```text
/ddd-setup
```

It asks how much of the kit you want, copies the templates and tools, records your code style, and reports missing tools. It never overwrites a file. In OpenCode, write `@ddd-setup`; the same goes for every `/` command below.

**3. Model one flow.** Describe what people do; you don't need to know any DDD terms.

```text
Use ddd-modelling at standard depth to model the ordering flow,
from adding the first item to placing or cancelling the order.
```

The agent asks questions in rounds, each with a proposed answer, and writes the model as you go.

**4. Approve it.** Read the model it shows you. When it is right:

```text
I approve docs/domain/contexts/ordering.md.
```

Setup records who may approve (`Approvers:` in `CLAUDE.md`). With more than one name there, add `Approver: <your name>`.

For money, credentials, personal data or anything hard to undo, model at `strict` depth and review it in a fresh session first: `/ddd-model-review docs/domain/contexts/ordering.md`.

**5. Implement one command.**

```text
Use ddd-implementation to implement PlaceOrder from
docs/domain/contexts/ordering.md.
```

It writes the model's examples as tests first, then the code, and runs compile, lint and tests.

**6. Review the code.** Commit on a branch, then:

```text
/ddd-review-all Review this branch against main.
```

**Not sure what comes next?** Ask "what's next?" at any point. `ddd-next` reads the state of the repository and gives the one next step, with the prompt to type.

## The skills

| Skill | Starts | Purpose |
|---|---|---|
| [`ddd-next`](skills/ddd-next/SKILL.md) | when asked in plain words | Say where the repository is in the workflow and the one next step |
| [`ddd-setup`](skills/ddd-setup/SKILL.md) | by name | Install templates, cards, tools and lint rules |
| [`ddd-modelling`](skills/ddd-modelling/SKILL.md) | when asked in plain words | Build a model through questions, or derive one from existing code |
| [`ddd-model-review`](skills/ddd-model-review/SKILL.md) | by name | Check a model for missing rules, contradictions and possible abuse |
| [`ddd-to-tickets`](skills/ddd-to-tickets/SKILL.md) | by name | Turn an approved model into tickets |
| [`ddd-implementation`](skills/ddd-implementation/SKILL.md) | when asked in plain words | Implement the model and its tests |
| [`ddd-review`](skills/ddd-review/SKILL.md) | by name | Check code against the model |
| [`secure-by-design-review`](skills/secure-by-design-review/SKILL.md) | by name | Review domain code with the Secure by Design checklist |
| [`task-review`](skills/task-review/SKILL.md) | by name | Check code against the task that asked for it |
| [`ddd-review-all`](skills/ddd-review-all/SKILL.md) | by name | Run the three code reviews in isolated subagents |

The skills are opt-in per repository: in a project without `docs/domain/`, they stay out of the way. Setup and the reviews never start on their own.

## Learn more

- [Reference](REFERENCE.md): setup options and prerequisites, depth, starting from existing code, approval, tickets, gaps found during implementation, the context file, and the cards
- [Strategic cards](skills/ddd-setup/kit/docs/ddd/strategic/README.md): how contexts relate, quoted from Eric Evans' *DDD Reference* and the DDD Crew
- [Pattern cards](skills/ddd-setup/kit/docs/ddd/cards/functional/README.md): how domain code is written in the functional style
- [Evals](evals/README.md): how the skills are tested
