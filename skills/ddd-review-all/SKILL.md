---
name: ddd-review-all
description: "Run the DDD review, the Secure by Design review and the task review on the same pinned diff, each in its own isolated sub-agent, and report them together. Use when implementation of domain or business-logic code is finished and needs review."
disable-model-invocation: true
---

# Review with all reviewers

Run `ddd-review`, `secure-by-design-review` and `task-review` on the same change, each in a sub-agent that has not seen this conversation, and combine their reports. You orchestrate. You do not review, and you do not edit the reviewers' findings.

The three answer different questions: does the code match the model, is it hard to misuse, and does it do what was asked. A change can pass any two and fail the third.

The isolation is the point. A reviewer that shares context with the author inherits the author's assumptions. It is therefore fine to run this skill in the session that wrote the code, because the reviewing is done elsewhere.

If you have no tool for starting sub-agents, say so and stop. Tell the user to run each review skill in its own fresh session instead. Do not run the reviews yourself in this context.

## 1. Pin the range and check it

1. Ask for a base ref if none was given. If the user has no preference, use the merge base with the default branch: `git merge-base HEAD origin/main` (or the repository's default branch).
2. Resolve both ends to full commit hashes with `git rev-parse`. The range is `<base>...<head>`.
3. Confirm that `git diff --stat <base>...<head>` is not empty. A bad ref or an empty diff should stop here, not inside three sub-agents.
4. If the working tree has uncommitted changes, tell the user they will not be reviewed, and ask whether to continue or commit first.

## 2. Find the task

The task reviewer needs the task, and a sub-agent cannot ask the user for it. Find it now, in the order the `task-review` skill gives: what the user gave you, issue references in the commit messages, a migration step in the context file, a specification matching the branch. Fetch an issue's text and save it to a file outside the repository.

If there is none, ask the user. If they say there is no written task, skip the task reviewer and say so under **Not checked**. Do not write a task yourself from the conversation or the diff.

## 3. Give each reviewer its own checkout

The DDD and security reviewers write and compile scratch files for their break-it attempts. In a shared checkout, one reviewer's deliberately broken file would fail another's build or tests.

Create a temporary worktree per reviewer at the head commit, outside the repository directory:

```
git worktree add --detach <tmp>/ddd-review <head>
git worktree add --detach <tmp>/sbd-review <head>
git worktree add --detach <tmp>/task-review <head>
```

A new worktree holds only tracked files: no `node_modules`, no generated code, no local environment files. Before starting the reviewers, make each worktree able to compile, lint and test:

- install dependencies with the repository's lockfile command (`npm ci`, `pnpm install --frozen-lockfile`); Go fetches modules from the shared cache on the first build
- run the repository's code generation step, if it has one

If that fails, do not start the reviewers on a tree that cannot build. Tell the user what failed and ask whether to continue with the checks that need no build.

## 4. Start the sub-agents in parallel

Find the skill files. They are sibling directories of this skill: `../ddd-review/SKILL.md`, `../secure-by-design-review/SKILL.md` and `../task-review/SKILL.md` relative to this file. Resolve them to absolute paths.

Give each sub-agent a prompt containing only:

- the absolute path of its skill file, with the instruction to read it and follow it exactly
- the absolute path of its worktree, as the only place it may work
- the base and head hashes, stated as already pinned so it does not ask
- for the task reviewer: the path of the task file, stated as the task so it does not search for another; also pass that original file to the DDD reviewer as the scope reference, so explicitly deferred adapters, storage or property tests are not mistaken for missing work in this ticket
- for the DDD reviewer only: the absolute path of a file outside the repository and outside the worktree, `<tmp>/ddd-tracing.md`, as the place to write its complete tracing tables
- the absolute path of a file outside the repository and outside the worktree, `<tmp>/<reviewer>-report.md`, with the instruction to write its full report there and to return only its verdict, its number of blockers and that path
- the part to review, when the user named one
- for a re-review (see **7. What comes next**): the path of that reviewer's earlier report, stated as a re-review of the fix commits

Do not pass a summary of the change, your opinion of the code, or anything else from this conversation. The task goes in as its author wrote it, never as your summary of it. If a sub-agent comes back with a question instead of a report, relay the question to the user and pass the answer on.

## 5. Combine the reports

The reports are in the files, not in this conversation: three full reports returned as messages would fill it before you had combined anything. Read from each file only what the list below needs.

Present, in this order:

1. The base and head hashes.
2. **Overall verdict**: the worst of the verdicts. Then each reviewer's own verdict, and one line per reviewer with its number of blockers and its most serious finding.
3. **Findings**, most severe first, each tagged `[DDD]`, `[SbD]` or `[Task]`, in the reviewer's own words. When two reviewers report the same `file:line` for the same reason, show it once and tag it with both.
4. **What was traced**: the DDD reviewer's counts and its rows that are not ok; the task reviewer's requirements that are not **done**, and how many were.
5. **What was attempted**: from the break-it and abuse-attempt tables, how many attempts were made and stopped, and every row that was **not prevented** or stopped later than the model expected.
6. **Not checked**: the union of what each reviewer said it did not check, including skipped conditional sections and a skipped task review.
7. Where the complete reports are: the three report files and the DDD reviewer's tracing file.

Rows with nothing wrong in them are counted, not shown. The user reads this to find what to fix; the complete tables are in the files for when a count needs checking.

Do not drop, soften, re-rank across severities or reword a finding. If you disagree with one, say so in a separate note after the report, clearly marked as your own.

## 6. Clean up

Remove the worktrees with `git worktree remove --force`, delete the task file if you created one, keep the report files, run `git worktree list` and `git status --porcelain` in the main checkout, and confirm in your final message that nothing was left behind.

## 7. What comes next

End the combined report with the next step, so a review round always ends somewhere:

- **No blockers**: the change can be merged. Should-fix findings and notes are fixed without another review round, or turned into tickets. Then the next ticket or command.
- **Blockers**: fix them and commit. Then run this skill again as a re-review: the base is the head just reviewed, start only the reviewers that reported blockers, and give each its earlier report. Each checks that its blockers are fixed and that the fix commits add none; it does not start again from the top. A full round is only for a change that grew beyond the fixes.
- **A finding that is a gap in the model**, not a mistake in the code: take it to `ddd-modelling`, not into a code fix.

Give the paths of the report files, because a re-review needs them.
