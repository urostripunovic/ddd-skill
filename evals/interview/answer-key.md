# Answer key for the interview eval

The expert in `expert-brief.md` holds ten rules it gives only when asked about their subject. Score the model the interview produced (`CONTEXT.md` and `docs/domain/` in the run's repository) against this table.

| # | Hidden rule | Found when the model has | The kind of question that finds it |
|---|---|---|---|
| 1 | At most 5 tools on loan at once | an invariant or a failure with the number 5 | asking for limits |
| 2 | Loans last 7 days, power tools 3 | both periods, as a rule or in examples | asking for limits |
| 3 | A loan 14 days overdue is lost; replacement is charged and the late fee stops | a lost state or command issued by time, with the 14 days | "what happens if nothing happens?" |
| 4 | One renewal, same length, only if nobody is queuing | a renew command with both conditions | "it happens twice" |
| 5 | Two reservations at once: one wins, the other is first in the queue; never promised twice | a row under Races, or an immediate rule across aggregates | races and consistency |
| 6 | Only a volunteer waives a fee; anyone may return for someone else; nobody borrows for someone else | "Issued by" for those three commands | "the wrong person does it" |
| 7 | A set with parts missing is "returned incomplete": loan open, fee paused, 7 days, then charged | its own state, with the way out of it | "it happens partially" |
| 8 | Membership is per household, up to 4 people; limits and fees are per household | two glossary terms for household and person, and the limit attached to the household | challenging the wording |
| 9 | A returned tool is offered to the first in the queue for 48 hours, then to the next | a policy, and a time-issued command with the 48 hours | reactions and time |
| 10 | Owing 200 kr or more blocks borrowing and reserving; exactly 200 blocks, 199 does not | the rule, with examples on both sides of 200 | examples at a limit |

## Scoring

For each rule, one of:

- **found**: the model states it, with its numbers
- **partial**: the model has the subject and is missing a number or a condition (rule 4 without "only if nobody is queuing"), or has it only as an open question
- **missed**: not in the model

Then three more numbers:

- **Invented facts**: statements in the model about how the library works that are neither in the brief nor listed under open questions. The expert was told to answer "I would have to ask the board" for anything the brief does not cover, so each of these is something the interviewer made up or took from its own proposal. Lower is better, and zero is the target.
- **Rounds**: how many times the interviewer turned to the expert before finishing.
- **Model check**: whether `tools/check-model.sh` passes on the result.

A run that finds ten rules and invents five facts is not a better interview than one that finds eight and invents none.
