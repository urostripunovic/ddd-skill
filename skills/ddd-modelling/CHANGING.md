# Changing a model

Use this when the context file has rows under `## Pending` or `## Amendments`, or the user asks to change a model that already exists. The notation is in [NOTATION.md](NOTATION.md) and the way of asking in [INTERVIEW.md](INTERVIEW.md); approval is in [lifecycle/approval.md](lifecycle/approval.md).

## Settling pending gaps and folding in amendments

When the context file has rows under `## Pending`, settle them first: each is a question implementation is waiting on. Ask it, write the answer into the section it affects, and remove the row once the model is approved again.

When it has rows under `## Amendments`, and the user asks to bring the model up to date or wants a larger change, fold them in: move what each row learned into the section it names, remove the row, and show the whole change as one diff. An amendment that touched only the rest needs no discussion. One that turns out to change the core (a new state, a command, an invariant, who may issue) is put to the user as a question. Then the user approves again, once, for all of them.

## When the request is small

A change to the rest of an approved model (a bound, a payload, an edge case, an example at a limit), at standard effective depth: do not edit the model. Add an `## Amendments` row: the date, the section, what the model said, and "Changed by the user:" with the new value. Tell the user in one line; the approval stands, and the row is folded in with the others later.

Any other change, to the core, inside a strict scope, at strict depth, or to a draft: update only the affected sections, including the matrix column or row and the examples the change touches. Show the change as a diff, run `tools/check-model.sh`, set an approved model back to draft, and wait for approval. A new rule, state, command or term always goes through the model first. When unsure whether a change touches the core, treat it as core.

A change inside a strict scope of a model that was already reviewed needs a review of the changed rows only: remove `, reviewed <date>` from the Status line, give the reviewer the diff, in the earlier review session or a fresh one, and write it back once no blocker is left.
