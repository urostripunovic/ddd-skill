---
name: ddd-modelling
description: "Model business rules with DDD before code, or derive a model from existing code: bounded contexts, states, commands, events, invariants, with worked examples. Use when the user asks to model a flow or its business rules, asks for DDD, or designs or changes domain behaviour in a repository that has docs/domain/. Not for terminology alone (one term, the glossary, an ADR): that is Matt Pocock's domain-modeling."
---

# DDD modelling

Produce a domain model the user approves. Write no implementation code in this skill.

The reason for the stop: a wrong business rule is cheap to fix in a model and expensive to fix in code. Agents tend to fill gaps while implementing; this skill makes those decisions visible first. The stop is for the core. At standard depth, everything else is written as a proposal marked `(assumed)` and listed once; it never holds the work up, and approval is asked again only when the core changes (lifecycle/approval.md). How the code is then written is not this skill's concern.

Read [lifecycle/depth.md](lifecycle/depth.md) first, for depth, the core and the rest, and strict scope. Read the others at the step that needs them: [lifecycle/triggers.md](lifecycle/triggers.md) at step 1, [lifecycle/approval.md](lifecycle/approval.md) and [lifecycle/checker.md](lifecycle/checker.md) before step 6, and [lifecycle/notes-tail.md](lifecycle/notes-tail.md) before writing to a context file's notes tail. This file does not repeat any of them. Whether or not you open them, these hold:

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
- **Adopting existing code**: optional, and only when the user asks for it. It derives a draft model from the code that is already there. When domain code exists with no model and the user has not said which they want, ask once: derive a draft from the code, or model from the interview alone. If they choose the code, read [ADOPTING.md](ADOPTING.md) and follow it; it uses the interview and the notation from this file. Otherwise follow this file, and treat the existing code as one more source of facts. That includes a spike on another branch: if the user tried the technology first, ask where, read it for what it showed is possible and how the outside systems behave, and do not treat its structure as something to keep.
- **Reviewing a model**: that is the `ddd-model-review` skill, in a fresh session.

## How deep

A model is worth what it saves later, and no more. This file describes **standard** depth: you ask about the core and propose the rest; depth.md has the others and what each settles. Reuse the recorded depth when resuming. For a new model, use the depth the user requested, otherwise standard, or strict when the work is strict by depth.md's table, and say which in one line of the first round so the user can change it. Write it on the context file's `Depth:` line.

- **Strict**: read [STRICT.md](STRICT.md) before the interview. It says what each step below does differently at strict depth.
- **Strict commands**: when part of a standard context is strict, write `Strict commands: ChargePayment, RefundPayment` under `Depth:`, using command names from the model, and show the user the strict scope `tools/check-model.sh` prints for each. Omit the line when there are none. STRICT.md applies inside those scopes.
- **None (a spike)**: do not model. Record the named scope and code paths, if known, under `## Prototypes` in `docs/domain/context-map.md` (or the agent instructions, without a map). Say in one line that the code can be adopted later with [ADOPTING.md](ADOPTING.md), and carry on with the request without this skill.

## Output

- `GLOSSARY.md` at the repository root: the glossary, the ubiquitous language
- `docs/domain/context-map.md`: bounded contexts and how they relate
- `docs/domain/contexts/<context>.md`: one file per context, following `contexts/_template.md`

If the templates are missing, tell the user to run `ddd-setup`. `tools/check-model.sh` reads the context file, so its headings, table columns and notation must be the template's.

If any of these already has content, read it first and extend it. Do not start over or rename existing terms without asking.

The glossary is shared with other skills, so its name and format are fixed, and a term is written the moment it is settled: [glossary.md](glossary.md).

## Write as you go

Do not hold the model in the conversation until the end. A long interview can be cut off, and everything not yet written is lost.

- Create the context file with `Status: draft` as soon as you know which context you are in.
- The moment a term is settled, write it to the glossary. The moment a state, command, invariant or example is settled, write it to the context file.
- Anything asked but not yet answered goes under open questions straight away, and comes back out when it is answered: the answer goes in the section it affects, and the item is removed in the same step.
- After each write, tell the user in one line what was recorded.

If you are resuming, read the glossary and `docs/domain/` first and continue from what is there and from its open questions.

## 1. Interview

You do not know this domain. The user or their domain expert does. The model is found in this step; the later steps only write it down, so do not hurry through it. The interview comes before the code at every depth. What changes with depth is how much of it comes first: at standard depth, ask what the work in front of you needs, and come back when the work raises more (lifecycle/triggers.md).

- **Ask about the core. Propose the rest.** For a bound, a payload, a race or an edge case, write your best guess into the model marked `(assumed)` and do not ask. Ask about something in the rest only when a wrong guess would lose money or data, expose something, or be hard to undo. Never mark the core `(assumed)`, and never fill it with a placeholder such as "TBD": `tools/check-model.sh` rejects an assumed or placeholder "Issued by" cell, invariant or "Believed when" cell. A core question still unanswered goes under open questions, and the model does not pass the check until the user answers it.
- **Stop after each round that has questions.** When every core question for this work is answered, do not stop for the rest: write it `(assumed)` and go on to step 6. End every round with a checkpoint of a few lines: the flow as it stands now, numbered, and under it what is still unclear. The user reads the flow and says where it is wrong. The next round is about the unclear points and nothing else; do not open new subjects while one is unclear.
- **Ask about the work in front of you.** Collect the whole timeline, which is cheap, but go deep only on the commands this work needs: the user's flow, or the change they asked for. For those, ask the core always and the rest only where lifecycle/triggers.md's triggers apply. Usually one or two rounds; if the core is not settled after about three, say what is still unclear and ask whether to go on or to continue with it under open questions. Do not keep asking to reach completeness. Later work that raises a new question comes back here for that question alone, and does not reopen the rest.

**How to ask.** If a skill named `grilling` is available, call the Skill tool with "grilling" and use the rest of this section as what to grill about; it supplies the format of a round. This file decides what to ask and when to stop: the work in front of you, the triggers, and the rest proposed and marked `(assumed)`, take precedence over grilling's rule that the session ends when every branch is visited. If it is not, ask this way:

- Work in rounds. A round holds every question you can ask now without guessing an answer you have not heard yet. Number the questions, and wait for the answers before the next round.
- Give a proposed answer with every question. Correcting a proposal is quicker for the user than composing an answer.
- Facts are yours to find; decisions are the user's. Read what the repository can already answer (the glossary, `docs/domain/`, `docs/adr/`, code, schemas, API specifications, a ticket the user points to) before asking. What the code does today is a fact. Whether the business intends it is a decision. A decision the user has already stated, in the request or earlier, is answered: write it without `(assumed)` and do not ask it again.

Whichever way you ask: a proposal is not a fact. If the user does not confirm it, it goes under open questions as an assumption. Never invent a domain fact to fill a gap. Use the user's words, not DDD jargon.

**Follow the timeline first.** People describe their business as things that happen, so open with the events: "what happens first, and then?" Collect the whole sequence before going deep on any part of it.

**Then ask who owns each part.** "Is any of this decided by another model, team or system?" A part with its own model is another context: put it on the context map and model only what crosses the boundary.

**Then one event at a time**, for the events this work needs. For each: what triggers it, who may trigger it and on whose data, what must be true before, what can go wrong, which data it needs that lives somewhere else, and who needs to know that it happened.

**Ask what the timeline hides, where a trigger applies.** A timeline shows one thing after another, done by people, to one thing. Five kinds of question find the rest — reactions, time, races, edges and consistency — and [interview.md](interview.md) asks each of them, with the examples, the matrix and the bounds they write down. Ask each for a command this work needs when lifecycle/triggers.md says the command raises it; **Edges** is the core and is always asked. Challenge the wording as it happens rather than noting it for later: if a skill named `domain-modeling` is available, call the Skill tool with "domain-modeling" at the start of the interview, and the glossary rules under **Output** still hold.

**The interview is done when** the timeline is whole, and for the commands this work needs every state and command is named with who may issue it, every caller and outside fact says what makes it trusted, every invariant is stated with one example, and every trigger they raise has its answer, proposed or confirmed. Ask whether anything is missing from the timeline at the end of the last checkpoint; the answer comes with the user's corrections. If the person who would know is not available, leave the item under open questions and do not keep asking.

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

Use the template's notation, so the model reads the same in every language and `tools/check-model.sh` can read it. The notation describes legal business states and says nothing about how the code is written: it does not ask for one code type per state.

```
type Order = DraftOrder | PlacedOrder | CancelledOrder
terminal CancelledOrder

DraftOrder  = { id: OrderId, items: Item[] }
PlacedOrder = { id: OrderId, items: Item[] (at least 1), placedAt: Timestamp }

StartOrder  : () -> DraftOrder
PlaceOrder  : DraftOrder -> PlacedOrder + [OrderPlaced] | EmptyOrder
CancelOrder : DraftOrder | PlacedOrder -> CancelledOrder + [OrderCancelled]
```

- **Notation**, which `tools/check-model.sh` reads: `Timestamp` and `Boolean` are built in; every other type is a primitive or is defined in the States block. `terminal` lists the states nothing leads out of. A command that creates the aggregate starts from `()`. Under the States block, one line per state that is not terminal says what ends it if nothing happens, or "no expiry". The Commands table's **Input** lists the values a command takes that are not in its starting state, as `name: Type`, or `none`; a command that time issues names the scheduler and the delay under **Issued by**. The matrix has one row per state and one column per command, without the creating commands. A section with nothing in it says `None.`
- **The flow**: the model told as a story, at the top of the context file: five to fifteen numbered sentences in the order things happen, each naming its command. Write it first, from the timeline, and keep it true as the model changes. It is what a person reads; the tables are what they look things up in.
- **Each section's own rules** — what Domain primitives, States, Commands, Matrix, Events, Invariants, Failures, Use-case failures, Examples, Races, Facts from outside, Aggregates, Rules across aggregates and Policies each hold — are in [sections.md](sections.md). Read it while writing a section.
- **Keep a cell a cell.** A table cell states the rule and the one reason for it, in a sentence or two. Anything longer is a derivation, and a derivation goes in a `## Decisions` row the cell names, or in a paragraph under the table; `tools/check-model.sh` warns past sixty words. The flow is what a person reads and the tables are what they look things up in, so a cell that has to be read twice has stopped doing its job.
- **Decisions**: the model says what was decided; this section says why. Record a decision only when all three hold: it is hard to reverse, a later reader would be surprised by it, and a real alternative was rejected. Only decisions about the domain go here: a rule, a boundary, a split between contexts. They are part of the approved model, so changing one means approving again. A technical decision (storage, a framework, event sourcing, deployment) is an ADR in `docs/adr/`, as Matt Pocock's `domain-modeling` writes them, and not a Decisions row.

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
2. Present the model for approval as its flow, not as its tables: the numbered steps, and under each step only what the user has to decide or might not expect. Then the open questions, with the unanswered core questions (who may issue a command, what makes a caller or fact trusted, an invariant) first and apart from the rest: the model cannot be approved until those are answered. After them, everything marked `(assumed)` in one compact list: "correct any of these; the rest stand". The user skims it; do not turn the list into questions. At standard depth this is the one approval the model needs until its core changes: say so when asking, so the user knows later work will not stop for the rest. Do not paste tables into the conversation; the user can open the file.
3. Offer no review, unless the context is strict or has strict commands (STRICT.md). The user can run `ddd-model-review` at any time.

When the user brings back a review's findings, apply them. A path is the usual way they arrive: apply `<round>.patch` with `git apply` once `git apply --check` passes, and read `<round>.md` for the verdict, the proposed changes and the questions — not the whole context file, whose strings the patch already carries. Read a part of the model only for a finding the patch does not settle, and put the blockers the report says need the user's word to them, each with the report's proposed answer. Once the review has no blockers left, add `, reviewed <date>` to the Status line, so a later session does not ask for the review again.

Never ask again for something the user has answered. An answer is written to the model the moment it is given, in the section it affects, and later rounds, reviews and sessions read it there — and the open-questions item it answers is removed in the same step, so that section holds what is still unanswered and nothing else. An answered item kept as a record is a second copy of the model's own rows, and the record of what a round asked is already committed in `docs/domain/reviews/`. Only a choice that meets the three conditions under **Decisions** also gets a Decisions row.

Approval follows lifecycle/approval.md: ask, and on the user's yes write `Status: approved <date>`. If the approved model adopts a scope listed under `## Prototypes`, remove that row in the same step, or narrow it to the part still unmodelled.

Then carry on with what the user asked for. If that includes the code, hand over to `ddd-implementation` now, without asking again; otherwise say in one line that implementation is the next step. This skill itself writes no implementation code.

## Changing a model

When the context file has rows under `## Pending`, settle them first: each is a question implementation is waiting on. A new rule, state, command or term always goes through the model first. At standard depth, a change to only the rest of an approved model is an `## Amendments` row and the approval stands; a change to the core sets it back to draft. For pending rows, amendments and small changes, read [CHANGING.md](CHANGING.md).
