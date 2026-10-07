---
name: ddd-setup
description: "Install the typed DDD kit into the current repository: pattern cards, domain model templates, the card and model check scripts, and the lint rules merged into the repository's own configs. Use once per repository before the other ddd skills."
disable-model-invocation: true
---

# Set up the typed DDD kit in this repository

The kit's files are in the `kit/` directory next to this file, and `install.sh` beside it copies them. The skills stay where they are installed; the cards and the model must live in the repository, because the team edits them and they are versioned with the code.

The copying is a script and the lint rules are yours to merge. Install no program during setup: no linter, no package, no `npm install`. A tool that is missing is reported, and the user decides. Change nothing outside what these steps name. Do not commit.

## 1. Choose how much of the kit

The kit has two halves: the model (what the software must do) and the pattern cards (how the code that does it is written). The model works for any language and any coding style, and comes with the strategic cards in `docs/ddd/strategic/`, which help decide how contexts relate. The pattern cards are one style, typed and functional in the manner of Scott Wlaschin, in `docs/ddd/cards/functional/`, with examples for Go and TypeScript. Ask which the repository wants, with your recommendation from what you see in it. Setup asks in two rounds, each question with your proposal: this choice and the language (step 2) first, then the conventions (step 3), who may approve models, and any ESLint question (step 4) together. Look at the repository before each round, so that every question in it can be answered without the others.

| Choice | When | What is installed |
|---|---|---|
| **Full** | Go or TypeScript, and no established style for domain code | the model, the cards, the examples and lint rules for the language: `install.sh` |
| **Cards without examples** | another language (Python, Java, Rust), and the team wants the kit's style as far as that language allows | the model and the cards' rules: `install.sh --lang none`. The code is written from the rules in the language's own idioms, best effort; use the project's own checks, with no supplied language-specific lint rules |
| **Model only** | the repository already has a way of writing domain code and wants to keep it (classic DDD with entity classes, say), or wants the model and nothing else | the model template, its checker and the strategic cards: `install.sh --model-only`. No pattern cards, no lint rules |

Recommend model only when the repository already has domain code in a consistent style of its own. Write the choice down in step 3.

With model only, skip step 4, and in step 3 describe the repository's own style in a line or two instead of choosing a layout. With cards without examples, also skip step 4 and record the project's own check commands. Installing cards is the style choice; later skills reuse it without asking again. An explicitly recorded model-only choice takes precedence over cards left from an earlier setup.

## 1b. Look

- Confirm this is a git repository, and note whether the working tree is clean. If it is not clean, tell the user, so they can tell your changes from theirs afterwards. If it is not a repository, offer `git init` and wait for the answer: `install.sh`, the model hash and `tools/ddd-status.sh` need git.
- Find the domain code: the packages or directories that hold business rules and no I/O. The domain lint rules in step 4 apply only there. If it is not obvious, ask, with the directory you would pick as the proposal. If there is no domain code yet, settle the layout in step 3 first and take the domain path from it: the `domain/` directory of layout (a), or each context's `domain/` directory in layout (b). The domain path never includes the use-case or infrastructure directories beside it, or the domain rules would forbid the I/O they exist to do.

## 2. Copy the files

Run `install.sh` from this skill's directory, in the repository root, with the flag for the choice made in step 1. It finds the languages (`go.mod`, `tsconfig.json`), and copies the cards, the directory of examples for each language found, the model templates, the tools, and the reference lint configs for those languages into `tools/lint/`. When the repository has no code yet, pass the language the user's request names (`--lang go` or `--lang ts`); if it names none, ask in the first round. A language without examples is `--lang none`.

It never overwrites. A file that exists with other content is kept and listed. For each one listed:

- A card: its **Corrections** section holds mistakes recorded by this team, and that is the most valuable part of the card. Show the diff above the Corrections heading and ask whether to take the kit's text; recommend taking it unless the team has edited the rules. Keep the repository's Corrections in every case. If the script reports the earlier card layout, or a card has `## Go` and `## TypeScript` sections, follow [UPGRADING.md](UPGRADING.md).
- A context map or context file: leave it. Never modify an existing model here.
- A tool or a reference config: show the diff and ask before replacing it.

The script installs no glossary. The glossary is `CONTEXT.md` at the repository root, shared with any other skill that reads one, and `ddd-modelling` creates it when the first term is settled. If `GLOSSARY.md`, `GLOSSARY-MAP.md` or `docs/domain/glossary.md` exists, follow [UPGRADING.md](UPGRADING.md).

Repeat what the script printed about programs that are not installed, and what each is needed for.

## 3. Conventions

The kit says what domain code looks like. It does not say where it lives or where its tests go, and a session that is not told will choose differently each time. Ask once, write the answers down, and no later prompt has to repeat them.

Look at what the repository already does and propose that. Where it does nothing yet, propose the first option of each:

- **Layout.** (a) Layers: `domain/` for the model's types and decisions, `services/` or `app/` for one use case per file, `infrastructure/` for repositories and adapters; the domain imports nothing from the others. (b) One directory per bounded context with the same three inside it. (c) The repository's own layout, described in a sentence.
- **Where tests go.** (a) Next to the code. (b) In a `__tests__` (or `__test__`) directory in each folder. (c) In a top-level `test/` directory.

Write the answers, and the choice from step 1 ("Code style: the kit's functional cards" or "Code style: the repository's own; the kit's cards are not used"), under a heading `## Domain code` in the repository's agent instructions (`CLAUDE.md`, or `AGENTS.md` if that is what it has; create `CLAUDE.md` if neither exists), in two or three lines, and `Approvers: <names>` with the names the user gives for who may approve models (ask for them; never take a name from git config or an account). Every later session reads that file. Where a rule can be linted (which layer may import which), add it in the next step, so a session that gets it wrong fails lint.

## 4. Lint rules

Merge into the repository's own configs. Add what is missing, and never remove or loosen what is there. The reference versions are in `tools/lint/`.

The reference configs have two kinds of rule. General rules apply to the whole repository. Domain rules apply only to the domain code found in step 1, and the reference configs mark where its paths go with a `DOMAIN-PATHS` comment and a placeholder path. Replace the placeholder with the real paths. A domain rule that points at a path with no code in it checks nothing, and nothing warns about that.

**Go (golangci-lint)**

- No config in the repository: copy `tools/lint/.golangci.yml` to the repository root and set the domain paths in the copy, in both places marked `DOMAIN-PATHS`: the `depguard` file globs, and the `path-except` expression that limits `forbidigo`. Leave `tools/lint/` as it is; `tools/check-cards.sh` checks the card examples with it.
- Existing config: check its format first. A top-level `version: "2"` means the settings key is `linters.settings`; without it, the key is `linters-settings`. Then:
  - general: enable `exhaustive`, `gochecksumtype` and `nolintlint`; set `default-signifies-exhaustive: false` for the first two, and `require-explanation` and `require-specific` for the third
  - domain: enable `depguard` with the reference config's `domain` list, next to any lists the repository already has; enable `forbidigo` with the reference patterns and the two exclusion rules that keep it to non-test files in the domain paths. If the repository already uses `forbidigo` everywhere, add the patterns and leave its scope alone, and say that they now apply everywhere.
  - if the repository also has a `node_modules` directory, exclude it from linting; some npm packages ship Go files
- If `golangci-lint` is not installed, write the config all the same and say that it has not been run. The rules take effect when the team's own lint step runs.

**TypeScript**

- `tsconfig.json`: add the compiler options from `tools/lint/tsconfig.json` that are missing: `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noImplicitReturns`, `noFallthroughCasesInSwitch`, `noPropertyAccessFromIndexSignature`. Do not change `target`, `module`, `moduleResolution` or `include`.
- ESLint flat config (`eslint.config.*`):
  - general: add the three rules from the first block of `tools/lint/eslint.config.mjs` with their options, and type-aware parsing (`projectService`) if the config does not have it, since `switch-exhaustiveness-check` needs type information
  - domain: add the second block, with its `files` set to the domain directories. Add the repository's own database, HTTP and framework packages to its `no-restricted-imports` patterns.
- Legacy `.eslintrc*`: say that the reference config is in flat format, and ask whether to add the same rules in the legacy format or leave ESLint alone. Recommend the legacy format, so the domain rules apply now and not after a migration.
- If `typescript-eslint` is not a dependency, the rules cannot be added: say so and ask whether to add it. Recommend yes for a repository that already uses ESLint, and leaving ESLint alone otherwise.

## 5. Verify, and report what the new rules find

1. Run the repository's own compile and lint commands, for the tools that are installed.
2. If `docs/domain/contexts/` already holds context files, run `tools/check-model.sh`. A model written before the kit had the matrix, examples and races sections will fail. Report what it says; do not fix it here. `ddd-modelling` brings a model up to date, and it needs the domain expert for the new sections.

Do not run `tools/check-cards.sh` here. The examples were compiled and linted before the kit was published, and the script downloads its own copies of the TypeScript tools. It is for the team, after they edit an example.

Stricter rules will usually flag existing code. That is expected. Do not fix those findings and do not suppress them. Report the count per rule, and give the user the choice, recommending the second:

- fix them now, as a separate change
- apply the general rules only to the domain code at first, and widen later
- keep the rules for the cards only (`tools/lint/`) and revert the changes to the repository's own configs

## 6. Summary

List every file added and every file changed, with one line on what changed in each. State what you could not do and why.

Then give the next step: the `ddd-modelling` skill. Say that asking "what's next?" at any point runs `ddd-next`, which reads `tools/ddd-status.sh` and gives the next step. For a repository with existing domain code, mention that the skill can also derive a draft model from that code, one aggregate at a time, if the user wants that.
