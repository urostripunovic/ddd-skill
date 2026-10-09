# 1. Interview

Read this from [SKILL.md](SKILL.md) when step 1 starts, or when an interview is resumed.

You do not know this domain. The user or their domain expert does. The model is found in this step; the later steps only write it down, so do not hurry through it.

- **Ask about the core. Propose the rest.** For a bound, a payload, a race or an edge case, write your best guess into the model marked `(assumed)` and do not ask. Ask about something in the rest only when a wrong guess would lose money or data, expose something, or be hard to undo. Never mark the core `(assumed)`, and never fill it with a placeholder such as "TBD": `tools/check-model.sh` rejects an assumed or placeholder "Issued by" cell, invariant or "Believed when" cell. A core question still unanswered goes under open questions, and the model does not pass the check until the user answers it.
- **Stop after each round.** End every round with a checkpoint of a few lines: the flow as it stands now, numbered, and under it what is still unclear. The user reads the flow and says where it is wrong. The next round is about the unclear points and nothing else; do not open new subjects while one is unclear.
- **About three rounds.** If the core is not settled by then, say what is still unclear and ask whether to go on or to continue with it under open questions. Do not keep asking to reach completeness.

**How to ask.** If a skill named `grilling` is available, call the Skill tool with "grilling" and use the rest of this file as what to grill about; it supplies the format of a round. This file decides when to stop: about three rounds, with the rest proposed and marked `(assumed)`, takes precedence over grilling's rule that the session ends when every branch is visited. If it is not, ask this way:

- Work in rounds. A round holds every question you can ask now without guessing an answer you have not heard yet. Number the questions, and wait for the answers before the next round.
- Give a proposed answer with every question. Correcting a proposal is quicker for the user than composing an answer.
- Facts are yours to find; decisions are the user's. Read what the repository can already answer (the glossary, `docs/domain/`, `docs/adr/`, code, schemas, API specifications, a ticket the user points to) before asking. What the code does today is a fact. Whether the business intends it is a decision. A decision the user has already stated, in the request or earlier, is answered: write it without `(assumed)` and do not ask it again.

Whichever way you ask: a proposal is not a fact. If the user does not confirm it, it goes under open questions as an assumption. Never invent a domain fact to fill a gap. Use the user's words, not DDD jargon.

**Follow the timeline first.** People describe their business as things that happen, so open with the events: "what happens first, and then?" Collect the whole sequence before going deep on any part of it.

**Then one event at a time.** For each: what triggers it, who may trigger it and on whose data, what must be true before, what can go wrong, which data it needs that lives somewhere else, and who needs to know that it happened.

**Ask what the timeline hides.** A timeline shows one thing after another, done by people, to one thing. Five kinds of question find the rest:

- **Reactions.** "Whenever this has happened, what has to happen next, and who or what does it?" Each answer is a policy.
- **Time.** For every state that is not final: "what happens if nothing happens, and after how long?" Deadlines, expiry and reminders are commands that a scheduler issues. Write the answer under the States block, one line per state that is not final, including "no expiry".
- **Races.** For every pair of commands that can reach the same thing at the same moment (two browser tabs, a customer and a member of staff, a retry, a person and the scheduler): "which wins, and what is the other told?"
- **Edges.** For every way in and out: "who or what is on the other side, and how do we know?" A model that only says "the customer" has skipped how a request becomes a customer. For each caller: what proves who they are, and what is refused. For each thing received from another system (a sign-in token, a price, a webhook): what must be checked before it is believed, and what happens when it is wrong, late or missing. These are part of the core, because every "who may issue" rule rests on them. The answers go in the context map's relationships and in the context file's **Facts from outside**, and each refusal is a named use-case failure.
- **Consistency.** For every rule that involves more than one thing: "if this were wrong for a few seconds, what would it cost, and who would notice?" The answer decides what belongs in one aggregate. Then: "can something outside the system make it wrong anyway?" A customer can pay twice, a carrier can lose a parcel; no boundary refuses a fact that has already happened. If so, the rule is not an invariant: name the state it leads to (an overpaid invoice) and the policy that resolves it.

**Turn every rule into examples.** When the user states a rule, fill it in with real values and ask what happens: one ordinary case, one on each side of every limit, and one for each way it can fail.

```
Rule: orders over 10 000 kr need a manager's approval.
Q3. What happens for each of these?
    a. 9 999 kr              Proposed: placed directly.
    b. exactly 10 000 kr     Proposed: placed directly; "over" means more than.
    c. 8 000 kr plus VAT, which makes 10 000   Proposed: the limit is on the amount including VAT.
```

A rule stated in general terms sounds complete until a specific case hits it. Write the confirmed rows to the context file's Examples table as you go: they are the test cases later. Row numbers are permanent, because tests and tickets refer to them: give a new row the next unused number, never renumber, and leave a gap where a row was removed. Ask about the rows of a rule in the core; for the other rows at a limit, write your proposal marked `(assumed)`. Other edges worth an example: it happens twice, it happens late or in the wrong order, it happens partially, the amount is zero or huge, the wrong person does it.

**Fill in the matrix yourself.** Once the states and commands are known, write `yes` where the signature allows the command, and for each other cell the likely reason, marked `(assumed)`. Ask only about a cell where the honest answer might be "yes, until…", or where a wrong guess would cost money or data: "Can a placed order still receive an item? Proposed: no, because picking has started." An answer like "yes, until it is packed" has just found a missing state. The other reasons go into the list of assumptions.

**Challenge the wording at once.** Do not note a language problem for later. If a skill named `domain-modeling` is available, call the Skill tool with "domain-modeling" at the start of the interview: it challenges terms and writes `GLOSSARY.md` and ADRs as they settle, and the glossary rules in [GLOSSARY-FORMAT.md](GLOSSARY-FORMAT.md) still hold. If it is not:

- One word used with two meanings: stop and ask which is meant. This often marks a context boundary.
- Two words for one thing: propose one. The other goes under `_Avoid_`.
- A term that conflicts with the glossary: quote the entry and ask which is right.
- A name the user would not say out loud to a colleague is the wrong name. Ask what they call it.

**Bounds.** How many, how long, how large, which characters. Every primitive needs bounds, and "no limit" is not an answer. Propose them all at once ("I will use these unless you object") and mark them `(assumed)`; a bound the user states is theirs and is not marked.

**The interview is done when** the timeline is whole, every state and command is named with who may issue it, every caller and outside fact says what makes it trusted, and every invariant is stated with one example. Ask whether anything is missing from the timeline at the end of the last checkpoint; the answer comes with the user's corrections. If the person who would know is not available, leave the item under open questions and do not keep asking.
