---
name: ddd-modelling
description: "Model business rules with DDD before code, or derive a model from existing code: bounded contexts, states, commands, events, invariants, with worked examples. Typed implementation patterns are optional. Use when the user asks for a domain model or for DDD, or when domain behaviour is designed or changed in a repository that has docs/domain/."
---

# DDD modelling

Produce a domain model the user approves. Write no implementation code in this skill.

The reason for the hard stop: a wrong business rule is cheap to fix in a model and expensive to fix in code. Agents tend to fill gaps while implementing; this skill makes those decisions visible first. The project's choice of code style is separate.

## Is this repository using the kit?

If `docs/domain/` does not exist and the user did not ask for a domain model or for DDD, this repository has not adopted the kit. Say in one line that `ddd-setup` and this skill exist, and carry on with the request without this skill.

If the request falls inside a scope listed under `## Prototypes` in `docs/domain/context-map.md` (or in the agent instructions), and the user did not ask to model or adopt it, say in one line that modelling was postponed for that scope, and carry on without this skill.

A change to existing code in an area that has no model is not a modelling request either, unless the user asks for a model or the change creates a new context, aggregate or lifecycle. Carry on without this skill (`ddd-implementation` handles that case), and mention in one line that the area can be modelled.

## Which mode

- **Building a model**: asked to model something new, or to change a model. Follow this file.
- **Adopting existing code**: optional, and only when the user asks for it. It derives a draft model from the code that is already there. When domain code exists with no model and the user has not said which they want, ask once: derive a draft from the code, or model from the interview alone. If they choose the code, read [ADOPTING.md](ADOPTING.md) and follow it; it uses the interview and the notation from this file. Otherwise follow this file, and treat the existing code as one more source of facts. That includes a spike on another branch: if the user tried the technology first, ask where, read it for what it showed is possible and how the outside systems behave, and do not treat its structure as something to keep.
- **Reviewing a model**: that is the `ddd-model-review` skill, in a fresh session.

## How deep

A model is worth what it saves later, and no more. Reuse the recorded depth when resuming. For a new model, use the depth the user requested; otherwise ask once with your recommendation. Write it on the context file's `Depth:` line.

| Depth | For | What is settled before code |
|---|---|---|
| none (a spike) | finding out whether an idea works; code that may be thrown away | Do not model. Record the named scope and code paths, if known, under `## Prototypes` in `docs/domain/context-map.md` so another session knows modelling was postponed. If the map is absent, record it in the project's agent instructions. This exemption applies only to unmodelled code in that scope. Say that code can be written first and adopted later with [ADOPTING.md](ADOPTING.md), and stop |
| `standard` | most work. Recommend this unless the row below applies | The **core**, confirmed by the user. The rest is your best guess, marked `(assumed)` |
| `strict` | money, credentials, authorisation, personal data, anything that cannot be undone; or when the user asks for it | Everything, confirmed and reviewed |

The **core** is what is expensive to change once code exists: the states, the commands and who may issue each, the invariants, the aggregate boundaries, and the glossary. Everything else is the **rest**: bounds, what a failure or an event carries, races, edge cases, the examples at the limits. A wrong guess in the rest costs one edit to the model and one to the code.

One part of a context may be strict while the rest is standard: write `Strict commands: ChargePayment, RefundPayment` under `Depth:`, using command names from the model. Omit the line when there are none. The **strict scope** of such a command is the command, its failures, the rows that name it (examples, invariants, races, facts from outside, policies) and the primitives of the data it adds. `tools/check-model.sh` prints it for each strict command, so nobody has to work it out; show it to the user when the line is added. The strict scope follows strict depth through review, tickets and implementation. Everything else keeps the context's depth. A missing `Depth:` means strict for older models. When adopting a recorded prototype, remove its row under `## Prototypes` as the draft model is created, or narrow it to the part that is still unmodelled.

The sections below describe the strict interview. **At standard depth** adapt them as follows:

- **Ask about the core. Propose the rest.** For a bound, a payload, a race or an edge case, write your best guess into the model marked `(assumed)` and do not ask. Ask about something in the rest only when a wrong guess would lose money or data, expose something, or be hard to undo.
- **Fill in the matrix yourself.** Write `yes` where the signature allows the command, and for each other cell the likely reason, marked `(assumed)`. Ask only about a cell where the honest answer might be "yes, until…", because that is how a missing state shows, or where a wrong guess would cost money or data. The other reasons go into the list of assumptions.
- **Stop after each round.** End every round with a checkpoint of a few lines: the flow as it stands now, numbered, and under it what is still unclear. The user reads the flow and says where it is wrong. The next round is about the unclear points and nothing else; do not open new subjects while one is unclear.
- **About three rounds.** If the core is not settled by then, say what is still unclear and ask whether to go on or to continue with it under open questions. Do not keep asking to reach completeness.
- **Show the assumptions once.** At the end, list everything marked `(assumed)` in one compact list: "correct any of these; the rest stand". The user skims it. Do not turn the list into questions.

The model grows. What implementation learns comes back as rows under the context file's `## Amendments`, and a later modelling session folds them in.

## Output

- `GLOSSARY.md` at the repository root: the ubiquitous language
- `docs/domain/context-map.md`: bounded contexts and how they relate
- `docs/domain/contexts/<context>.md`: one file per context, following `contexts/_template.md`

If the templates are missing, tell the user to run `ddd-setup`. `tools/check-model.sh` reads the context file, so its headings, table columns and notation must be the template's.

If any of these already has content, read it first and extend it. Do not start over or rename existing terms without asking.

### The glossary is shared

Other skills read and write the same `GLOSSARY.md`, so its format is fixed:

```md
# Ordering

Takes, places and cancels customer orders.

## Language

**Placed order**:
An order the customer has committed to. It has at least one item and a time of placing.
_Avoid_: Submitted order
```

- One or two sentences per term, written so a newcomer can tell it from its neighbours. Business words only: no record, entity, DTO, manager, handler or status.
- When several words exist for one concept, pick one and list the others under `_Avoid_`. The checks search for those words, so a rejected synonym that is not written down will come back.
- With one context, there is one `GLOSSARY.md` at the root. With several, each context has its own `GLOSSARY.md` and a `GLOSSARY-MAP.md` at the root links to them: `- [Ordering](./src/ordering/GLOSSARY.md): one line on what it is`. How the contexts relate stays in `docs/domain/context-map.md`; the map points there.
- Create the file when the first term is settled, not before.
- A term is written the moment it is settled, with no separate approval step. Approval hashes cover context files, not the glossary or context map. When a shared definition or relationship changes, identify the affected contexts and show the impact to the user. If it changes an approved rule's meaning, record that change in the context, set it to draft and get approval again. The checker catches some missing names and rejected synonyms; it cannot detect a change of meaning.

## Write as you go

Do not hold the model in the conversation until the end. A long interview can be cut off, and everything not yet written is lost.

- Create the context file with `Status: draft` as soon as you know which context you are in.
- The moment a term is settled, write it to the glossary. The moment a state, command, invariant or example is settled, write it to the context file.
- Anything asked but not yet answered goes under open questions straight away.
- After each write, tell the user in one line what was recorded.

If you are resuming, read the glossary and `docs/domain/` first and continue from what is there and from its open questions.

## 1. Interview

You do not know this domain. The user or their domain expert does. The model is found in this step; the later steps only write it down, so do not hurry through it.

**How to ask.** If a skill named `grilling` is available, invoke it and use the rest of this section as what to grill about; it supplies the way of asking. If it is not, ask this way:

- Work in rounds. A round holds every question you can ask now without guessing an answer you have not heard yet. Number the questions, and wait for the answers before the next round.
- Give a proposed answer with every question. Correcting a proposal is quicker for the user than composing an answer.
- Facts are yours to find; decisions are the user's. Read what the repository can already answer (the glossary, `docs/domain/`, code, schemas, API specifications, a ticket the user points to) before asking. What the code does today is a fact. Whether the business intends it is a decision.

Whichever way you ask: a proposal is not a fact. If the user does not confirm it, it goes under open questions as an assumption. Never invent a domain fact to fill a gap. Use the user's words, not DDD jargon.

**Follow the timeline first.** People describe their business as things that happen, so open with the events: "what happens first, and then?" Collect the whole sequence before going deep on any part of it.

**Then one event at a time.** For each: what triggers it, who may trigger it and on whose data, what must be true before, what can go wrong, which data it needs that lives somewhere else, and who needs to know that it happened.

**Ask what the timeline hides.** A timeline shows one thing after another, done by people, to one thing. Five kinds of question find the rest:

- **Reactions.** "Whenever this has happened, what has to happen next, and who or what does it?" Each answer is a policy.
- **Time.** For every state that is not final: "what happens if nothing happens, and after how long?" Deadlines, expiry and reminders are commands that a scheduler issues. Write the answer under the States block, one line per state that is not final, including "no expiry".
- **Races.** For every pair of commands that can reach the same thing at the same moment (two browser tabs, a customer and a member of staff, a retry, a person and the scheduler): "which wins, and what is the other told?"
- **Edges.** For every way in and out: "who or what is on the other side, and how do we know?" A model that only says "the customer" has skipped how a request becomes a customer. For each caller: what proves who they are, and what is refused. For each thing received from another system (a sign-in token, a price, a webhook): what must be checked before it is believed, and what happens when it is wrong, late or missing. These are part of the core, because every "who may issue" rule rests on them. The answers go in the context map's relationships and in the context file's **Facts from outside**, and each refusal is a named use-case failure.
- **Consistency.** For every rule that involves more than one thing: "if this were wrong for a few seconds, what would it cost, and who would notice?" The answer decides what belongs in one aggregate.

**Turn every rule into examples.** When the user states a rule, fill it in with real values and ask what happens: one ordinary case, one on each side of every limit, and one for each way it can fail.

```
Rule: orders over 10 000 kr need a manager's approval.
Q3. What happens for each of these?
    a. 9 999 kr              Proposed: placed directly.
    b. exactly 10 000 kr     Proposed: placed directly; "over" means more than.
    c. 8 000 kr plus VAT, which makes 10 000   Proposed: the limit is on the amount including VAT.
```

A rule stated in general terms sounds complete until a specific case hits it. Write the confirmed rows to the context file's Examples table as you go: they are the test cases later. Row numbers are permanent, because tests and tickets refer to them: give a new row the next unused number, never renumber, and leave a gap where a row was removed. Other edges worth an example: it happens twice, it happens late or in the wrong order, it happens partially, the amount is zero or huge, the wrong person does it.

**Fill in the matrix.** Once the states and commands are known, go through every pair. Where the command is not allowed in that state, ask why not, with a proposal: "Can a placed order still receive an item? Proposed: no, because picking has started." An answer like "yes, until it is packed" has just found a missing state.

**Challenge the wording at once.** Do not note a language problem for later.

- One word used with two meanings: stop and ask which is meant. This often marks a context boundary.
- Two words for one thing: propose one. The other goes under `_Avoid_`.
- A term that conflicts with the glossary: quote the entry and ask which is right.
- A name the user would not say out loud to a colleague is the wrong name. Ask what they call it.

**Ask for limits.** How many, how long, how large, which characters. Every primitive needs bounds, and "no limit" is not an answer. At standard depth, propose them all at once ("I will use these unless you object") and mark them `(assumed)`; a bound the user states is theirs and is not marked.

**The interview is done when**, at standard depth, the timeline is whole, every state and command is named with who may issue it, every caller and outside fact says what makes it trusted, every invariant is stated with one example, and the user has seen the list of assumptions. At strict depth, when all of these hold:

- every event on the timeline has its trigger, issuer, preconditions, failures and outside data, each either answered or listed under open questions
- every caller and every outside fact says what makes it trusted and what happens when it is not
- every cell of the matrix is `yes` or has the business's reason
- every command, every failure and every limit has an example the user confirmed
- reactions, time, races and consistency have each been asked about, and each answer is written down, including "none"
- every value with rules has bounds, and every term in use is in the glossary

Then ask the user whether anything is missing from the timeline. Do not move on before they answer. If the person who would know is not available, leave the item under open questions and do not keep asking.

## 2. Bounded contexts

Split where one of these holds:

- a term changes meaning
- the rules or lifecycle of the same thing differ
- different people own the decisions

Do not split by technical layer or by database table. For a small domain, one context is a valid answer; say so instead of inventing boundaries.

## 3. Model each context

Use the template's notation, so the model reads the same for Go and TypeScript and `tools/check-model.sh` can read it:

The state notation describes legal business states, regardless of the implementation language or style. In model-only projects it does not require one code type per state; record enforcement using the project's actual validation mechanisms rather than prescribing a typed refactor.

```
type Order = DraftOrder | PlacedOrder | CancelledOrder
terminal CancelledOrder

DraftOrder  = { id: OrderId, items: Item[] }
PlacedOrder = { id: OrderId, items: Item[] (at least 1), placedAt: Timestamp }

StartOrder  : () -> DraftOrder
PlaceOrder  : DraftOrder -> PlacedOrder + [OrderPlaced] | EmptyOrder
CancelOrder : DraftOrder | PlacedOrder -> CancelledOrder + [OrderCancelled]
```

- **The flow**: the model told as a story, at the top of the context file: five to fifteen numbered sentences in the order things happen, each naming its command. Write it first, from the timeline, and keep it true as the model changes. It is what a person reads; the tables are what they look things up in.
- **Domain primitives**: every value with rules gets a named type with stated bounds, and the reason for each bound. No bare strings or numbers in the model.
- **States**: one type per state, holding only the data that exists in that state. No status field with optional fields.
- **Commands**: a function from the specific state or states it is legal in, to a new state plus events, or a named failure. A command that is illegal in a state is simply not defined for that state's type, so "wrong state" is never listed as a failure of the command.
- **Matrix**: every state against every command. `yes`, or `no:` and the reason the business gave.
- **Events**: past tense, in the ubiquitous language, with the data consumers need.
- **Invariants**: each one names where it is enforced (the type, a constructor, a decision function, or "not in types" with how it is checked instead) and every command that could break it.
- **Failures**: each business failure gets a name and the data needed to explain it.
- **Use-case failures**: "not found", "not allowed" and "not in a state this command accepts" are raised by the workflow, not by a decision. Name them in their own table.
- **Examples**: the confirmed rows from the interview. Values, not descriptions.
- **Races**: which command wins and what the other is told.
- **Facts from outside**: any data a command needs that the aggregate does not hold gets a named type, its source, what is checked before it is believed, what happens when that check fails or the source does not answer, and whether it may be slightly out of date. The caller's identity is such a fact: "Requester", from the sign-in token, believed once its signature, issuer, audience and expiry are checked.
- **Aggregates**: keep them small. Data belongs in the same aggregate only if a rule requires it to change together. Other aggregates are referenced by ID.
- **Rules across aggregates**: immediate or eventual. An immediate rule means the things involved are one aggregate, or a database constraint holds it. An eventual rule names the policy that restores it and what the user sees in the meantime.
- **Policies**: each reaction from the interview: the event, the command it causes, and what happens when that command fails.
- **Decisions**: the model says what was decided; this section says why. Record a decision only when all three hold: it is hard to reverse, a later reader would be surprised by it, and a real alternative was rejected.

## 4. Model it twice

Aggregate boundaries are the part of a model that is hardest to change later, and the first boundary that comes to mind is usually the nouns in the conversation. Before settling them, look for a second candidate whenever one of these holds:

- there is a rule across aggregates
- an aggregate holds a list that grows without a limit
- two groups of commands touch different parts of the same aggregate

Sketch both candidates, with only the state types and command signatures. Run every example and every race from the context file through each. Show the user a short comparison: which examples each candidate needs a policy and a delay for, and which races each makes impossible. The user chooses. Record the choice under Decisions, with the example that decided it.

When only one boundary is plausible, say so in one line and move on.

## 5. Security pass on the model

Security problems are cheapest to remove at modelling time.

- Does every primitive have an upper bound and an allowed character set or format?
- For every command: who may issue it, and on whose data?
- Which values are sensitive (credentials, personal data, payment data)? Mark them. They must not appear in events, errors or logs later.
- Can any numeric value be negative, zero or huge in a way the business never intended?
- What could someone do within the rules that the business never intended: the same discount twice, a reservation that is never used, an order placed and cancelled in a loop?

## 6. Check, write, stop

The files are already written.

1. Run `tools/check-model.sh` on each context file and fix structural errors. It checks that every template section is present (write "None." where a section has nothing), state-field type references, signature/table agreement, incoming/outgoing command mentions, matrix cells, unique example numbers, and example mentions for commands and decision failures, and it prints the strict scope of each strict command. It does not prove reachability, validate payloads or outside-fact trust rules, cover use-case failures, or judge whether examples follow the rules. Read those yourself at the chosen depth; propose improvements rather than treating every missing detail as a blocker.
2. Present the model for approval as its flow, not as its tables: the numbered steps, and under each step only what the user has to decide or might not expect. Then the open questions, and at standard depth the assumptions. Do not paste tables into the conversation; the user can open the file.
3. Review before approval depends on the depth. Strict: tell the user to run `ddd-model-review` in a fresh session. In a standard context with strict commands, that review covers the strict scope; review of the rest is optional. Standard otherwise: offer review as optional, and say that one round is enough unless it finds a blocker in the core.

When the user brings back a review's findings, apply them. At strict depth, a proposed assumption the user accepts is confirmed: write it without the `(assumed)` marker. Once the review has no blockers left, add `, reviewed <date>` to the end of the Status line (it is outside the hash), so a later session does not ask for the review again.

Never ask again for something the user has answered. An answer is written to the model the moment it is given, in the section it affects, and later rounds, reviews and sessions read it there. Only a choice that meets the three conditions under **Decisions** also gets a Decisions row.

When the user approves a context file, run `tools/model-hash.sh <file>` and set its status line to `Status: approved by <name> on <date>, model-hash <hash>`, keeping a `, reviewed <date>` at the end if it was there. The hash covers the context's approved body, excluding the status line and trailing notes. Approval at standard depth means the user has confirmed the core and seen the assumptions; say so when you ask for it. Never write an approved status the user did not give. After a later edit to the approved part, set the status back to `draft`. Keep `## Migration` and `## Amendments` at the end, after all model sections. The hash leaves this tail out, so recording findings or updating the migration plan does not undo an approval; model sections after it are an error.

Stop here. Implementation is a separate step with the `ddd-implementation` skill.

## Folding in amendments

When the context file has rows under `## Amendments`, and the user asks to bring the model up to date or wants a larger change, fold them in first: move what each row learned into the section it names, remove the row, and show the whole change as one diff. An amendment that touched only the rest needs no discussion. One that turns out to change the core (a new state, a command, an invariant, who may issue) is put to the user as a question. Then the user approves again, once, for all of them.

## When the request is small

For a change to an existing model, update only the affected sections, including the matrix column or row and the examples the change touches. Show the change as a diff, run `tools/check-model.sh`, and still wait for approval. A new rule, state, command or term always goes through the model first.

A change inside the strict scope of a model that was already reviewed needs a review of the changed rows only: give the reviewer the diff, in the earlier review session or a fresh one. It does not start a new review of the whole model. Changes outside the strict scope follow the context's depth.
