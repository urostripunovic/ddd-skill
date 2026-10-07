# Changing a model

Use this when the context file has rows under `## Pending` or `## Amendments`, or the user asks to change a model that already exists. The notation and the way of asking are in [SKILL.md](SKILL.md); approval is in [lifecycle/approval.md](lifecycle/approval.md).

## Settling pending gaps and folding in amendments

When the context file has rows under `## Pending`, settle them first: each is a question implementation is waiting on. Ask it, write the answer into the section it affects, and remove the row once the model is approved again.

When it has rows under `## Amendments`, and the user asks to bring the model up to date or wants a larger change, fold them in: move what each row learned into the section it names, remove the row, and show the whole change as one diff. An amendment that touched only the rest needs no discussion. One that turns out to change the core (a new state, a command, an invariant, who may issue) is put to the user as a question. Then the user approves again, once, for all of them.

## When the request is small

For a change to an existing model, update only the affected sections, including the matrix column or row and the examples the change touches. Show the change as a diff, run `tools/check-model.sh`, and still wait for approval. A new rule, state, command or term always goes through the model first.

A change inside a strict scope of a model that was already reviewed needs a review of the changed rows only: give the reviewer the diff, in the earlier review session or a fresh one.
