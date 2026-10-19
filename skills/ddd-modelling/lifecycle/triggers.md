# When to ask

At light and standard depth, questions are asked when the work in front of you raises them, not all up front, and again whenever new ones surface mid-work. At strict depth, and inside a strict scope, every question is asked ([depth.md](depth.md)); this file does not apply there.

**Always asked, for every request or command the work adds or changes:** who or what may make it, and on whose data; for each caller and each fact from outside, what makes it trusted. These are the core and are never guessed.

**Asked when the work hits a trigger:**

| The work | Ask |
|---|---|
| ends in an outcome others rely on (placed, paid, cleared, won, closed) | Can something outside make the opposite happen afterwards: a second payment, a lost parcel, a bullet already in flight? If so, what then, and is it a state to handle rather than a rule? |
| lets two requests reach the same thing at once (two tabs, a retry, a person and the scheduler, two outcomes in one tick) | Which wins, and what is the other told? The answer must not depend on which arrived first by accident: test both orders. |
| makes one decision with several consequences | Which of them belong together, what must never be seen half done, and is the same request arriving twice harmless? |
| leaves something in a state that is not final | What happens if nothing happens, and after how long? |
| produces a fact something else might react to | Who reacts, and what happens when their reaction fails? Another context reacting is a reason to move a light context up. |
| states a rule with a limit | What happens on each side of it, with real values? |

**How to ask.** One round, a few questions, each with the case that raises it, a proposed answer, and the alternatives. Find the case first, in the code, the model or a quick test, so the question is about something real. A question nothing in the work raises is not asked. If the user is not there, a question about the rest is settled with the proposal, marked `(assumed)`, and said in one line; a question about the core waits.

**Where answers go.** At light depth, a new Examples row with its test. At standard depth, the section of the model it affects, as `ddd-modelling` writes it; found during implementation, as [gaps.md](gaps.md) says.
