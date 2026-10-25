# Changelog

## Unreleased

- **`ddd-modelling` reads less to ask the first question.** Its SKILL.md was 28 617 characters, larger than 2 435 of the 2 592 skills in the plugin catalogue, and it opened by telling the agent to read five `lifecycle/` files as well: 37 252 characters before question 1, on a model whose first round may be three questions long. The structure for disclosing that material was already there and the skill pulled all of it eagerly anyway. Three blocks of reference now sit behind pointers that name their branches — what the timeline hides, with the examples, the matrix and the bounds they write down (`interview.md`), what each section of a context file holds (`sections.md`), and the shared glossary with its worked example (`glossary.md`) — and the four `lifecycle/` files that are not needed to choose a depth are read at the step that needs them: triggers at step 1, approval and the checker before step 6, the notes tail before anything is written to one. SKILL.md is 21 266 characters and the entry cost is 22 670, 40% less. No rule changed: every line of the old file is still there, in SKILL.md or in one of the three, and a test holds the pins — the Decisions row's split from ADRs, the core's definition, and that every relative link resolves.

## 0.9.0 (2026-10-25)

- **An answered question comes out of the model.** `ddd-modelling` already wrote each answer into the section it affects; nothing told it to remove the question, so a session kept the item as a record and `## Open questions` became an archive of the rounds. On a strict context of two models that reached 431 of 729 lines, 59% of the file, under a heading whose first word was "None" — a second copy of the model's own rows, beside the reports in `docs/domain/reviews/` that already held what each round asked. The item is now removed in the same step as the answer is written, in the template's own comment and in both places the skill says an answer is never asked for twice; `tools/check-model.sh` warns when items under Open questions record an answer. The reviewer's "no open questions at all in a model of any size" lens says the opposite finding out loud too, since a section built of answered items is not a model with open questions. The reviewer also stops reading the round number out of the model's prose, which was the one thing that rewarded keeping the rounds there, and asks instead.
- **A table cell states a rule; it does not derive one.** Nothing bounded a cell, and the Why column of a bound invites the whole argument for it: the same two models carried 92 cells over sixty words, the longest 506, a full derivation of one duration inside one cell of one row. `ddd-modelling` now says a cell is a sentence or two and that a derivation belongs in a `## Decisions` row the cell names, or a paragraph under the table, and `tools/check-model.sh` warns past sixty words, naming the section and the longest cell. The flow is what a person reads and the tables are what they look things up in; a cell that has to be read twice is doing neither job.
- **A review's fixes rewrite the row.** A patch that appended what a row used to say left "it was X until this round" in three rows of a model whose report, which is committed, was the place for that sentence. `ddd-model-review` now says a fixed row states the rule as it now stands.

### Upgrading

- Update the plugin, or copy `skills/` again. Copy `skills/ddd-setup/kit/tools/check_model.py` over your repository's `tools/` to get the two warnings; nothing else in `docs/`, `tools/` or `CLAUDE.md` changes, and no approval, review or test is affected. Both warnings leave the exit status alone, so a model that reports them keeps passing: they tell you where the material belongs, and you move it at the next change to that model. A `## Open questions` section that is already an archive is trimmed by hand once — the answers are in the rows they affect, so what comes out is the duplicate, and the rounds stay in `docs/domain/reviews/`.

## 0.8.0 (2026-10-23)

- **A review report is a summary first.** `ddd-model-review` now opens the report with the verdict, the blockers, the questions and one line of counts, and puts the rest below it: the assumptions and notes as one line each, then the patch, then `tools/check-model.sh`'s output last, as evidence rather than the first thing to scroll past. Before, the order led with the checker and gave every finding a paragraph with its entry quoted, assumptions and notes included — on a strict context that reported thirty-odd of them, the approval decision was buried in a report nobody reads to the end, and the fix the user asked for was to type "make a summary instead of a wall of text" into the review prompt. The detail is still in the file for whoever wants a line of it; the terminal keeps items 1 to 4. The round number is pinned down with it: `<n>` is one more than the highest report in `docs/domain/reviews/`, which is one reason they are committed.

### Upgrading

- Update the plugin, or copy `skills/` again. Nothing in your repository's `docs/`, `tools/` or `CLAUDE.md` changes, no tool changes, and a report written in the old order still applies: the change is the order the reviewer writes the next one in, so a round already in `docs/domain/reviews/` needs nothing. If your reports were never committed, the reviewer can no longer infer `<n>` from an empty directory — name the round in the prompt once, or commit the ones you have.

## 0.7.0 (2026-10-22)

- **A review round is handed over as files, not pasted.** `ddd-model-review` writes the report to `docs/domain/reviews/<context>-r<n>.md` and the fixes that need no domain fact to `<context>-r<n>.patch`, a unified diff it has checked with `git apply --check`; `ddd-modelling` applies that patch instead of reading the context file again to rebuild strings the diff already carried. Answers the user gives in the review session are folded into the patch, so the round comes back as one path. On a strict context of 98 KB the old loop cost roughly 12k tokens for the paste and another 35k for the modelling session to find the exact strings to edit; the patch makes the second of those nearly free. `REFERENCE.md` also says to commit the model after each round and to give the next round a diff, which the review skill already reads as "only the changed rows".

### Upgrading

- Update the plugin, or copy `skills/` again. Nothing in your repository's `docs/`, `tools/` or `CLAUDE.md` changes, and no tool changes. The reviewer writes `docs/domain/reviews/` on the first round that reports there; commit the reports if you want a round's questions and answers kept, and leave the patches out, since each is applied once.

## 0.6.0 (2026-10-20)

- **New skill: `ddd-system-design`.** After approval, it goes through one flow step by step and checks it against the common system-design patterns: caching, read replicas, indexing, batching, sharding, async writes, real-time updates, queues, worker pools, workflow engines, retries, idempotency, circuit breakers, self-healing and CQRS. A pattern is only asked about when the model or the project gives a signal for it. Each is recorded as applies, not needed or deferred, with the reason, in `docs/system-design/<context>.md`. Answers that would change what the business sees are sent back to `ddd-modelling`; the skill never edits the model.
- **`ddd-next` includes the system-design check.** After approval and before any code, it sends you to `/ddd-system-design` once per context, and again when the model is approved again. Questions the check marks "blocked by the model" are sent to `ddd-modelling`, with the other model rows. `tools/ddd-status.sh` reports the record: `system design: none`, the commit it was checked at, whether the model was approved again since, and how many rows are blocked by the model. Amendments rows alone do not count as a change.
- **Questions are asked when the work raises them.** At standard depth, the interview goes deep only on the commands the work in front of it needs, and asks the harder questions (an outcome something outside can reverse, two requests at once, one decision with several consequences, what happens if nothing happens, who reacts, a limit) when a trigger in the new `lifecycle/triggers.md` applies. Who may issue a command and what makes a caller or fact trusted are still always asked. A question that surfaces later as a `## Pending` row gets one round of its own and does not reopen the interview. Before, standard depth swept every kind of question for every command, in about three rounds. Strict depth still asks everything.
- **At standard depth, approval is asked only when the core is new or changes.** `lifecycle/approval.md` already allowed this, but the skills read as if every detail stopped the work: modelling ended every round with a stop, and called its whole output a hard stop. Now a round stops only when it has questions, the rest is written `(assumed)` and listed once, and the approval request says that later work will not stop for the rest. The core that does need approval is unchanged and includes what makes callers and outside facts trusted. Strict depth still approves every change.
- **`tools/check-range.sh <base>` runs the mechanical part of a review.** It fails when the model above the notes tail changed in the range while the Status line stayed the same; that check was written out by hand in three reviewer skills. It also lists, to judge: identifiers in new code containing a word under `_Avoid_`, suppressions, changed lint configs with their removed lines, glossary or context-map changes, and example rows no test names. `ddd-review-all` runs it once and passes the output to each reviewer, the reviewers use it instead of finding these by reading, and `ddd-implementation` runs it before reporting done. On the seeded fixture it reports D1, D2, D12 and D16; in the review eval a seed it reports and the reviewer leaves out is scored **check**, not missed. Avoided words are listed, not failed: the fixture showed that `row` and `line` are also ordinary programming words.

### Upgrading

- Copy `tools/ddd_status.py`, `tools/check-range.sh` and `tools/check_range.py` from the kit, or run `/ddd-setup` again. Without the new `ddd_status.py`, `ddd-next` never sees a system-design record and suggests the check every time.

## 0.5.0 (2026-10-19)

- **`ddd-implementation` names the `## Pending` columns.** One run wrote its own columns, which tools reading the table could not use.
- **`secure-by-design-review` compares code with the approved model.** When the range changes primitive rules, bounds or other entries above the notes tail without a new approval, it compares against the version before the change and reports the edit as a blocker. Before, it took the edited rule as the one in force.
- **`ddd-review` no longer compiles, lints or tests the change.** That is `ddd-implementation`'s and CI's job. The review still reads the diff for suppressions and loosened lint configs, which CI cannot see, and its break-it attempts still compile and run tests. The section is now called "Checks switched off". In the review eval, a seed the reviewer leaves to the linters is scored **lint**, not missed.

### Upgrading

- Update the plugin, or copy `skills/` again. Nothing in your repository's `docs/`, `tools/` or `CLAUDE.md` changes. If your CI doesn't already compile, lint and test domain code, add it, since `ddd-review` no longer does.

## 0.4.0 (2026-10-19)

The tag `v0.3.0` was pushed without release notes or a version bump. Its one change is the first entry below, so 0.4.0 lists everything since 0.2.0.

- **`ddd-modelling` asks who owns each part before modelling it.** "Is any of this decided by another model, team or system?" A part with its own model becomes another context on the context map, and only what crosses the boundary is modelled. Before, the interview modelled everything it heard, including values another model owns.
- **TypeScript brands on object types use an unexported symbol.** Cards 02 (`Money`) and 14 (`Actor`) branded an object type with `readonly __brand: "..."`, which anyone can type into an object literal: `{ kind: "customer", id, __brand: "Actor" }` compiled and forged an actor. They now use a `unique symbol` the module does not export. `ts/README.md` says when a string brand is safe (on a `string` or `number`) and when it is not. The clean TypeScript fixture had copied the pattern for `Actor` and `CustomerEmail`; it is fixed, with a compile-time test for each.
- **Model changes go through `ddd-modelling`, by an instruction in `CLAUDE.md`.** A request that names no skill ("raise the limit to 2000", "I approve the model") did not load `ddd-modelling`, and the session edited the model directly: in the guard probes it changed the body of an approved model with no Amendments row, and approved a strict model that had no review. `ddd-setup` now writes a line under `## Domain code` sending every change to `docs/domain/` through the skill. With it, the three failing probes went from 1 of 6 to 6 of 6.
- **`tools/check-model.sh` no longer reads types out of field names.** In a command's Input column, `toolId: ToolId` reported a type named `Id`, and `missingPartsCharge: Kronor` one named `PartsCharge`, each as undefined. The check now matches a type name only at the start of a word.

### Upgrading

- Copy `tools/check_model.py` from the kit, or run `/ddd-setup` again.
- Add this line under `## Domain code` in `CLAUDE.md` or `AGENTS.md`: "Changes to `docs/domain/`, including approving a model, go through the `ddd-modelling` skill, even a one-line edit."
- In TypeScript domain code that followed cards 02 or 14, replace each `readonly __brand: "X"` on an object type with `readonly [xBrand]: true`, where `const xBrand: unique symbol = Symbol("X")` is not exported. Brands on `string` and `number` stay as they are.

## 0.2.0 (2026-10-09)

- **Approval is a plain line.** Say that you approve the model; the agent writes `Status: approved <date>` and carries on. `tools/stamp-model.sh`, `tools/model-hash.sh`, the hashes on the Status line and the `Approvers:` list are gone. `tools/check-model.sh` no longer reports "edited after approval": `ddd-review` reads the reviewed range in git for a model that changed without a new approval. Tickets carry the commit of the context file in place of its hash.
- **Only `ddd-implementation` chooses a code style.** The other skills no longer branch on whether the pattern cards are installed. What a review checks in card-style code moved out of `ddd-review` into the cards' own `docs/ddd/cards/functional/REVIEW.md`, which the reviewers apply when the repository has it. `lifecycle/code-style.md` is gone; its rule is in `ddd-implementation`.
- **`ddd-modelling` describes standard depth.** What strict depth does differently moved to `skills/ddd-modelling/STRICT.md`, read only for a strict context or strict commands. You ask for it the same way: "at strict depth".

### Upgrading

- Run `/ddd-setup` again. It lists `tools/check_model.py` and `tools/ddd_status.py` as differing: take the kit's, then delete `tools/stamp-model.sh` and `tools/model-hash.sh`. Existing Status lines still read as approved. Remove the `Approvers:` line from `CLAUDE.md` or `AGENTS.md`.
- With cards installed, the same run adds `docs/ddd/cards/functional/REVIEW.md`. Without it, `ddd-review` no longer checks the cards' style.

## 0.1.0 (2026-10-08)

The first published version.

- Ten skills: `ddd-next`, `ddd-setup`, `ddd-modelling`, `ddd-model-review`, `ddd-to-tickets`, `ddd-implementation`, `ddd-review`, `secure-by-design-review`, `task-review` and `ddd-review-all`.
- Twenty functional pattern cards with Go and TypeScript examples, ten strategic cards quoted from Evans and the DDD Crew, a context template, and tools: `check-model.sh`, `stamp-model.sh`, `ddd-status.sh`, `check-cards.sh` and lint configs for golangci-lint and ESLint.
- Works with Matt Pocock's skills 1.3: the glossary is `GLOSSARY.md`.
- Installs as a Claude Code plugin (`/plugin marketplace add urostripunovic/ddd-skill`), with `npx skills add urostripunovic/ddd-skill`, or by copying `skills/`.

### Upgrading from an unpublished version

- **The glossary is `GLOSSARY.md`.** A repository with `CONTEXT.md` or `CONTEXT-MAP.md` fails `tools/check-model.sh` until it is renamed: `git mv CONTEXT.md GLOSSARY.md`. Approvals stand; the hash does not cover the glossary.
- **Sum-type switches can live in any package.** Cards 03 and 06 no longer ask for every switch in the declaring package; `gochecksumtype` checks them all.
- **Unknown fields** are rejected in requests from outside the system, and ignored in messages from other contexts.
- Copy the updated `tools/` and cards from `skills/ddd-setup/kit/` into your repository, or run `/ddd-setup` again: it never overwrites a file, and lists each one that differs from the kit.
