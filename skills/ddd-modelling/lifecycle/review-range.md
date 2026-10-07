# The range a code review covers

`ddd-review`, `secure-by-design-review` and `task-review` pin what they review the same way. A review of "the current code" cannot be repeated or compared, so fix the range first.

If you are given an earlier report of yours and the commits that fix it, this is a re-review: the range is those fix commits. Check that each blocker in the earlier report is fixed, and that the fix commits add no new blocker. Do not review the rest again. Report each earlier blocker as fixed or not fixed.

1. Ask for a base ref if none was given. If the user has no preference, use the merge base with the default branch: `git merge-base HEAD origin/main` (or the repository's default branch).
2. Review exactly `git diff <base>...HEAD`. Uncommitted changes are not part of the review unless the user says so; if there are any, say that they were excluded.
3. Put the base and head commit hashes at the top of the report.
