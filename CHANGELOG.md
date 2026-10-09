# Changelog

## Unreleased

- **Approval is a plain line.** Say that you approve the model; the agent writes `Status: approved <date>` and carries on. `tools/stamp-model.sh`, `tools/model-hash.sh`, the hashes on the Status line and the `Approvers:` list are gone. `tools/check-model.sh` no longer reports "edited after approval": `ddd-review` reads the reviewed range in git for a model that changed without a new approval. Tickets carry the commit of the context file in place of its hash.

### Upgrading

- Run `/ddd-setup` again. It lists `tools/check_model.py` and `tools/ddd_status.py` as differing: take the kit's, then delete `tools/stamp-model.sh` and `tools/model-hash.sh`. Existing Status lines still read as approved. Remove the `Approvers:` line from `CLAUDE.md` or `AGENTS.md`.

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
