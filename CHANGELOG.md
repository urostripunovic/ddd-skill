# Changelog

## Unreleased

- **Light depth, between none and standard.** A light context is a Requests table (who or what may make each request, never assumed) and a numbered Examples table (state, request, facts, the test that pins it), written alongside the code with no approval step. It comes from a game prototype built this way, where the rules stayed modular with no approval rounds and the safety came from tests, lint and types. The interview still comes first, in one short round; later questions are asked when a change raises them, and each answer is a new row with its test. It moves to standard, or strict for the part that needs it, when a request touches money, credentials, authorisation, personal data or anything hard to undo, another context reacts to its facts, it gains a second lifecycle, it outgrows about a dozen rows, or the user asks; the rows keep their numbers. `tools/check-model.sh` checks a light context's two tables, `tools/ddd-status.sh` reads its rows, `ddd-to-tickets` cuts one ticket per request, and `ddd-review-all` gives it the standard review. Strict depth and strict scopes are unchanged.
- **Questions are asked when the work raises them.** At light and standard depth, the interview goes deep only on the commands the work in front of it needs, and asks the harder questions (an outcome something outside can reverse, two requests at once, one decision with several consequences, what happens if nothing happens, who reacts, a limit) when a trigger in the new `lifecycle/triggers.md` applies. Who may issue a command and what makes a caller or fact trusted are still always asked. A question that surfaces later, as a `## Pending` row or a light trigger, gets one round of its own and does not reopen the interview. Before, standard depth swept every kind of question for every command, in about three rounds. Strict depth still asks everything.
- **`ddd-implementation` names the `## Pending` columns.** One run wrote its own columns, which tools reading the table could not use.
- **`secure-by-design-review` compares code with the approved model.** When the range changes primitive rules, bounds or other entries above the notes tail without a new approval, it compares against the version before the change and reports the edit as a blocker. Before, it took the edited rule as the one in force.
- **`ddd-review` no longer compiles, lints or tests the change.** That is `ddd-implementation`'s and CI's job. The review still reads the diff for suppressions and loosened lint configs, which CI cannot see, and its break-it attempts still compile and run tests. The section is now called "Checks switched off". In the review eval, a seed the reviewer leaves to the linters is scored **lint**, not missed.

### Upgrading

- Copy `tools/check_model.py`, `tools/ddd_status.py` and `docs/domain/contexts/_light-template.md` from the kit, or run `/ddd-setup` again.
- Extend the line under `## Domain code` in `CLAUDE.md` or `AGENTS.md` with: "The one exception: `ddd-implementation` adds the Requests and Examples rows of a light context (`Depth: light`) alongside its code." Without it, a session that reads the line sends every light row through `ddd-modelling`.

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
