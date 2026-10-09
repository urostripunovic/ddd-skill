# 3. Model each context

Read this from [SKILL.md](SKILL.md) before the first write to a context file.

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
- **Decisions**: the model says what was decided; this section says why. Record a decision only when all three hold: it is hard to reverse, a later reader would be surprised by it, and a real alternative was rejected. Only decisions about the domain go here: a rule, a boundary, a split between contexts. They are part of the approved model, so changing one means approving again. A technical decision (storage, a framework, event sourcing, deployment) is an ADR in `docs/adr/`, as Matt Pocock's `domain-modeling` writes them, and not a Decisions row.
