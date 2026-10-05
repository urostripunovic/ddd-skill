# Scoring the implementation eval

The eval tests one claim: an approved model leaves the implementer no business decision. `run.sh` gives `ddd-implementation` the fixture's Ordering model and nobody to ask.

## 1. What the script decides

`score.sh` prints these. Any FAIL is a failed run.

- the work is committed, and the model, the glossary and the lint config are as they were
- `tools/check-model.sh`, `go build`, `go vet`, `go test` and `golangci-lint` pass
- the number of `//nolint` comments: read each one

## 2. Model gaps

Read the end of `summary.md`. For each item under MODEL GAPS, decide which it is:

- **real gap**: the model does not say. Fix the fixture model, and note it in the result. This is the eval working.
- **not a gap**: the model does say, and the implementer missed it. Counts against the skill.

Then look for the opposite: a decision made without saying so. `ddd-review`'s second tracing table (code to model) lists every exported name that the model does not have; each is a candidate.

## 3. Coverage

Run `ddd-review` on `<base>...<head>` in a fresh session, and take from its tracing file:

| Number | From |
|---|---|
| Model elements ok, of the total | the first tracing table |
| Examples with a test that uses the row's values, of 10 | the same table, kind "example" |
| Races with a workflow test | the same table, kind "race" |
| Invariants whose removal made a test fail | the break-it table, "remove a rule" rows |
| Names in code that are not in the model | the second tracing table |

## Reading the result

A good run has no FAIL, no gap that the model answers, no undeclared decision, every example covered, and every removed rule caught by a test. Compare runs of the same skill version before comparing versions: one run is one data point.

## Limits

- Go only: the fixture has no TypeScript configuration for a model-only repository.
- The Ordering model is small and was written with the kit's own template, so it is the easy case.
- The reviewer that fills in section 3 is one of the kit's own skills. A reviewer that misses something scores the implementation too high.
