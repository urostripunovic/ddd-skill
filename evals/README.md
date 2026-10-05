# Evals

Repeatable tests of the skills, each with an answer key. They answer one question per skill: does it do what it claims, and did the last edit to it help or hurt?

| Eval | Tests | Planted | Counts as caught |
|---|---|---|---|
| Review, seeded fixture | `ddd-review`, `secure-by-design-review` | 17 and 16 violations in code, plus 2 controls | the report names the problem at the place |
| Review, clean fixture | the same two | nothing: the code follows the model | every blocker or should-fix is a candidate false positive |
| Baseline | no skill at all | the seeded fixture | as above; the gap to a skill's score is what the skill adds |
| Implementation | `ddd-implementation` | nothing: the approved fixture model, and nobody to ask | builds, lints and tests pass with the model untouched; then by hand: gaps it reported, decisions it made anyway, examples covered |
| Interview | `ddd-modelling` | 10 rules a scripted domain expert gives only when asked | the rule is in the model that the interview wrote |

## Contents

| Path | Purpose |
|---|---|
| `fixture/model/` | An Ordering model and its glossary, approved in the base commit of both fixture repositories |
| `fixture/go/`, `fixture/ts/` | An implementation with seeded violations |
| `fixture-clean/go/`, `fixture-clean/ts/` | A correct implementation in each language, with tests |
| `make-fixture-repo.sh` | Builds a git repository with a base and a head commit and prints both hashes; `model` builds the base only |
| `expected-findings.md` | The seeds per reviewer, the controls, and how to score the clean fixture |
| `baseline-prompt.md` | The prompt for a run with no skill |
| `implementation/run.sh`, `score.sh` | Runs `ddd-implementation` on the model alone, then the checks a script can decide |
| `implementation/scoring.md` | What to score by hand, and where each number comes from |
| `interview/expert-brief.md` | The scripted domain expert: what it says freely, and ten rules it gives only when asked |
| `interview/answer-key.md` | The ten rules and how to score a model against them |
| `interview/run.sh` | Runs the interview between two Claude Code sessions |
| `results/` | One file per run |

## Run the review evals

1. `evals/make-fixture-repo.sh /tmp/ddd-fixture seeded`, and note the base and head hashes. For the seeded fixture, run `npm install` in that repository.
2. Run `ddd-review-all` there with the base hash, or run `ddd-review` and `secure-by-design-review` each in a fresh session.
3. Score each report against `expected-findings.md`.
4. Repeat with `evals/make-fixture-repo.sh /tmp/ddd-clean clean` for Go, and with `clean-ts` for TypeScript. The TypeScript repository needs `npm install`, and Node 22.18 or later: its tests run from the `.ts` files with no build step.
5. Run the baseline: the prompt in `baseline-prompt.md`, in a fresh session with none of the kit's skills, on the seeded repository.
6. Record the result in `results/`.

## Run the implementation eval

```
evals/implementation/run.sh /tmp/ddd-impl
```

It needs the Claude Code CLI, signed in, with `go` and `golangci-lint`. It builds a repository with the approved Ordering model and no code, and has one session implement the Order aggregate in Go with nobody to ask. `score.sh` then prints what a script can decide. Score the rest with `implementation/scoring.md`: it uses a `ddd-review` run on the printed base and head.

## Run the interview eval

```
evals/interview/run.sh /tmp/ddd-interview
```

It needs the Claude Code CLI, signed in. It creates a repository with the kit and the skills, starts one session that runs `ddd-modelling` and one that plays the expert, and passes their messages back and forth until the expert ends the interview. Then score `/tmp/ddd-interview/repo` against `interview/answer-key.md`: rules found, facts invented, rounds, and whether `tools/check-model.sh` passes.

Record in the result whether a `grilling` skill was installed on the machine, because `ddd-modelling` uses it when it is there.

To see whether a change to the interview helped: run before and after, three times each, and compare.

## Limits

- The seeds are obvious ones. Passing shows the reviewers follow their checklists, not that they find subtle problems. The "findings beyond the seeds" in `results/` are a source of subtler seeds.
- The clean fixtures were written by the same model family that will review them. A reviewer may find real problems in one; fix the fixture when it does.
- One expert and ten rules is one domain. An interview tuned to this brief has learned the brief.
- Results vary between runs. One run is one data point.
- Scoring is by hand.
