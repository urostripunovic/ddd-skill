---
name: ddd-modelling
description: "Model business rules with DDD before code, or derive a model from existing code: bounded contexts, states, commands, events, invariants, with worked examples. Use when the user asks to model a flow or its business rules, asks for DDD, or designs or changes domain behaviour in a repository that has docs/domain/. Not for terminology alone (one term, the glossary, an ADR): that is Matt Pocock's domain-modeling."
---

# DDD modelling

Produce a domain model the user approves. Write no implementation code in this skill.

The reason for the hard stop: a wrong business rule is cheap to fix in a model and expensive to fix in code. Agents tend to fill gaps while implementing; this skill makes those decisions visible first. How the code is then written is not this skill's concern.

Read [lifecycle/depth.md](lifecycle/depth.md) and [lifecycle/notes-tail.md](lifecycle/notes-tail.md) first; read [lifecycle/approval.md](lifecycle/approval.md) and [lifecycle/checker.md](lifecycle/checker.md) before step 6. They define depth, the core and the rest, strict scope, approval, the notes tail and the checker's limits, and this file does not repeat them. Whether or not you open them, these hold:

- Only the user approves a model. On a clear yes about the model ("I approve", "approved"), write `Status: approved <date>` and carry on; never write it without one.
- A strict model, or one with strict commands, is reviewed in a fresh session (`ddd-model-review`) before approval.
- Never mark the core (states, commands and who may issue them, what makes callers and outside facts trusted, invariants, aggregate boundaries, glossary) `(assumed)`, and never fill it with a placeholder.

## Is this repository using the kit?

Carry on with the request without this skill, and say in one line what it could do, when:

- `docs/domain/` does not exist and the user did not ask for a domain model or for DDD: name `ddd-setup` and this skill
- the request falls inside a prototype scope ([lifecycle/adoption.md](lifecycle/adoption.md)) and the user did not ask to model or adopt it: say that modelling was postponed for that scope
- the request changes existing code in an area with no model, and creates no new context, aggregate or lifecycle: say that the area can be modelled; `ddd-implementation` handles the change

## Which mode

- **Building a model**: asked to model something new, or to change a model. Follow this file.
- **Adopting existing code**: optional, and only when the user asks for it. It derives a draft model from the code that is already there. When domain code exists with no model and the user has not said which they want, ask once: derive a draft from the code, or model from the interview alone. If they choose the code, read [ADOPTING.md](ADOPTING.md) and follow it; it uses [INTERVIEW.md](INTERVIEW.md) and [NOTATION.md](NOTATION.md). Otherwise follow this file, and treat the existing code as one more source of facts. That includes a spike on another branch: if the user tried the technology first, ask where, read it for what it showed is possible and how the outside systems behave, and do not treat its structure as something to keep.
- **Reviewing a model**: that is the `ddd-model-review` skill, in a fresh session.

## How deep

A model is worth what it saves later, and no more. This file describes **standard** depth: you ask about the core and propose the rest. The depths and what each settles are in lifecycle/depth.md. Reuse the recorded depth when resuming. For a new model, use the depth the user requested; otherwise use standard, or strict when the work is strict by that file's table, and say which in one line of the first round so the user can change it. Write it on the context file's `Depth:` line.

- **Strict**: read [STRICT.md](STRICT.md) before the interview. It says what each step below does differently at strict depth.
- **Strict commands**: when part of a standard context is strict, write `Strict commands: ChargePayment, RefundPayment` under `Depth:`, using command names from the model, and show the user the strict scope `tools/check-model.sh` prints for each. Omit the line when there are none. STRICT.md applies inside those scopes.
- **None (a spike)**: do not model. Record the named scope and code paths, if known, under `## Prototypes` in `docs/domain/context-map.md` (or the agent instructions, without a map). Say in one line that the code can be adopted later with [ADOPTING.md](ADOPTING.md), and carry on with the request without this skill.

## Output

- `GLOSSARY.md` at the repository root: the glossary, the ubiquitous language
- `docs/domain/context-map.md`: bounded contexts and how they relate
- `docs/domain/contexts/<context>.md`: one file per context, following `contexts/_template.md`

If the templates are missing, tell the user to run `ddd-setup`. `tools/check-model.sh` reads the context file, so its headings, table columns and notation must be the template's.

If any of these already has content, read it first and extend it. Do not start over or rename existing terms without asking.

### The glossary is shared

Other skills read and write the same `GLOSSARY.md`, among them Matt Pocock's `domain-modeling` and `tdd`, so its name and format are fixed. Read [GLOSSARY-FORMAT.md](GLOSSARY-FORMAT.md) before the first write to it. A term is written the moment it is settled, with no separate approval step.

## Write as you go

Do not hold the model in the conversation until the end. A long interview can be cut off, and everything not yet written is lost.

- Create the context file with `Status: draft` as soon as you know which context you are in.
- The moment a term is settled, write it to the glossary. The moment a state, command, invariant or example is settled, write it to the context file.
- Anything asked but not yet answered goes under open questions straight away.
- After each write, tell the user in one line what was recorded.

If you are resuming, read the glossary and `docs/domain/` first and continue from what is there and from its open questions.

## 1. Interview

Read [INTERVIEW.md](INTERVIEW.md) now and follow it. The model is found in this step; the later steps only write it down. At standard depth, whether or not you open it, these hold:

- Ask about the core. Propose the rest, marked `(assumed)`.
- End every round with a checkpoint: the flow as it stands, numbered, and under it what is still unclear. The next round is about the unclear points and nothing else.
- About three rounds. Then say what is still unclear and ask whether to go on or to continue with it under open questions.
- Never invent a domain fact to fill a gap. An unconfirmed proposal goes under open questions as an assumption.

## 2. Bounded contexts

Split where one of these holds:

- a term changes meaning
- the rules or lifecycle of the same thing differ
- different people own the decisions

Do not split by technical layer or by database table. For a small domain, one context is a valid answer; say so instead of inventing boundaries.

Then two questions for the context map. The cards in `docs/ddd/strategic/` quote Evans and the DDD Crew on each answer; read the README and the cards you need, and describe the patterns to the user in the cards' words, not your own.

- **What kind is each context?** Ask the canvas's question, "How important is this context to the success of your organisation?", with its three answers: core, supporting or generic.
- **What pattern is each relationship?** For every row in Relationships, describe the patterns that could fit and let the user say which describes how the teams actually work. Evans: "Map the existing terrain. Take up transformations later." Who owns each side, and whether one team plans for the other's needs, are facts about teams: ask, and do not infer them from the code.

A kind, pattern or owner the user has already stated is answered: write it into the map and ask only for what is missing. With one context and no relationships, write the Kind as your proposal, marked `(assumed)`, and do not ask. When one person or team owns both sides of a relationship, do the same for its Pattern. In each Relationships row, What crosses the boundary lists glossary terms, comma-separated, not prose: `tools/check-model.sh` looks for each in the glossary of the side it belongs to.

The cards give no rule for which pattern to choose. Do not add one. If the strategic cards are not installed, ask the same two questions without them.

## 3. Model each context

Read [NOTATION.md](NOTATION.md) before the first write to a context file: `tools/check-model.sh` reads the notation, so it must be the template's. The notation describes legal business states and says nothing about how the code is written.

Write the flow first: the model told as a story at the top of the context file, five to fifteen numbered sentences in the order things happen, each naming its command. It is what a person reads; the tables are what they look things up in.

## 4. Model it twice

Aggregate boundaries are the part of a model that is hardest to change later, and the first boundary that comes to mind is usually the nouns in the conversation. Before settling them, look for a second candidate whenever one of these holds:

- there is a rule across aggregates
- an aggregate holds a list that grows without a limit
- two groups of commands touch different parts of the same aggregate

Put it to the user as one question: the two candidates, what each makes easy or hard, and your recommendation. Record the answer under Decisions.

When only one boundary is plausible, say so in one line and move on.

## 5. Security pass on the model

Security problems are cheapest to remove at modelling time. Who may issue each command, and on whose data, is the core and is always asked. Propose the other answers, marked `(assumed)`.

- Does every primitive have an upper bound and an allowed character set or format?
- For every command: who may issue it, and on whose data?
- Which values are sensitive (credentials, personal data, payment data)? Mark them. They must not appear in events, errors or logs later.
- Can any numeric value be negative, zero or huge in a way the business never intended?
- What could someone do within the rules that the business never intended: the same discount twice, a reservation that is never used, an order placed and cancelled in a loop?

## 6. Check, write, stop

The files are already written.

1. Run `tools/check-model.sh` on each context file and fix structural errors. Then read what it does not check (lifecycle/checker.md) yourself at the effective depth; propose improvements rather than treating every missing detail as a blocker.
2. Present the model for approval as its flow, not as its tables: the numbered steps, and under each step only what the user has to decide or might not expect. Then the open questions, with the unanswered core questions (who may issue a command, what makes a caller or fact trusted, an invariant) first and apart from the rest: the model cannot be approved until those are answered. After them, everything marked `(assumed)` in one compact list: "correct any of these; the rest stand". The user skims it; do not turn the list into questions. Do not paste tables into the conversation; the user can open the file.
3. Offer no review, unless the context is strict or has strict commands (STRICT.md). The user can run `ddd-model-review` at any time.

When the user brings back a review's findings, apply them. Once the review has no blockers left, add `, reviewed <date>` to the Status line, so a later session does not ask for the review again.

Never ask again for something the user has answered. An answer is written to the model the moment it is given, in the section it affects, and later rounds, reviews and sessions read it there. Only a choice that meets the three conditions under **Decisions** in NOTATION.md also gets a Decisions row.

Approval follows lifecycle/approval.md: ask, and on the user's yes write `Status: approved <date>`. If the approved model adopts a scope listed under `## Prototypes`, remove that row in the same step, or narrow it to the part still unmodelled.

Then carry on with what the user asked for. If that includes the code, hand over to `ddd-implementation` now, without asking again; otherwise say in one line that implementation is the next step. This skill itself writes no implementation code.

## Changing a model

When the context file has rows under `## Pending`, settle them first: each is a question implementation is waiting on. A new rule, state, command or term always goes through the model first. At standard depth, a change to only the rest of an approved model is an `## Amendments` row and the approval stands; a change to the core sets it back to draft. For pending rows, amendments and small changes, read [CHANGING.md](CHANGING.md).
