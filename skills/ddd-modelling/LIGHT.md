# Light modelling

Read this from [SKILL.md](SKILL.md) when the context's depth is light. Light is for an area where a wrong rule is cheap to find and fix; [lifecycle/depth.md](lifecycle/depth.md) says when that holds and when the context moves up.

A light context is two tables, from `docs/domain/contexts/_light-template.md`: **Requests** (each request the rules answer, and who or what may make it) and **Examples** (one numbered row per rule: state, request, facts, the test that pins it). There are no state types, matrix, invariants table or approval. The rows are the model, and the tests are their proof.

## Interview first, and short

The interview still comes before the code. It is one round, about what the work in front of you needs:

1. The timeline of this area in a few lines: what happens first, and then?
2. Who or what makes each request. This is the one part of the core light keeps, and it is never `(assumed)`: `tools/check-model.sh` rejects an unconfirmed "Issued by".
3. For each rule the first change needs: one row with real values, and a proposed answer the user corrects.
4. Whether anything here touches money, credentials, authorisation, personal data or something hard to undo, and whether another context reacts to it. A yes to either means this is not light: say so and use standard, with strict commands where needed.

Write the context file with `Status: light` and `Depth: light` as soon as you know the context, the terms to `GLOSSARY.md` as they settle, and the rows as they are confirmed. Then run `tools/check-model.sh`. There is no approval to ask for: carry on with what the user asked for, and hand over to `ddd-implementation` if that includes the code.

## Later questions

Further rules are not collected up front. When a change raises a question the rows do not answer, or hits a trigger in [lifecycle/triggers.md](lifecycle/triggers.md), it is asked then, with a proposal, and the answer becomes a new row with the next unused number, written with its test. `ddd-implementation` does this as it goes; [lifecycle/gaps.md](lifecycle/gaps.md) has the rule.

## Moving up

When one of depth.md's reasons to move up holds, model the context at standard depth from what is there, with [ADOPTING.md](ADOPTING.md#moving-a-light-context-up): the rows keep their numbers, so the tests that name them stay true.
