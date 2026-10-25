# What the timeline hides, and how to write it down

Read this from [SKILL.md](SKILL.md)'s step 1, for the commands the work in front of you needs.
**Edges** is the core and is always asked; [lifecycle/triggers.md](lifecycle/triggers.md) says when a
command raises the other four.

**Ask what the timeline hides, where a trigger applies.** A timeline shows one thing after another, done by people, to one thing. Five kinds of question find the rest. Ask each for a command this work needs when lifecycle/triggers.md says the command raises it; **Edges** is the core and is always asked:

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

**Challenge the wording at once.** Do not note a language problem for later. If a skill named `domain-modeling` is available, call the Skill tool with "domain-modeling" at the start of the interview: it challenges terms and writes `GLOSSARY.md` and ADRs as they settle, and the glossary rules under **Output** still hold. If it is not:

- One word used with two meanings: stop and ask which is meant. This often marks a context boundary.
- Two words for one thing: propose one. The other goes under `_Avoid_`.
- A term that conflicts with the glossary: quote the entry and ask which is right.
- A name the user would not say out loud to a colleague is the wrong name. Ask what they call it.

**Bounds.** How many, how long, how large, which characters. Every primitive needs bounds, and "no limit" is not an answer. Propose them all at once ("I will use these unless you object") and mark them `(assumed)`; a bound the user states is theirs and is not marked.

