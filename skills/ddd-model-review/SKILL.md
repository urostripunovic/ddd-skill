---
name: ddd-model-review
description: "Review a domain model before it is approved, through three lenses: an implementer who may not ask questions, someone abusing the rules from inside them, and a sceptic looking for answers nobody gave. Use after ddd-modelling and before approval, in a fresh session."
disable-model-invocation: true
---

# DDD model review

Answer one question: could this model be implemented without anyone making a business decision along the way, and would the result be what the business wants? Report findings. Do not rewrite the model unless the user asks.

Run this in a session that did not write the model. An author reviewing its own model reads what it meant, not what it wrote. If you wrote the model in this session, say so at the top of the report.

## What is reviewed

Only the model: `GLOSSARY.md` (or the glossaries `GLOSSARY-MAP.md` links to), `docs/domain/context-map.md`, and the context files the user names, or every file under `docs/domain/contexts/` whose status is not approved, except `_template.md`. Do not read code. A model that needs the code to be understood is a finding.

If you are given a diff of an earlier-reviewed model (a change inside its strict scope, or the fixes for your blockers), review only the changed rows and what they touch, and say so at the top.

## One part at a time

A review of a whole context at once gives a long report that nobody reads to the end, and every round has the whole model to find something new in. Prefer a part.

- If the user names a part, review only that: an aggregate, a command, or a step of the flow (`/ddd-model-review PlaceOrder`, `/ddd-model-review step 3`). Read the whole model for context, and report only on the part: its command, the states it starts from and ends in, the invariants, examples, races and failures that name it.
- If the user names nothing and the context has more than about six commands, propose going through it in the order of `## The flow`, one step per round, and start with step 1. The user says "next" to go on.
- A small context is reviewed whole.

Order every report along the flow: findings for step 1 before findings for step 2. A reader follows a story more easily than a list sorted by lens.

## How much to review

Read the context file's `Depth:` line and what the system is for (the glossary's opening lines, the context map). A homelab tool and a payment system do not get the same review.

A missing `Depth:` line means strict. Review at the effective depth defined in [depth.md](../ddd-modelling/lifecycle/depth.md): each strict scope gets strict review even under `Depth: standard`, the rest the context's depth. Name the reviewed scope in the report.

- **`standard`**: one pass, in this session, no sub-agents. Apply the three lenses to the **core** only (depth.md). Skip section 3. Entries marked `(assumed)` in the rest are not findings: nobody claimed they were confirmed. An unconfirmed core fails `tools/check-model.sh` and is a blocker, because an implementer would have to invent who may issue or what must hold. Report at most five questions, the ones where a wrong answer costs most.
- **`strict`**, or no `Depth:` line: everything below, and [STRICT.md](STRICT.md), in full.

## What stops approval, and what does not

A review that can always find one more thing never ends, and each round's fixes add text for the next round to question. These rules make it end.

- **A blocker is one of three things**: an example that contradicts a rule; a place in the core where an implementer would have to invent a state, a command, an invariant, who may issue, or what makes a caller or fact trusted; an abuse sequence that causes real loss or exposure for this system and that nothing limits. Nothing else is a blocker, at either depth.
- **Everything else does not stop approval.** Write it as a proposed assumption: the value or behaviour you would pick, as a diff that adds it marked `(assumed)`. The user accepts them all in a word. Do not turn them into questions. At strict depth, an accepted assumption counts as confirmed, and the modelling session writes it without the marker.
- **Settled is settled.** A row under Decisions, a bound the model says was confirmed, and anything an earlier review asked and the user answered, is not asked again. If you think a decision is wrong, say so once, as a note.
- **Abuse is scaled to the system.** Do not report abuse that needs an administrator of another system, a second account in the identity provider, or a restart of the service, unless the model says that is in scope.
- **Verdict: ready for approval when there are no blockers**, however many assumptions and notes there are.
- **A second round is for blockers only.** If this round found none, say that no further round is needed. If it found some, the next round checks that those are fixed and reads only what changed; it does not start again from the top. Say this at the end of the report, so the user knows when to stop.

## 1. Mechanical check

Run `tools/check-model.sh <file>` for each context file and put its output in the report as it is. If structural errors prevent a useful review, report the needed corrections and pause. Warnings are information, not automatic blockers.

What the script does and does not check is in [checker.md](../ddd-modelling/lifecycle/checker.md); check the rest yourself at the effective depth. If it is missing, say so and check its structural points by hand too.

## 2. Three lenses

Each lens is a separate reading of the model with one concern. Finish one and write its findings before starting the next, so the second does not excuse what the first found.

At strict depth, run the lenses as [STRICT.md](STRICT.md) says.

### Implementer

Read the model as the person who has to write its types and functions tomorrow and cannot ask anyone anything.

Take each example in the Examples table and work it by hand: start from its Given, apply the command in its When using only what the model states, and write down the result. Then compare with its Then.

- Every point where you had to choose is a finding: the model left a decision to the implementer. Typical ones: what a command does to each field of the state; input a command needs that is listed nowhere; which failure is returned when two apply; what an event carries; where an ID or a time comes from; rounding, units and time zones; what happens to the rest of a list when one element changes.
- An example whose Then does not follow from the rules as written is a finding. Either the rule or the example is wrong.
- An example that cannot become a test because a value is missing ("a large order") is a finding.

Then go through what no example touched: every command, failure, invariant, race and policy without one. Each is either a missing example or something nobody checked.

This lens is done when every example has been worked and every command has been through at least one.

### Abuser

Read the model as someone who follows every rule in it and still wants to gain something or cause damage. Assume a valid account and no technical attack.

For each command, and for sequences of them, try:

- doing it twice, or a thousand times
- alternating two commands in a loop: place and cancel, reserve and release
- starting something and never finishing it, to hold a resource
- the largest and smallest values every primitive allows, and many of them at once
- acting in the window of a rule that is only eventually true, or with a fact that is allowed to be stale
- two sessions at once, where the Races table says nothing about the pair
- acting on someone else's data, where "Issued by" does not tie the caller to an owner

For each attempt, name what in the model stops or limits it: an invariant, a bound, a failure, an "Issued by" rule. If nothing does, that is a finding. Write it as the exact sequence of commands and what the abuser ends up with.

Also check what leaves the context: any event, failure or example that carries a primitive marked sensitive.

### Sceptic

Read the model looking for entries that were written without anyone being asked. A model can pass every check and still be the author's guess.

- A `no:` reason in the matrix that is technical ("not implemented", "wrong state") and not a reason a person in the business would give.
- "None." under Races, Policies or Rules across aggregates, when two commands start from the same state, an event has a consumer, or two aggregates appear in one rule.
- Bounds that look like defaults (255, 1000, 100) with nothing to say where they came from.
- Examples with no value on either side of a limit, or that only show the success case.
- A term whose definition would not let a newcomer tell it from its neighbour, or that nobody in the business would say out loud.
- A Decisions row with no rejected alternative.
- No open questions at all in a model of any size.

Write each as a question for the domain expert, quoting the entry. Do not answer it yourself.

## 3. What the lenses do not cover

At strict depth only, in [STRICT.md](STRICT.md).

## Report

Lead with the verdict: **ready for approval** (no blockers), **ready after changes** (blockers you can fix with the diffs below), or **needs another interview round** (blockers only the domain expert can answer). Then one line: whether another review round is needed, and why.

Then, in this order:

1. The output of `tools/check-model.sh`.
2. Findings per lens, most severe first. For each: the file and section, the entry quoted, what is wrong, and severity:
   - **blocker**: only the three kinds under "What stops approval"
   - **assumption**: everything else that needs a value or a behaviour, with the one you propose
   - **note**
3. The proposed changes as one diff: the fixes that need no domain fact, and every proposed assumption marked `(assumed)`. A question only for a blocker that needs the domain expert.
4. The questions for the domain expert, numbered, each with a proposed answer, most costly first.
5. What you did not check and why.

Do not pad the report with praise.
