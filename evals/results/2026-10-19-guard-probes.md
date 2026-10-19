# Guard probes, 2026-10-19

`evals/guard-probes/run.sh`, two runs per probe, as real `claude -p` sessions, on the branch that adds light depth, asking on triggers, approval only when the core changes, and `tools/check-range.sh`. Scored from the repository state afterwards, not from the reply.

## Run 1: the four commits as planned

12 of 14 passed. The two failures:

- **light-1, a scoring bug in the probe.** The session did what light asks: it added the `PlayerDowned` rule as new rows, marked the rows it guessed `(assumed)`, and wrote a test per row. Its table test built case names with `fmt.Sprintf("example %d", ...)`, which the probe's grep did not match. The grep now accepts `%d`. `tools/ddd-status.sh` has the same blind spot, as `ddd-next` already says: a row "without" a test may have one under another name.
- **pending-1, a regression in this branch.** The session stopped without code and without inventing the rule, which is safe, but wrote no `## Pending` row. It quoted the line under `## Domain code`, which this branch had extended with "The one exception: `ddd-implementation` adds the rows of a light context". Naming one exception read as forbidding implementation's notes-tail rows. The line now names both: the notes tail and light rows.

## Run 2: after rewording the line

13 of 14 passed; pending passed 2 of 2.

- **light-2** wrote a correct row for "any request" in a finished run, which the checker rejected, and did not run the checker after adding rows. The checker now accepts "any request" or "every request" for a rule that answers all requests alike, and the light case of `ddd-implementation` runs the check again after adding rows.

## Run 3: light only, after those fixes

2 of 2 passed.

| Probe | Run 1 | Run 2 | Run 3 |
|---|---|---|---|
| approve | 2/2 | 2/2 | |
| coreedit | 2/2 | 2/2 | |
| goahead | 2/2 | 2/2 | |
| light | 1/2 (probe bug) | 1/2 | 2/2 |
| pending | 1/2 | 2/2 | |
| restedit | 2/2 | 2/2 | |
| strict | 2/2 | 2/2 | |

## Caveats

- Two runs per probe. A probe that passes twice can still fail on a third.
- The probes test the guard rules, not whether a light interview or a trigger-scoped standard interview finds the right rules. The interview eval does that and was not run here.
