---
name: task-review
description: "Review a change against the task that asked for it: which requirements are done, partial, missing or wrong, and what the change does that nobody asked for. Use after implementation, in a fresh session, alongside ddd-review and secure-by-design-review."
disable-model-invocation: true
---

# Task review

Answer one question: does this change do what was asked, no less and no more? Report findings. Do not change the code unless the user asks.

The other two reviews cannot answer this. Code can match the domain model exactly, pass every security check, and still solve a different problem from the one in the ticket.

Run this in a session that did not write the code. If you wrote the code under review in this session, say so at the top of the report.

## Scope

This skill compares the change with the task. It does not check:

- whether the code matches the domain model or the cards: `ddd-review`
- security: `secure-by-design-review`
- style, naming or anything a formatter or linter handles

Do not report findings in those areas. If you notice a serious problem in passing, mention it in one line under notes.

## Pin what is reviewed

If you are given an earlier report of yours and the commits that fix it, this is a re-review: the range is those fix commits. Check that each blocker in the earlier report is fixed, and that the fix commits add no new blocker. Do not review the rest again. Report each earlier blocker as fixed or not fixed.

1. Ask for a base ref if none was given. If the user has no preference, use the merge base with the default branch: `git merge-base HEAD origin/main` (or the repository's default branch).
2. Review exactly `git diff <base>...HEAD`. Uncommitted changes are not part of the review unless the user says so; if there are any, say that they were excluded.
3. Put the base and head commit hashes at the top of the report.

## Find the task

Look in this order and use the first that exists:

1. A file, link or text the user gave you as the task.
2. Issue references in the commit messages of `git log <base>..HEAD`, such as `#123` or `Closes #45`. Fetch the issue with the repository's own tool (`gh issue view`, `glab issue view`). If you cannot fetch it, ask the user to paste it.
3. A step in the `## Migration` section of the context file in `docs/domain/contexts/`, when the commits say they implement one.
4. A specification under `docs/` or `specs/` whose name matches the branch.

If none exists, ask the user for the task. If they say there is none, stop and report "no task available".

Never reconstruct the task from the diff or from the commit messages' own descriptions. A task inferred from the code can only agree with the code, so the review would pass everything.

## Read the task into requirements

Before reading the diff, write a numbered list of what the task asks for, each with the line of the task it comes from, quoted.

- Include acceptance criteria and anything the task says is out of scope.
- A sentence that asks for two things is two requirements.
- Where the task is vague or contradicts itself, do not pick a reading. List it as a question, and review the rest.

Doing this first matters. Read the diff first and the code's own interpretation becomes yours.

## Check each requirement

For each one, find the code and the test that carry it, and give one status:

- **done**: implemented, with a test that would fail without it
- **partial**: some cases are handled, or it is implemented with no test that proves it
- **missing**: nothing in the diff implements it
- **wrong**: implemented, and it behaves differently from what the task says

Give `file:line` evidence for every status except missing. Run the tests the change adds or touches; a requirement whose test fails is not done.

Pay attention to the cases a task implies without spelling out: the failure path of each new operation, the empty and the maximum case, and what happens to existing data.

## Look for what was not asked for

Go through the diff hunk by hunk. Each hunk either carries a requirement, is needed to support one, or is unrequested.

- Unrequested behaviour is a finding even when it is good. It was not reviewed as part of the task, and it hides in the diff of something else.
- An unrequested edit to the approved model body is a finding, unless the model was approved again in the same range for a gap the task ran into: then say so as a note. Rows in the context file's notes tail (`## Amendments`, `## Pending`, and `(done <date>)` on a `## Migration` step) are permitted bookkeeping; still check whether the behaviour they describe is within the task. An amendment inside a strict scope (as `tools/check-model.sh` prints it), or at strict depth, is a finding.
- Refactoring mixed into a behaviour change is a finding: name the files, and suggest a separate commit.
- Removed or weakened tests are a finding, whatever the reason given.

## When the task and the model disagree

If the task asks for behaviour the approved model does not have, or forbids, the problem is in the task or the model, not in the code. Report it as a blocker with both quoted, and do not judge the code on that requirement.

## Report

Start with the base and head hashes and where the task came from, then the verdict: **approve**, **approve with changes**, or **reject**.

Then the requirements table:

| # | Requirement (quoted) | Status | Evidence |
|---|---|---|---|

Then the findings, most severe first. For each one:

- location as `file:line`
- the requirement it concerns, by number, or "unrequested"
- severity: **blocker** (a requirement missing or wrong, the task and the model disagree, a test removed), **should fix** (partial, unrequested behaviour, mixed refactoring), or **note**
- what is needed to close it

Then the questions about the task that only its author can answer.

End with what you did not check and why, and state that model conformance and security were not reviewed here. A reader must be able to tell a clean result from an unchecked one.

Do not pad the report with praise.
