# What each section of a context file holds

Read this from [SKILL.md](SKILL.md)'s step 3, while writing a section. The notation, the flow, the
bound on a table cell and the Decisions rule stay in SKILL.md, because each of them applies to every
section at once. `docs/domain/contexts/_template.md` shows the shape of each section; these are its
rules.

- **Domain primitives**: every value with rules gets a named type with stated bounds, and the reason for each bound; a bound nobody confirmed says `(assumed)` in the Why column. No bare strings or numbers in the model.
- **States**: one type per state, holding only the data that exists in that state. No status field with optional fields.
- **Commands**: a function from the specific state or states it is legal in, to a new state plus events, or a named failure. A command that is illegal in a state is simply not defined for that state's type, so "wrong state" is never listed as a failure of the command.
- **Matrix**: every state against every command. `yes`, or `no:` and the reason the business gave.
- **Events**: past tense, in the ubiquitous language, with the data consumers need.
- **Invariants**: each one names where it is enforced (the type, a constructor, a decision function, or "not in types" with how it is checked instead) and every command that could break it.
- **Failures**: each business failure gets a name and the data needed to explain it.
- **Use-case failures**: "not found", "not allowed" and "not in a state this command accepts" are raised by the workflow, not by a decision. Name them in their own table.
- **Examples**: the confirmed rows from the interview. Values, not descriptions. Every command and every failure has at least one, and every bound one on each side.
- **Races**: which command wins and what the other is told.
- **Facts from outside**: any data a command needs that the aggregate does not hold gets a named type, its source, what is checked before it is believed, what happens when that check fails or the source does not answer, and whether it may be slightly out of date. The caller's identity is such a fact: "Requester", from the sign-in token, believed once its signature, issuer, audience and expiry are checked.
- **Aggregates**: keep them small. Data belongs in the same aggregate only if a rule requires it to change together. Other aggregates are referenced by ID.
- **Rules across aggregates**: immediate or eventual. An immediate rule means the things involved are one aggregate, or a database constraint holds it. An eventual rule names the policy that restores it and what the user sees in the meantime.
- **Policies**: each reaction from the interview: the event, the command it causes, and what happens when that command fails.
