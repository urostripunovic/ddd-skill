# tools/check-range.sh on the review fixtures, 2026-10-19

Not a reviewer run: the script added in this change, run once on each fixture built by `make-fixture-repo.sh`. It decides nothing a reviewer should judge; this records what it hands them.

| Fixture | Exit | Problems | To judge |
|---|---|---|---|
| seeded | 1 | `model changed`: the Quantity bound edited under an unchanged approval (D1) | 8 `SubmittedOrder` lines (D2); 3 entries on 2 lines for a database `row`, which are not D2; 6 suppressions, including the disabled exhaustiveness rule (D16); rows 1 to 10 untested (D12) |
| clean | 0 | none | none |
| clean-ts | 0 | none | 8 commented casts in the parsers and repository, 2 `@ts-expect-error` tests; all correct, as the C2 control describes |

What it showed:

- **Avoided words are leads, not verdicts.** The first version failed on them, and the seeded fixture showed why that is wrong: `row` and `line` are avoided for Item, and are also an ordinary database row and the `eslint-disable-next-line` comment. Comments are now skipped, and a match is listed to judge.
- **The four seeds it reports were each checked by hand in two or three reviewer skills.** The model-changed check was written out in `ddd-review`, `secure-by-design-review` and `task-review`, and in run 1 both reviewers reported it.
- **What it cannot do** is judge: whether a test uses a row's values, whether a suppression is justified, whether `SubmittedOrder` is a rename the migration plan allows.

## Caveats

- One run of a deterministic script on fixtures written by the same model family. It says what the script reports, not that reviewers now spend fewer tokens; that needs a reviewer run before and after.
