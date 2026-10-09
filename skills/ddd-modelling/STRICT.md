# Strict modelling

Read this from [SKILL.md](SKILL.md) before the interview when the context's depth is strict or it has no `Depth:` line. With a `Strict commands:` line in a standard context, apply this file inside each strict scope ([lifecycle/depth.md](lifecycle/depth.md)) and SKILL.md outside it.

SKILL.md describes standard depth, where you ask about the core and propose the rest marked `(assumed)`. At strict depth nothing is proposed and left: everything is asked, confirmed and reviewed. The steps below say what changes; everything else in SKILL.md still holds.

## 1. Interview

- **Ask about the rest too.** A bound, a payload, a race, an edge case and an example at a limit are each a question with a proposed answer. Nothing is written `(assumed)`: a proposal the user has not confirmed goes under open questions.
- **No limit on rounds.** Go on until the list below holds. If `grilling` runs the interview, its own rule applies: the session ends when every branch is visited. Still end each round with the checkpoint.
- **The matrix.** Go through every pair of state and command with the user. Where the command is not allowed in that state, ask why not, with a proposal.
- **Bounds.** Ask for each one: how many, how long, how large, which characters. Do not propose them in one batch.
- **Examples.** For every rule: one ordinary case, one on each side of every limit, and one for each way it can fail, each confirmed by the user.

**The interview is done when** all of these hold:

- every event on the timeline has its trigger, issuer, preconditions, failures and outside data, each either answered or listed under open questions
- every caller and every outside fact says what makes it trusted and what happens when it is not
- every cell of the matrix is `yes` or has the business's reason
- every command, every failure and every limit has an example the user confirmed
- reactions, time, races and consistency have each been asked about, and each answer is written down, including "none"
- every value with rules has bounds, and every term in use is in the glossary

Then ask whether anything is missing from the timeline, on its own, and do not move on before they answer.

## 2. Bounded contexts

Ask for the Kind of every context and the Pattern of every relationship, also when there is one context or one owner on both sides.

## 4. Model it twice

Do not settle it with one question. Sketch both candidates, with only the state types and command signatures. Run every example and every race from the context file through each. Show the user a short comparison: which examples each candidate needs a policy and a delay for, and which races each makes impossible. The user chooses. Record the choice under Decisions, with the example that decided it.

## 5. Security pass on the model

Ask every question on the list, each with a proposed answer, and write the answers the user confirms.

## 6. Check, write, stop

- There is no list of assumptions to show: `tools/check-model.sh` fails an approved strict model that has one, and one whose strict scope has one.
- Before asking for approval, ask for the review [lifecycle/approval.md](lifecycle/approval.md) requires: `/ddd-model-review <file>`, in a fresh session.
- When the user brings back the review's findings, a proposed assumption the user accepts is confirmed: write it without the `(assumed)` marker.
